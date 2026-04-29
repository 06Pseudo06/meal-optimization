import React, { useState, useEffect, useRef } from 'react';

const AnimatedCharacters = ({ isPasswordVisible = false }) => {
  const svgRef = useRef(null);
  const [target, setTarget] = useState({ x: window.innerWidth / 2, y: window.innerHeight / 2 });

  useEffect(() => {
    const handleMouseMove = (e) => {
      // If an input is actively focused, don't follow mouse
      if (document.activeElement && document.activeElement.tagName === 'INPUT') {
        const rect = document.activeElement.getBoundingClientRect();
        setTarget({
          x: rect.left + rect.width / 2,
          y: rect.top + rect.height / 2
        });
      } else {
        setTarget({ x: e.clientX, y: e.clientY });
      }
    };

    const handleFocus = (e) => {
      if (e.target.tagName === 'INPUT') {
        const rect = e.target.getBoundingClientRect();
        setTarget({
          x: rect.left + rect.width / 2,
          y: rect.top + rect.height / 2
        });
      }
    };

    const handleScroll = () => {
      if (document.activeElement && document.activeElement.tagName === 'INPUT') {
        const rect = document.activeElement.getBoundingClientRect();
        setTarget({
          x: rect.left + rect.width / 2,
          y: rect.top + rect.height / 2
        });
      }
    };

    const handleBlur = (e) => {
      // When leaving an input, revert to center of the screen temporarily until mouse moves
      setTarget({ x: window.innerWidth / 2, y: window.innerHeight / 2 });
    };

    window.addEventListener('mousemove', handleMouseMove);
    window.addEventListener('focusin', handleFocus);
    window.addEventListener('focusout', handleBlur);
    window.addEventListener('scroll', handleScroll, true);

    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('focusin', handleFocus);
      window.removeEventListener('focusout', handleBlur);
      window.removeEventListener('scroll', handleScroll, true);
    };
  }, []);

  const eyeCenters = {
    carrotL: { cx: 121, cy: 216, r: 11 },
    carrotR: { cx: 161, cy: 214, r: 11 },
    brinjalL: { cx: 276, cy: 239, r: 9 },
    brinjalR: { cx: 307, cy: 247, r: 9 },
    potatoL: { cx: 223, cy: 374, r: 10 },
    potatoR: { cx: 267, cy: 374, r: 10 },
  };

  const [pupils, setPupils] = useState({
    carrotL: { x: 0, y: 0 },
    carrotR: { x: 0, y: 0 },
    brinjalL: { x: 0, y: 0 },
    brinjalR: { x: 0, y: 0 },
    potatoL: { x: 0, y: 0 },
    potatoR: { x: 0, y: 0 },
  });

  useEffect(() => {
    if (!svgRef.current) return;
    const svgRect = svgRef.current.getBoundingClientRect();

    // Fallback if the element is not rendered correctly yet
    if (svgRect.width === 0 || svgRect.height === 0) return;

    const scaleX = svgRect.width / 400;
    const scaleY = svgRect.height / 500;

    const newPupils = {};

    Object.keys(eyeCenters).forEach((key) => {
      const eye = eyeCenters[key];
      const eyeScreenX = svgRect.left + eye.cx * scaleX;
      const eyeScreenY = svgRect.top + eye.cy * scaleY;

      const angle = Math.atan2(target.y - eyeScreenY, target.x - eyeScreenX);
      const distance = Math.hypot(target.y - eyeScreenY, target.x - eyeScreenX);

      const maxR = eye.r;
      // The further away the target, the closer to the edge the pupil goes
      const moveR = Math.min(distance * 0.05, maxR);

      newPupils[key] = {
        x: Math.cos(angle) * moveR,
        y: Math.sin(angle) * moveR,
      };
    });

    setPupils(newPupils);
  }, [target]);

  return (
    <svg
      ref={svgRef}
      viewBox="0 0 400 500"
      style={{
        width: '100%',
        height: '100%',
        display: 'block',
        filter: 'drop-shadow(0 10px 20px rgba(0,0,0,0.5))',
        transform: 'scale(1.35) translate(-15px, 25px)'
      }}
    >
      <defs>
        {/* Carrot Gradients */}
        <linearGradient id="carrotGrad" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#FFA726" />
          <stop offset="100%" stopColor="#E65100" />
        </linearGradient>

        {/* Brinjal Gradients */}
        <linearGradient id="brinjalGrad" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#AB47BC" />
          <stop offset="100%" stopColor="#4A148C" />
        </linearGradient>

        {/* Potato Gradients */}
        <linearGradient id="potatoGrad" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#D4A373" />
          <stop offset="100%" stopColor="#A67C52" />
        </linearGradient>
      </defs>

      {/* --- EGGPLANT / BRINJAL --- */}
      <g id="brinjal" transform="translate(280, 285) rotate(15) scale(1.08) translate(-280, -300)">
        {/* Body */}
        <path
          d="M 280 160 C 330 160 360 260 360 340 C 360 410 320 440 280 440 C 240 440 200 410 200 340 C 200 260 230 160 280 160 Z"
          fill="url(#brinjalGrad)"
        />
        {/* Green Cap */}
        <path
          d="M 280 130 C 285 130 285 140 290 145 C 310 150 320 160 310 170 C 300 180 290 170 280 175 C 270 170 260 180 250 170 C 240 160 250 150 270 145 C 275 140 275 130 280 130 Z"
          fill="#8BC34A"
        />
        <path
          d="M 280 120 C 275 120 275 135 280 135 C 285 135 285 120 280 120 Z"
          fill="#689F38"
        />
        {/* Left Eye */}
        <circle cx="265" cy="260" r="18" fill="white" />
        <circle
          cx="265" cy="260" r="8" fill="black"
          transform={`translate(${pupils.brinjalL.x}, ${pupils.brinjalL.y})`}
        />
        <circle
          cx="263" cy="257" r="2.5" fill="white"
          transform={`translate(${pupils.brinjalL.x}, ${pupils.brinjalL.y})`}
        />
        {/* Right Eye */}
        <circle cx="295" cy="260" r="18" fill="white" />
        <circle
          cx="295" cy="260" r="8" fill="black"
          transform={`translate(${pupils.brinjalR.x}, ${pupils.brinjalR.y})`}
        />
        <circle
          cx="293" cy="257" r="2.5" fill="white"
          transform={`translate(${pupils.brinjalR.x}, ${pupils.brinjalR.y})`}
        />
        {/* Mouth */}
        <path d="M 270 295 C 275 315 285 315 290 295 Z" fill="#000" />
        <path d="M 275 305 C 280 310 280 310 285 305 Z" fill="#E53935" />

        {/* Hands covering eyes */}
        <g style={{ transform: isPasswordVisible ? 'translateY(0)' : 'translateY(40px)', opacity: isPasswordVisible ? 1 : 0, transition: 'all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1)', filter: 'drop-shadow(0 0 1px #000)' }}>
          <path d="M 245 330 Q 255 290 265 260" fill="none" stroke="#4A148C" strokeWidth="14" strokeLinecap="round" />
          <circle cx="265" cy="260" r="21" fill="#4A148C" />
          <path d="M 265 260 L 250 240 M 265 260 L 262 230 M 265 260 L 278 240" fill="none" stroke="#4A148C" strokeWidth="12" strokeLinecap="round" />
        </g>
        <g style={{ transform: isPasswordVisible ? 'translateY(0)' : 'translateY(40px)', opacity: isPasswordVisible ? 1 : 0, transition: 'all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1)', transitionDelay: '0.1s', filter: 'drop-shadow(0 0 1px #000)' }}>
          <path d="M 315 330 Q 305 290 295 260" fill="none" stroke="#4A148C" strokeWidth="14" strokeLinecap="round" />
          <circle cx="295" cy="260" r="21" fill="#4A148C" />
          <path d="M 295 260 L 282 240 M 295 260 L 298 230 M 295 260 L 310 240" fill="none" stroke="#4A148C" strokeWidth="12" strokeLinecap="round" />
        </g>
      </g>

      {/* --- CARROT --- */}
      <g id="carrot" transform="translate(140, 250) rotate(-3) scale(1.15) translate(-140, -250)">
        {/* Leaves */}
        <path d="M 140 100 Q 110 30 90 20 Q 120 60 130 100 Z" fill="#4CAF50" />
        <path d="M 140 100 Q 130 20 135 10 Q 150 60 145 100 Z" fill="#388E3C" />
        <path d="M 140 100 Q 170 30 190 20 Q 160 60 150 100 Z" fill="#4CAF50" />
        {/* Body */}
        <path
          d="M 140 100 C 200 100 200 150 190 250 C 175 350 165 450 140 470 C 115 450 105 350 90 250 C 80 150 80 100 140 100 Z"
          fill="url(#carrotGrad)"
        />
        {/* Small detail lines on carrot */}
        <path d="M 115 150 Q 130 155 145 150" stroke="#E65100" strokeWidth="3" strokeLinecap="round" fill="none" opacity="0.5" />
        <path d="M 135 180 Q 150 185 165 180" stroke="#E65100" strokeWidth="3" strokeLinecap="round" fill="none" opacity="0.5" />
        <path d="M 110 280 Q 125 285 140 280" stroke="#E65100" strokeWidth="3" strokeLinecap="round" fill="none" opacity="0.5" />
        <path d="M 130 350 Q 140 355 150 350" stroke="#E65100" strokeWidth="3" strokeLinecap="round" fill="none" opacity="0.5" />
        <path d="M 120 410 Q 130 415 140 410" stroke="#E65100" strokeWidth="3" strokeLinecap="round" fill="none" opacity="0.5" />

        {/* Left Eye */}
        <circle cx="125" cy="220" r="22" fill="white" />
        <circle
          cx="125" cy="220" r="10" fill="black"
          transform={`translate(${pupils.carrotL.x}, ${pupils.carrotL.y})`}
        />
        <circle
          cx="122" cy="216" r="3" fill="white"
          transform={`translate(${pupils.carrotL.x}, ${pupils.carrotL.y})`}
        />
        {/* Right Eye */}
        <circle cx="160" cy="220" r="22" fill="white" />
        <circle
          cx="160" cy="220" r="10" fill="black"
          transform={`translate(${pupils.carrotR.x}, ${pupils.carrotR.y})`}
        />
        <circle
          cx="157" cy="216" r="3" fill="white"
          transform={`translate(${pupils.carrotR.x}, ${pupils.carrotR.y})`}
        />
        {/* Mouth */}
        <path d="M 130 260 C 138 285 152 285 160 260 Z" fill="#000" />
        <path d="M 138 273 C 145 278 145 278 152 273 Z" fill="#E53935" />

        {/* Hands covering eyes */}
        <g style={{ transform: isPasswordVisible ? 'translateY(0)' : 'translateY(40px)', opacity: isPasswordVisible ? 1 : 0, transition: 'all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1)', filter: 'drop-shadow(0 0 1px #000)' }}>
          <path d="M 105 290 Q 115 250 125 220" fill="none" stroke="#D84315" strokeWidth="18" strokeLinecap="round" />
          <circle cx="125" cy="220" r="25" fill="#D84315" />
          <path d="M 125 220 L 105 195 M 125 220 L 122 185 M 125 220 L 142 195" fill="none" stroke="#D84315" strokeWidth="14" strokeLinecap="round" strokeLinejoin="round" />
        </g>
        <g style={{ transform: isPasswordVisible ? 'translateY(0)' : 'translateY(40px)', opacity: isPasswordVisible ? 1 : 0, transition: 'all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1)', transitionDelay: '0.05s', filter: 'drop-shadow(0 0 1px #000)' }}>
          <path d="M 180 290 Q 170 250 160 220" fill="none" stroke="#D84315" strokeWidth="18" strokeLinecap="round" />
          <circle cx="160" cy="220" r="25" fill="#D84315" />
          <path d="M 160 220 L 143 195 M 160 220 L 163 185 M 160 220 L 180 195" fill="none" stroke="#D84315" strokeWidth="14" strokeLinecap="round" strokeLinejoin="round" />
        </g>
      </g>

      {/* --- POTATO --- */}
      <g id="potato" transform="translate(245, 385) scale(1.1) translate(-195, -385)">
        {/* Body */}
        <path
          d="M 200 315 C 250 315, 300 345, 305 390 C 310 435, 240 460, 185 465 C 130 470, 95 425, 85 380 C 75 335, 150 315, 200 315 Z"
          fill="url(#potatoGrad)"
          transform="rotate(-5, 195, 385)"
        />

        {/* Potato Spots */}
        <circle cx="130" cy="350" r="4" fill="#8D6E63" opacity="0.6" />
        <circle cx="260" cy="360" r="5" fill="#8D6E63" opacity="0.6" />
        <circle cx="270" cy="410" r="4" fill="#8D6E63" opacity="0.6" />
        <circle cx="120" cy="400" r="3" fill="#8D6E63" opacity="0.6" />
        <circle cx="195" cy="445" r="4" fill="#8D6E63" opacity="0.6" />

        {/* Left Eye */}
        <circle cx="175" cy="375" r="18" fill="white" />
        <circle
          cx="175" cy="375" r="9" fill="black"
          transform={`translate(${pupils.potatoL.x}, ${pupils.potatoL.y})`}
        />
        <circle
          cx="172" cy="371" r="2.5" fill="white"
          transform={`translate(${pupils.potatoL.x}, ${pupils.potatoL.y})`}
        />
        {/* Right Eye */}
        <circle cx="215" cy="375" r="18" fill="white" />
        <circle
          cx="215" cy="375" r="9" fill="black"
          transform={`translate(${pupils.potatoR.x}, ${pupils.potatoR.y})`}
        />
        <circle
          cx="212" cy="371" r="2.5" fill="white"
          transform={`translate(${pupils.potatoR.x}, ${pupils.potatoR.y})`}
        />
        {/* Mouth */}
        <path d="M 185 405 C 195 425 205 425 215 405 Z" fill="#000" />
        <path d="M 192 414 C 195 418 205 418 208 414 Z" fill="#E53935" />

        {/* Hands covering eyes */}
        <g style={{ transform: isPasswordVisible ? 'translateY(0)' : 'translateY(40px)', opacity: isPasswordVisible ? 1 : 0, transition: 'all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1)', transitionDelay: '0.05s', filter: 'drop-shadow(0 0 1px #000)' }}>
          <path d="M 155 445 Q 165 405 175 375" fill="none" stroke="#8D6E63" strokeWidth="14" strokeLinecap="round" />
          <circle cx="175" cy="375" r="21" fill="#8D6E63" />
          <path d="M 175 375 L 160 355 M 175 375 L 172 345 M 175 375 L 188 355" fill="none" stroke="#8D6E63" strokeWidth="12" strokeLinecap="round" />
        </g>
        <g style={{ transform: isPasswordVisible ? 'translateY(0)' : 'translateY(40px)', opacity: isPasswordVisible ? 1 : 0, transition: 'all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1)', transitionDelay: '0.15s', filter: 'drop-shadow(0 0 1px #000)' }}>
          <path d="M 235 445 Q 225 405 215 375" fill="none" stroke="#8D6E63" strokeWidth="14" strokeLinecap="round" />
          <circle cx="215" cy="375" r="21" fill="#8D6E63" />
          <path d="M 215 375 L 202 355 M 215 375 L 218 345 M 215 375 L 230 355" fill="none" stroke="#8D6E63" strokeWidth="12" strokeLinecap="round" />
        </g>
      </g>
    </svg>
  );
};

export default AnimatedCharacters;
