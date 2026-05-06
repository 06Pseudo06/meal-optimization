import React from 'react';
import { Flame, Beef, Wheat, Droplet, Sparkles, CheckCircle2, Lightbulb } from 'lucide-react';
import './RecommendationCard.css';

export default function RecommendationCard({ data }) {
  if (!data) return null;

  const {
    name,
    calories,
    protein,
    carbs,
    fats,
    confidenceLabel,
    explanationText,
    tags,
    dietType,
    isQuick,
    isGymFriendly
  } = data;

  // Build the array of chips
  const chips = [];
  if (dietType && dietType.toLowerCase() !== 'non_veg') {
    chips.push(dietType.charAt(0).toUpperCase() + dietType.slice(1));
  }
  if (isGymFriendly) chips.push('Gym Friendly');
  if (isQuick) chips.push('Quick Meal');
  if (protein > 25) chips.push('High Protein');
  if (calories < 450) chips.push('Low Calorie');
  if (tags && Array.isArray(tags)) {
    tags.forEach(t => {
      const formatted = t.charAt(0).toUpperCase() + t.slice(1);
      if (!chips.includes(formatted)) chips.push(formatted);
    });
  }

  // Determine icon and color based on confidence label
  let ConfIcon = Sparkles;
  let confClass = "recommendation-card__conf--good";
  
  if (confidenceLabel.includes('Recommended') || confidenceLabel.includes('High Confidence')) {
    ConfIcon = CheckCircle2;
    confClass = "recommendation-card__conf--high";
  } else if (confidenceLabel.includes('Alternative')) {
    ConfIcon = Lightbulb;
    confClass = "recommendation-card__conf--alt";
  }

  return (
    <div className="recommendation-card">
      <div className="recommendation-card__header">
        <h3 className="recommendation-card__title">🍽️ {name}</h3>
        <div className={`recommendation-card__confidence ${confClass}`}>
          {confidenceLabel}
        </div>
      </div>

      <div className="recommendation-card__macros">
        <div className="macro-chip macro-chip--cal">
          <Flame size={14} />
          <span><strong>{Math.round(calories)}</strong> kcal</span>
        </div>
        <div className="macro-chip macro-chip--pro">
          <Beef size={14} />
          <span><strong>{Math.round(protein)}g</strong> protein</span>
        </div>
        <div className="macro-chip macro-chip--carb">
          <Wheat size={14} />
          <span><strong>{Math.round(carbs || 0)}g</strong> carbs</span>
        </div>
        <div className="macro-chip macro-chip--fat">
          <Droplet size={14} />
          <span><strong>{Math.round(fats || 0)}g</strong> fats</span>
        </div>
      </div>

      <div className="recommendation-card__explanation">
        <div className="explanation-header">
          <Sparkles size={16} />
          <span>Why this fits:</span>
        </div>
        <p className="explanation-body">{explanationText}</p>
      </div>

      {chips.length > 0 && (
        <div className="recommendation-card__tags">
          {chips.map((chip, idx) => (
            <span key={idx} className="recipe-tag">
              {chip}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}
