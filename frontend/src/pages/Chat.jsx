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
        const error = new Error("Server error");
        error.response = response;
        throw error;
      }

      const data = await response.json();
      
      let aiResponseText = '';
      if (Array.isArray(data) && data.length > 0) {
        const topRecipe = data[0];
        
        // Defensive consumption with nullish coalescing
        const recipeName = topRecipe?.recipe?.name ?? 'a customized meal';
        const proteinAlignment = topRecipe?.explanation?.protein_alignment ?? 0;
        const calorieAlignment = topRecipe?.explanation?.calorie_alignment ?? 0;

        aiResponseText = `I recommend the **${recipeName}**. It scored highly based on your profile! \n\n*Protein alignment: ${Math.round(proteinAlignment * 100)}%*\n*Calorie alignment: ${Math.round(calorieAlignment * 100)}%*`;
      } else {
        aiResponseText = "I couldn't find a perfect match for that request right now. Could you tell me more about what you're looking for?";
      }

      setMessages(prev => [...prev, {
        type: 'ai',
        text: aiResponseText
      }]);
    } catch (error) {
      console.error(error);
      
      // Strict error classification
      let errorMsg;
      if (error.message === "Failed to fetch") {
        errorMsg = "Backend unreachable";
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