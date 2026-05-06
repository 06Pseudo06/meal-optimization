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
  const [loadingText, setLoadingText] = useState('Thinking...');
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
    setLoadingText('Thinking...');

    // Set 3-second delay hint
    const delayTimer = setTimeout(() => {
      setLoadingText('Still processing...');
    }, 3000);

    if (msg.toLowerCase() === 'reset') {
      setMessages([{
        type: 'ai',
        text: `Memory cleared! What would you like to eat?`
      }]);
    }

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
      const meta = responseData?.meta;
      const data = responseData?.data;

      if (responseData.message && (!data || data.length === 0)) {
        setMessages(prev => [...prev, {
          type: 'ai',
          text: responseData.message
        }]);
        setLoading(false);
        return;
      }

      if (!data || data.length === 0) {
        throw new Error("No recipes found");
      }

      const topRecipe = data?.[0];
      const recipeName = topRecipe?.recipe?.name;

      if (!recipeName) {
        throw new Error("No recipes found");
      }

      const fallbackMode = topRecipe?.explanation?.fallback_mode ?? false;
      const explanationText = topRecipe?.explanation_text || "This recipe was selected because it's a reasonable match based on available options.";
      const conf = topRecipe?.confidence ?? (meta?.confidence || 0.5);

      let confidenceLabel = "💡 Alternative Pick";
      if (!fallbackMode && conf >= 0.35) {
        if (conf >= 0.80) {
          confidenceLabel = "✅ Recommended";
        } else if (conf >= 0.55) {
          confidenceLabel = "✨ Great Fit";
        } else {
          confidenceLabel = "💡 Alternative Pick";
        }
      }

      // Create recommendation payload
      const recommendationData = {
        name: recipeName,
        calories: topRecipe.recipe.calories,
        protein: topRecipe.recipe.protein,
        carbs: topRecipe.recipe.carbs || Math.round(topRecipe.recipe.calories * 0.4 / 4),
        fats: topRecipe.recipe.fats || Math.round(topRecipe.recipe.calories * 0.3 / 9), 
        confidenceLabel,
        explanationText,
        tags: topRecipe.recipe.tags || [],
        dietType: topRecipe.recipe.diet_type,
        isQuick: topRecipe.recipe.is_quick,
        isGymFriendly: topRecipe.recipe.is_gym_friendly
      };

      setMessages(prev => [...prev, {
        type: 'ai',
        text: "Here is a great option for you based on your preferences:",
        recommendationData: recommendationData
      }]);
    } catch (error) {
      console.error(error);

      let errorMsg;
      if (error.message === "Failed to fetch") {
        errorMsg = "The recommendation service is temporarily unavailable.";
      } else if (error.message === "No recipes found") {
        errorMsg = "I couldn't understand that preference. Please try a more specific meal request.";
      } else if (error.message === "Invalid token") {
        errorMsg = "Your session has expired or token is invalid. Please log in again.";
      } else if (error.response) {
        errorMsg = "The recommendation service is temporarily unavailable. Please try again later.";
      } else {
        errorMsg = "I couldn't process that. Please try a more specific meal request.";
      }

      setMessages(prev => [...prev, {
        type: 'ai',
        text: `❌ **System Alert**\n${errorMsg}`
      }]);
    } finally {
      clearTimeout(delayTimer);
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
            recommendationData={msg.recommendationData}
          />
        ))}
        {loading && (
          <ChatMessage type="ai" text={loadingText} />
        )}
        {/* Invisible element to scroll to */}
        <div ref={messagesEndRef} />
      </div>

      {/* Input bar */}
      <ChatInput
        value={input}
        onChange={setInput}
        onSend={handleSend}
        disabled={loading}
      />
    </div>
  );
}
