/**
 * Chat.jsx — AI nutrition assistant chat interface
 * 
 * Features:
 * - "AI Assistant Active" status indicator
 * - Message history with AI/user bubbles (using ChatMessage component)
 * - Auto-scroll to newest message
 * - Chat input with send on Enter (using ChatInput component)
 * - Mock conversation data for demo
 * 
 * Messages are stored in local state. In production, these would
 * come from an API/WebSocket connection.
 */

import { useState, useRef, useEffect } from 'react';
import ChatMessage from '../components/ChatMessage';
import ChatInput from '../components/ChatInput';
import './Chat.css';

export default function Chat() {
  /* Parse user for avatar in chat bubbles */
  const user = (() => {
    try {
      return JSON.parse(localStorage.getItem('user')) || null;
    } catch {
      return null;
    }
  })();

  /* Start with a real greeting */
  const [messages, setMessages] = useState([
    {
      type: 'ai',
      text: `Hello! I'm your Mealimizer AI. Tell me what you're craving, what ingredients you have, or what your macros goals are, and I'll find the perfect recipe for you.`
    }
  ]);

  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  /**
   * Auto-scroll to the bottom whenever messages change.
   * Uses smooth scrolling for a polished feel.
   */
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  /**
   * Handle sending a new message.
   * Calls the backend recommendation API with the user's query.
   */
  const handleSend = async (text, image) => {
    const msg = (text || '').trim();
    if (!msg && !image) return;
    if (loading) return;

    /* Add user message immediately (with optional image) */
    setMessages(prev => [...prev, { type: 'user', text: msg, image: image || null }]);
    setInput('');
    setLoading(true);

    try {
      const token = localStorage.getItem('accessToken');
      const response = await fetch('http://localhost:8000/recipes/recommend', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token && { 'Authorization': `Bearer ${token}` })
        },
        body: JSON.stringify({
          query: msg || 'Analyze this food image'
        }) // Using query mapped to natural language
      });

      if (!response.ok) {
        if (response.status === 401) {
          throw new Error("Invalid token");
        }
        const error = new Error("Server error");
        error.response = response;
        throw error;
      }

      const responseData = await response.json();
      
      if (!responseData || !responseData.data || responseData.data.length === 0) {
        throw new Error("No recipes found");
      }
      
      const meta = responseData.meta;
      const data = responseData.data;

      if (meta?.reason === "no_intent") {
        setMessages(prev => [...prev, {
          type: 'ai',
          text: "Tell me what you're looking for — ingredient, goal, or diet — and I'll suggest something relevant."
        }]);
        setLoading(false);
        return;
      }
      
      const topRecipe = data[0];
      const recipeName = topRecipe?.recipe?.name;
      
      if (!recipeName) {
        throw new Error("No recipes found");
      }
      
      const ingredientAlignment = topRecipe?.explanation?.ingredient_alignment ?? 0;
      const proteinAlignment = topRecipe?.explanation?.protein_alignment ?? 0;
      const calorieAlignment = topRecipe?.explanation?.calorie_alignment ?? 0;
      const fallbackMode = topRecipe?.explanation?.fallback_mode ?? false;
      
      let reason = "it aligns with your preferences";
      
      if (fallbackMode || meta?.reason === "fallback" || meta?.reason === "low_confidence") {
        reason = "it's a reasonable match based on available options";
      } else if (ingredientAlignment > 0 && calorieAlignment > 0.8) {
        reason = "it matches your ingredient and calorie requirement";
      } else if (ingredientAlignment > 0) {
        reason = "it matches your requested ingredient";
      } else if (proteinAlignment > 0.8) {
        reason = "it fits your protein requirement";
      } else if (calorieAlignment > 0.8) {
        reason = "it meets your calorie requirement";
      }

      const intros = ["I recommend", "I suggest", "You might like", "How about"];
      const randomIntro = intros[Math.floor(Math.random() * intros.length)];
      const aiResponseText = `${randomIntro} **${recipeName}** because ${reason}.`;

      setMessages(prev => [...prev, {
        type: 'ai',
        text: aiResponseText
      }]);
    } catch (error) {
      console.error(error);
      
      let errorMsg;
      if (error.message === "Failed to fetch") {
        errorMsg = "Backend unreachable";
      } else if (error.message === "No recipes found") {
        errorMsg = "I couldn't find any recipes matching your exact request. Could you tell me more about what you're looking for?";
      } else if (error.message === "Invalid token") {
        errorMsg = "Your session has expired or token is invalid. Please log in again.";
      } else if (error.response) {
        errorMsg = "Server error";
      } else {
        errorMsg = "Unexpected failure";
      }

      setMessages(prev => [...prev, {
        type: 'ai',
        text: errorMsg
      }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="chat">
      {/* Status bar */}
      <div className="chat__status">
        <span className="chat__status-dot">●</span>
        <span className="chat__status-text label-ui">AI Assistant Active</span>
      </div>

      {/* Messages container */}
      <div className="chat__messages">
        {messages.map((msg, i) => (
          <ChatMessage
            key={i}
            type={msg.type}
            text={msg.text}
            image={msg.image}
            imageCaption={msg.imageCaption}
          />
        ))}
        {/* Invisible element to scroll to */}
        <div ref={messagesEndRef} />
      </div>

      {/* Input bar */}
      <ChatInput
        value={input}
        onChange={setInput}
        onSend={handleSend}
      />
    </div>
  );
}