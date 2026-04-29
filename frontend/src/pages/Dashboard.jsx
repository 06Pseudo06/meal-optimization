/**
 * Dashboard.jsx — Main analytics dashboard
 * 
 * Displays nutrition overview with:
 * - Top stat cards (Daily Goal, Protein, Carbs, Fats)
 * - AI Nutritionist Insight with weekly stats
 * - Log Meal quick-add card
 * - Recent Intake list
 * - Weight Journey tracker
 * 
 * All data is mocked (would come from API in production).
 * User data is read dynamically from localStorage.
 */

import { useState, useEffect, useRef } from 'react';
import {
  Home as HomeIcon, Flame, Beef, Wheat, Droplet,
  Brain, Mic, MicOff, Sparkles, ChevronRight, Loader2, Check, AlertCircle, X
} from 'lucide-react';
import './Dashboard.css';

export default function Dashboard() {
  /* Parse user safely for personalized elements */
  const user = (() => {
    try {
      return JSON.parse(localStorage.getItem('user')) || null;
    } catch {
      return null;
    }
  })();

  const token = localStorage.getItem('accessToken');

  /* Log Meal input state */
  const [mealInput, setMealInput] = useState('');

  /* Analyze state: 'idle' | 'analyzing' | 'success' | 'error' */
  const [analyzeStatus, setAnalyzeStatus] = useState('idle');
  const [analyzeResult, setAnalyzeResult] = useState(null);

  /* Speech recognition state */
  const [isListening, setIsListening] = useState(false);
  const recognitionRef = useRef(null);

  /* View All modal state */
  const [showAllMeals, setShowAllMeals] = useState(false);

  /* State for API Data */
  const [apiData, setApiData] = useState({
    caloriesConsumed: 0,
    calorieTarget: 2000,
    proteinConsumed: 0,
    proteinTarget: 100,
    carbsConsumed: 0,
    carbsTarget: 0,
    fatsConsumed: 0,
    fatsTarget: 0
  });

  /* User profile (weight, targets) */
  const [userProfile, setUserProfile] = useState(null);

  /* Recent intake from recommendation history */
  const [recentIntake, setRecentIntake] = useState([]);

  /* Fetch today's summary */
  const fetchTodaySummary = () => {
    if (token) {
      fetch('http://localhost:8000/logs/today', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      .then(res => res.json())
      .then(data => {
        if (!data.detail) {
          setApiData({
            caloriesConsumed: data.calories_consumed || 0,
            calorieTarget: data.calorie_target || 2000,
            proteinConsumed: data.protein_consumed || 0,
            proteinTarget: data.protein_target || 100,
            carbsConsumed: data.carbs_consumed || 0,
            carbsTarget: data.carbs_target || 0,
            fatsConsumed: data.fats_consumed || 0,
            fatsTarget: data.fats_target || 0
          });
        }
      })
      .catch(err => console.error("Failed to fetch dashboard summary", err));
    }
  };

  /* Fetch user profile for weight data */
  const fetchUserProfile = () => {
    if (token) {
      fetch('http://localhost:8000/user/me', {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      .then(res => res.json())
      .then(data => {
        if (!data.detail) setUserProfile(data);
      })
      .catch(err => console.error('Failed to fetch user profile', err));
    }
  };

  /* Fetch recent intake from recommendation history */
  const fetchRecentIntake = () => {
    if (token) {
      fetch('http://localhost:8000/recipes/history', {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      .then(res => res.json())
      .then(data => {
        if (Array.isArray(data)) {
          const items = data.slice(0, 5).map(entry => {
            const recipes = entry.recommendations || [];
            const top = recipes[0];
            const ts = entry.created_at ? new Date(entry.created_at) : null;
            const timeStr = ts ? ts.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : '--:--';
            const hour = ts ? ts.getHours() : 12;
            const mealType = hour < 11 ? 'Breakfast' : hour < 15 ? 'Lunch' : hour < 18 ? 'Snack' : 'Dinner';
            return {
              name: top?.name || 'Unknown meal',
              meal: mealType,
              time: timeStr,
              kcal: Math.round(top?.calories || 0),
              tag: top?.diet_type || 'N/A',
              dots: ['#3838ff', '#ff6b6b']
            };
          });
          setRecentIntake(items);
        }
      })
      .catch(err => console.error('Failed to fetch recent intake', err));
    }
  };

  useEffect(() => {
    fetchTodaySummary();
    fetchUserProfile();
    fetchRecentIntake();
  }, [token]);

  /* ---- Speech Recognition (Mic button) ---- */
  const toggleListening = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      alert('Speech recognition is not supported in your browser. Please use Chrome or Edge.');
      return;
    }

    if (isListening) {
      /* Stop listening */
      recognitionRef.current?.stop();
      setIsListening(false);
      return;
    }

    /* Start listening */
    const recognition = new SpeechRecognition();
    recognition.lang = 'en-US';
    recognition.interimResults = false;
    recognition.continuous = false;
    recognition.maxAlternatives = 1;

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      setMealInput(prev => prev ? `${prev}, ${transcript}` : transcript);
      setIsListening(false);
    };

    recognition.onerror = () => {
      setIsListening(false);
    };

    recognition.onend = () => {
      setIsListening(false);
    };

    recognitionRef.current = recognition;
    recognition.start();
    setIsListening(true);
  };

  /* ---- Quick-tag click handler ---- */
  const handleTagClick = (food) => {
    setMealInput(prev => {
      if (!prev.trim()) return food;
      /* Avoid duplicates */
      const existing = prev.split(',').map(s => s.trim().toLowerCase());
      if (existing.includes(food.toLowerCase())) return prev;
      return `${prev}, ${food}`;
    });
  };

  /* ---- Analyze with AI ---- */
  const handleAnalyze = async () => {
    const text = mealInput.trim();
    if (!text || analyzeStatus === 'analyzing') return;

    setAnalyzeStatus('analyzing');
    setAnalyzeResult(null);

    try {
      /* Step 1: Get AI recommendation based on the meal description */
      const recResponse = await fetch('http://localhost:8000/recipes/recommend', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token && { 'Authorization': `Bearer ${token}` })
        },
        body: JSON.stringify({ query: text })
      });

      if (!recResponse.ok) throw new Error('Recommendation API failed');

      const recipes = await recResponse.json();

      if (!Array.isArray(recipes) || recipes.length === 0) {
        setAnalyzeResult({ message: 'No matching recipe found for your meal. Try different keywords.' });
        setAnalyzeStatus('error');
        return;
      }

      const topRecipe = recipes[0];
      const recipeId = topRecipe.id ?? topRecipe.recipe_id;

      /* Step 2: Log the matched recipe to the daily log */
      const logResponse = await fetch('http://localhost:8000/logs/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token && { 'Authorization': `Bearer ${token}` })
        },
        body: JSON.stringify({ user_id: 0, recipe_id: recipeId })
      });

      if (!logResponse.ok) throw new Error('Failed to log meal');

      setAnalyzeResult({
        message: `Logged "${topRecipe.name}" — ${Math.round(topRecipe.calories || 0)} kcal, ${Math.round(topRecipe.protein || 0)}g protein`,
        recipe: topRecipe
      });
      setAnalyzeStatus('success');
      setMealInput('');

      /* Step 3: Refresh dashboard stats */
      fetchTodaySummary();

    } catch (err) {
      console.error('Analyze error:', err);
      setAnalyzeResult({ message: 'Failed to analyze meal. Please try again.' });
      setAnalyzeStatus('error');
    }
  };

  /* Dynamic stat cards data */
  const calProgress = apiData.calorieTarget > 0 ? (apiData.caloriesConsumed / apiData.calorieTarget) * 100 : 0;
  const proProgress = apiData.proteinTarget > 0 ? (apiData.proteinConsumed / apiData.proteinTarget) * 100 : 0;
  const carbProgress = apiData.carbsTarget > 0 ? (apiData.carbsConsumed / apiData.carbsTarget) * 100 : 0;
  const fatProgress = apiData.fatsTarget > 0 ? (apiData.fatsConsumed / apiData.fatsTarget) * 100 : 0;

  const stats = [
    { icon: HomeIcon, label: 'Daily Goal', title: 'Calories', value: Math.round(apiData.caloriesConsumed), unit: `/ ${Math.round(apiData.calorieTarget)} kcal`, color: 'var(--color-primary)', progress: calProgress },
    { icon: Beef, label: 'Protein', value: `${Math.round(apiData.proteinConsumed)}g`, unit: `/ ${Math.round(apiData.proteinTarget)}g`, color: '#ff6b6b', progress: proProgress },
    { icon: Wheat, label: 'Carbs', value: `${Math.round(apiData.carbsConsumed)}g`, unit: `/ ${apiData.carbsTarget > 0 ? Math.round(apiData.carbsTarget) : '-'}g`, color: '#ffa502', progress: carbProgress },
    { icon: Droplet, label: 'Fats', value: `${Math.round(apiData.fatsConsumed)}g`, unit: `/ ${apiData.fatsTarget > 0 ? Math.round(apiData.fatsTarget) : '-'}g`, color: '#ff4757', progress: fatProgress },
  ];

  /* Weekly stats derived from real data */
  const todayKcal = Math.round(apiData.caloriesConsumed);
  const adherencePercent = apiData.calorieTarget > 0
    ? Math.min(100, Math.round((apiData.caloriesConsumed / apiData.calorieTarget) * 100))
    : 0;
  const weeklyStats = [
    { label: 'Today', value: `${todayKcal.toLocaleString()} kcal` },
    { label: 'Goal Hit', value: `${adherencePercent}%` },
    { label: 'Protein', value: `${Math.round(apiData.proteinConsumed)}g` },
  ];

  /* Weight data from user profile */
  const currentWeight = userProfile?.current_weight ?? null;
  const weightGoal = userProfile?.weight_goal ?? null;
  const weightDiff = (currentWeight && weightGoal) ? (currentWeight - weightGoal) : null;

  /* Build calorie chart from recent intake (last 6 entries as daily proxies) */
  const dayLabels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
  const recentKcals = recentIntake.slice(0, 6).map(e => e.kcal);
  const maxKcal = Math.max(...recentKcals, 1);
  const chartValues = dayLabels.map((_, i) => {
    const kcal = recentKcals[i] || 0;
    return Math.round((kcal / maxKcal) * 100);
  });

  /* Quick-add food suggestions */
  const quickFoods = ['Chicken', 'Oats', 'Avocado'];

  return (
    <div className="dashboard">
      {/* ---- Top Stats Row ---- */}
      <section className="dashboard__stats">
        {stats.map((stat, i) => (
          <div key={i} className="dashboard__stat-card card">
            <div className="dashboard__stat-header">
              <span className="dashboard__stat-icon" style={{ color: stat.color }}>
                <stat.icon size={14} />
              </span>
              <span className="label-ui">{stat.label}</span>
            </div>
            {stat.title && <h4 className="dashboard__stat-title">{stat.title}</h4>}
            <div className="dashboard__stat-value">
              {stat.value} <span className="dashboard__stat-unit">{stat.unit}</span>
            </div>
            {/* Progress mini-bars */}
            <div className="dashboard__stat-bars">
              {[...Array(4)].map((_, j) => (
                <div
                  key={j}
                  className="dashboard__stat-bar"
                  style={{
                    backgroundColor: j < Math.floor(stat.progress / 25)
                      ? stat.color
                      : 'var(--color-surface-3)'
                  }}
                />
              ))}
            </div>
          </div>
        ))}
      </section>

      {/* ---- AI Insight + Log Meal Row ---- */}
      <section className="dashboard__middle-row">
        {/* AI Nutritionist Insight */}
        <div className="dashboard__insight card">
          <div className="dashboard__insight-header">
            <span className="dashboard__insight-dot">●</span>
            <span className="label-ui">AI Nutritionist Insight</span>
          </div>
          <div className="dashboard__insight-body">
            <div className="dashboard__insight-text">
              <p className="dashboard__insight-quote">
                "Your protein intake is 12% higher this week, optimizing muscle recovery."
              </p>
              <p className="dashboard__insight-detail">
                Based on your recent meal logs and biometric data, increasing your hydration by 500ml
                before your afternoon workout could further enhance metabolism.
              </p>
            </div>
            <Brain size={48} className="dashboard__insight-icon" />
          </div>
          {/* Weekly stats row */}
          <div className="dashboard__insight-stats">
            {weeklyStats.map((s, i) => (
              <div key={i} className="dashboard__insight-stat card">
                <span className="label-ui">{s.label}</span>
                <strong>{s.value}</strong>
              </div>
            ))}
          </div>
        </div>

        {/* Log Meal Card */}
        <div className="dashboard__log-meal card">
          <h3>Log Meal</h3>
          <div className="dashboard__log-input">
            <input
              type="text"
              placeholder="What did you eat?"
              value={mealInput}
              onChange={(e) => setMealInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleAnalyze()}
              disabled={analyzeStatus === 'analyzing'}
            />
            <button
              className={`dashboard__log-mic ${isListening ? 'dashboard__log-mic--active' : ''}`}
              aria-label={isListening ? 'Stop listening' : 'Voice input'}
              onClick={toggleListening}
              disabled={analyzeStatus === 'analyzing'}
            >
              {isListening ? <MicOff size={18} /> : <Mic size={18} />}
            </button>
          </div>
          <div className="dashboard__log-suggestions">
            {quickFoods.map((food, i) => (
              <span
                key={i}
                className="dashboard__log-tag"
                onClick={() => handleTagClick(food)}
                role="button"
                tabIndex={0}
                onKeyDown={(e) => e.key === 'Enter' && handleTagClick(food)}
              >
                {food}
              </span>
            ))}
          </div>
          <button
            className="btn-primary dashboard__log-btn"
            onClick={handleAnalyze}
            disabled={!mealInput.trim() || analyzeStatus === 'analyzing'}
          >
            {analyzeStatus === 'analyzing' ? (
              <><Loader2 size={14} className="spin-icon" /> Analyzing...</>
            ) : (
              <><Sparkles size={14} /> Analyze with AI</>
            )}
          </button>

          {/* Status feedback message */}
          {analyzeResult && (
            <div className={`dashboard__log-result dashboard__log-result--${analyzeStatus}`}>
              {analyzeStatus === 'success' ? <Check size={14} /> : <AlertCircle size={14} />}
              <span>{analyzeResult.message}</span>
            </div>
          )}
        </div>
      </section>

      {/* ---- Bottom Row: Recent Intake + Weight Journey ---- */}
      <section className="dashboard__bottom-row">
        {/* Recent Intake */}
        <div className="dashboard__recent card">
          <div className="dashboard__recent-header">
            <h3>Recent Intake</h3>
            {recentIntake.length > 2 && (
              <button className="dashboard__recent-view label-ui" onClick={() => setShowAllMeals(true)}>View All</button>
            )}
          </div>
          <div className="dashboard__recent-list">
            {recentIntake.length === 0 ? (
              <div className="dashboard__recent-item">
                <div className="dashboard__recent-thumb">
                  <Flame size={16} />
                </div>
                <div className="dashboard__recent-info">
                  <strong>No meals logged yet</strong>
                  <span>Use "Log Meal" above to get started</span>
                </div>
              </div>
            ) : (
              recentIntake.slice(0, 2).map((item, i) => (
                <div key={i} className="dashboard__recent-item">
                  <div className="dashboard__recent-thumb">
                    <Flame size={16} />
                  </div>
                  <div className="dashboard__recent-info">
                    <strong>{item.name}</strong>
                    <span>{item.meal} · {item.time}</span>
                  </div>
                  <div className="dashboard__recent-right">
                    <span className="dashboard__recent-kcal">{item.kcal}</span>
                    <span className="dashboard__recent-tag">{item.tag}</span>
                    <div className="dashboard__recent-dots">
                      {item.dots.map((c, j) => (
                        <span key={j} className="dashboard__recent-dot" style={{ backgroundColor: c }} />
                      ))}
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Weight Journey */}
        <div className="dashboard__weight card">
          <div className="dashboard__weight-header">
            <h3>Weight Journey</h3>
            {weightDiff !== null && (
              <span 
                className="dashboard__weight-change"
                style={{
                  color: weightDiff > 0 ? 'var(--color-danger)' : 
                         weightDiff < 0 ? 'var(--color-success)' : 'var(--color-success)'
                }}
              >
                {weightDiff > 0 
                  ? `↑ ${weightDiff.toFixed(1)} Kg ahead` 
                  : weightDiff < 0 
                    ? `↓ ${Math.abs(weightDiff).toFixed(1)} Kg behind` 
                    : '✓ Goal reached!'}
              </span>
            )}
          </div>
          <div className="dashboard__weight-value">
            {currentWeight !== null ? currentWeight.toFixed(1) : '—'}
            <span className="dashboard__weight-label">
              Current Body Weight (Kg){weightGoal ? ` · Goal: ${weightGoal} Kg` : ''}
            </span>
          </div>
          {/* Calorie intake chart from recent logs */}
          <div className="dashboard__weight-chart">
            {dayLabels.map((day, i) => (
              <div key={i} className="dashboard__weight-col">
                <div
                  className="dashboard__weight-bar"
                  style={{
                    height: `${chartValues[i] || 5}%`,
                    backgroundColor: i === recentKcals.length - 1 && recentKcals[i] ? 'var(--color-primary)' : 'var(--color-surface-3)'
                  }}
                />
                <span className="dashboard__weight-day">{day}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ---- View All Meals Modal ---- */}
      {showAllMeals && (
        <div className="dashboard__modal-overlay" onClick={() => setShowAllMeals(false)}>
          <div className="dashboard__modal" onClick={(e) => e.stopPropagation()}>
            <div className="dashboard__modal-header">
              <h3>Today's Meals</h3>
              <button className="dashboard__modal-close" onClick={() => setShowAllMeals(false)} aria-label="Close">
                <X size={18} />
              </button>
            </div>
            <div className="dashboard__modal-list">
              {recentIntake.map((item, i) => (
                <div key={i} className="dashboard__recent-item">
                  <div className="dashboard__recent-thumb">
                    <Flame size={16} />
                  </div>
                  <div className="dashboard__recent-info">
                    <strong>{item.name}</strong>
                    <span>{item.meal} · {item.time}</span>
                  </div>
                  <div className="dashboard__recent-right">
                    <span className="dashboard__recent-kcal">{item.kcal}</span>
                    <span className="dashboard__recent-tag">{item.tag}</span>
                    <div className="dashboard__recent-dots">
                      {item.dots.map((c, j) => (
                        <span key={j} className="dashboard__recent-dot" style={{ backgroundColor: c }} />
                      ))}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}