/**
 * ChatInput.jsx — Chat message input bar
 * 
 * Features: text input, mic button (placeholder), send button.
 * Disclaimer text below the input.
 * 
 * Props:
 *   - value: Current input value
 *   - onChange: Input change handler
 *   - onSend: Send button/enter handler
 */

import { Mic, Send, PlusCircle } from 'lucide-react';

export default function ChatInput({ value, onChange, onSend }) {
  /* Send on Enter key (not Shift+Enter for multiline) */
  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      onSend();
    }
  };

  return (
    <div className="chat-input-wrapper">
      <div className="chat-input">
        {/* Add attachment button */}
        <button className="chat-input__action" aria-label="Add attachment">
          <PlusCircle size={20} />
        </button>

        {/* Text input */}
        <input
          type="text"
          className="chat-input__field"
          placeholder="Ask Mealimizer about your diet..."
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onKeyDown={handleKeyDown}
        />

        {/* Mic button */}
        <button className="chat-input__action" aria-label="Voice input">
          <Mic size={20} />
        </button>

        {/* Send button */}
        <button
          className="chat-input__send"
          onClick={onSend}
          aria-label="Send message"
          disabled={!value.trim()}
        >
          <Send size={18} />
        </button>
      </div>

      {/* Disclaimer */}
      <p className="chat-input__disclaimer">
        Mealimizer AI can make mistakes. Verify nutritional data.
      </p>
    </div>
  );
}
