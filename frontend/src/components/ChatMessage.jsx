/**
 * ChatMessage.jsx — Single chat message bubble
 * 
 * Renders either an AI or user message with appropriate styling.
 * AI messages: left-aligned with sparkle icon, dark background.
 * User messages: right-aligned with user avatar, brand-colored background.
 * 
 * Props:
 *   - type: 'ai' | 'user'
 *   - text: Message content string
 *   - image: Optional image URL to display in the message
 *   - imageCaption: Caption for the image
 */

import { Sparkles } from 'lucide-react';
import default_user from '../assets/default-user.jpg';

export default function ChatMessage({ type, text, image, imageCaption }) {
  const isAI = type === 'ai';

  /* Get user avatar from localStorage for user messages */
  const userAvatar = (() => {
    const saved = localStorage.getItem('profileImage');
    return saved && saved !== 'null' ? saved : default_user;
  })();

  return (
    <div className={`chat-message chat-message--${type}`}>
      {/* AI sparkle icon or spacer for alignment */}
      {isAI && (
        <div className="chat-message__icon">
          <Sparkles size={16} />
        </div>
      )}

      {/* Message bubble */}
      <div className="chat-message__bubble">
        <p className="chat-message__text">{text}</p>

        {/* Optional image (e.g., recipe recommendation) */}
        {image && (
          <div className="chat-message__image-wrap">
            <img src={image} alt={imageCaption || 'Chat image'} className="chat-message__image" />
            {imageCaption && <span className="chat-message__caption">{imageCaption}</span>}
          </div>
        )}
      </div>

      {/* User avatar on user messages */}
      {!isAI && (
        <img
          src={userAvatar}
          alt="You"
          className="chat-message__avatar"
          onError={(e) => { e.target.src = default_user; }}
        />
      )}
    </div>
  );
}
