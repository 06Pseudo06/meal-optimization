/**
 * ChatInput.jsx — Chat message input bar
 * 
 * Features: text input, mic button, send button, image attachment (camera + device upload).
 * Disclaimer text below the input.
 * 
 * Props:
 *   - value: Current input value
 *   - onChange: Input change handler
 *   - onSend: Send button/enter handler — called with (text, imageDataUrl | null)
 */

import { useState, useRef, useEffect } from 'react';
import { Mic, Send, PlusCircle, X, Camera } from 'lucide-react';

export default function ChatInput({ value, onChange, onSend }) {
  const [showUploadMenu, setShowUploadMenu] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [showCamera, setShowCamera] = useState(false);
  const [attachedImage, setAttachedImage] = useState(null); // base64 data URL

  const uploadMenuRef = useRef(null);
  const valueRef = useRef(value);
  const recognitionRef = useRef(null);
  const videoRef = useRef(null);
  const streamRef = useRef(null);
  const canvasRef = useRef(null);
  const deviceInputRef = useRef(null);

  useEffect(() => {
    valueRef.current = value;
  }, [value]);

  /* Close upload menu on outside click */
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (uploadMenuRef.current && !uploadMenuRef.current.contains(event.target)) {
        setShowUploadMenu(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  /* Send on Enter key (not Shift+Enter for multiline) */
  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendWithImage();
    }
  };

  /* Wrap onSend to include attachedImage then clear it */
  const handleSendWithImage = () => {
    const text = value.trim();
    if (!text && !attachedImage) return;
    onSend(text, attachedImage);
    setAttachedImage(null);
  };

  /* ─── Voice input (10-second continuous) ─── */
  const startListening = () => {
    if (isListening) return;

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) return;

    const recognition = new SpeechRecognition();
    recognitionRef.current = recognition;
    recognition.lang = 'en-US';
    recognition.continuous = true;
    recognition.interimResults = false;

    recognition.onstart = () => {
      setIsListening(true);
      setTimeout(() => {
        if (recognitionRef.current) {
          recognitionRef.current.stop();
        }
        setIsListening(false);
      }, 10000);
    };

    recognition.onresult = (event) => {
      let newTranscript = '';
      for (let i = event.resultIndex; i < event.results.length; i++) {
        newTranscript += event.results[i][0].transcript;
      }
      onChange(valueRef.current + (valueRef.current ? ' ' : '') + newTranscript);
    };

    recognition.onerror = (event) => {
      console.error('Speech recognition error', event.error);
      setIsListening(false);
    };

    recognition.onend = () => setIsListening(false);

    recognition.start();
  };

  /* ─── Camera ─── */
  const handleOpenCamera = async () => {
    setShowUploadMenu(false);
    setShowCamera(true);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      streamRef.current = stream;
      setTimeout(() => {
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
        }
      }, 100);
    } catch (err) {
      console.error("Camera access denied or not available", err);
      setShowCamera(false);
    }
  };

  const closeCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
    }
    setShowCamera(false);
  };

  const takePhoto = () => {
    const video = videoRef.current;
    if (!video) return;

    const canvas = canvasRef.current;
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext('2d').drawImage(video, 0, 0);
    const dataUrl = canvas.toDataURL('image/png');

    setAttachedImage(dataUrl);
    closeCamera();
  };

  /* ─── Device file upload ─── */
  const handleUploadDevice = () => {
    deviceInputRef.current?.click();
    setShowUploadMenu(false);
  };

  const handleFileSelected = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => {
      setAttachedImage(reader.result);
    };
    reader.readAsDataURL(file);
    e.target.value = '';
  };

  return (
    <div className="chat-input-wrapper">
      {/* Main container with image preview + input bar */}
      <div style={{
        background: 'var(--color-surface)',
        border: '1px solid var(--color-border)',
        borderRadius: 'var(--radius-lg)',
        overflow: 'visible',
        transition: 'border-color var(--transition-fast)'
      }}>
        {/* Attached image preview — inside the container, above the input row */}
        {attachedImage && (
          <div style={{ padding: '12px 16px 0 16px' }}>
            <div style={{ position: 'relative', display: 'inline-block' }}>
              <img
                src={attachedImage}
                alt="Attachment preview"
                style={{
                  width: '120px',
                  height: '120px',
                  objectFit: 'cover',
                  borderRadius: '10px',
                  border: '1px solid var(--color-surface-3)'
                }}
              />
              <button
                onClick={() => setAttachedImage(null)}
                style={{
                  position: 'absolute',
                  top: '-8px',
                  right: '-8px',
                  width: '22px',
                  height: '22px',
                  borderRadius: '50%',
                  background: '#000',
                  color: '#fff',
                  border: '2px solid var(--color-surface)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  cursor: 'pointer',
                  padding: 0
                }}
                aria-label="Remove attachment"
              >
                <X size={12} />
              </button>
            </div>
          </div>
        )}

        {/* Input row */}
        <div className="chat-input" style={{ border: 'none', borderRadius: 0, background: 'transparent' }}>
          {/* Upload menu */}
          <div style={{ position: 'relative' }} ref={uploadMenuRef}>
            <button className="chat-input__action" aria-label="Add attachment" onClick={() => setShowUploadMenu(!showUploadMenu)}>
              <PlusCircle size={20} />
            </button>

            {showUploadMenu && (
              <div style={{
                position: 'absolute',
                bottom: '40px',
                left: '0',
                background: 'var(--color-surface)',
                border: '1px solid var(--color-surface-3)',
                borderRadius: '8px',
                padding: '8px',
                display: 'flex',
                flexDirection: 'column',
                gap: '4px',
                minWidth: '160px',
                zIndex: 100,
                boxShadow: '0 4px 12px rgba(0,0,0,0.5)'
              }}>
                <button className="btn-ghost" style={{ textAlign: 'left', padding: '8px', fontSize: '11px', border: 'none' }} onClick={handleOpenCamera}>
                  Open Camera
                </button>
                <button className="btn-ghost" style={{ textAlign: 'left', padding: '8px', fontSize: '11px', border: 'none' }} onClick={handleUploadDevice}>
                  Upload from device
                </button>
              </div>
            )}

            <input
              type="file"
              ref={deviceInputRef}
              accept="image/*"
              style={{ display: 'none' }}
              onChange={handleFileSelected}
            />
          </div>

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
          <button
            className="chat-input__action"
            aria-label="Voice input"
            onClick={startListening}
            style={{ color: isListening ? 'var(--color-danger)' : 'inherit' }}
          >
            <Mic size={20} />
          </button>

          {/* Send button */}
          <button
            className="chat-input__send"
            onClick={handleSendWithImage}
            aria-label="Send message"
            disabled={!value.trim() && !attachedImage}
          >
            <Send size={18} />
          </button>
        </div>
      </div>

      {/* Disclaimer */}
      <p className="chat-input__disclaimer">
        Mealimizer AI can make mistakes. Verify nutritional data.
      </p>

      {/* Hidden canvas for camera capture */}
      <canvas ref={canvasRef} style={{ display: 'none' }} />

      {/* Camera Modal */}
      {showCamera && (
        <div style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
          background: 'rgba(0,0,0,0.8)', zIndex: 1000,
          display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center'
        }}>
          <div style={{ background: 'var(--color-surface)', padding: '20px', borderRadius: '12px', width: '90%', maxWidth: '500px', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
            <div style={{ width: '100%', display: 'flex', justifyContent: 'space-between', marginBottom: '15px' }}>
              <h3 style={{ margin: 0, color: 'var(--color-text)' }}>Camera</h3>
              <button onClick={closeCamera} className="btn-ghost" style={{ padding: '4px' }}>
                <X size={20} />
              </button>
            </div>
            <video ref={videoRef} autoPlay playsInline style={{ width: '100%', borderRadius: '8px', background: '#000', marginBottom: '15px' }} />
            <button
              onClick={takePhoto}
              style={{ background: 'var(--color-primary)', color: 'white', border: 'none', borderRadius: '50%', width: '60px', height: '60px', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer' }}
            >
              <Camera size={24} />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
