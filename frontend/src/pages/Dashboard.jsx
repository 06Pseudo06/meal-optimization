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

import { useState, useEffect } from 'react';
import {
  Home as HomeIcon, Flame, Beef, Wheat, Droplet,
  Brain, Mic, Sparkles, ChevronRight
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

  /* State for API Data */
  const [apiData, setApiData] = useState({
    caloriesConsumed: 0,
    calorieTarget: 2000,
    proteinConsumed: 0,
    proteinTarget: 100
  });

  useEffect(() => {
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
            proteinTarget: data.protein_target || 100
          });
        }
      })
      .catch(err => console.error("Failed to fetch dashboard summary", err));
    }
  }, [token]);

  /* Mock/Dynamic stat cards data */
  const calProgress = apiData.calorieTarget > 0 ? (apiData.caloriesConsumed / apiData.calorieTarget) * 100 : 0;
  const proProgress = apiData.proteinTarget > 0 ? (apiData.proteinConsumed / apiData.proteinTarget) * 100 : 0;

  const stats = [
    { icon: HomeIcon, label: 'Daily Goal', title: 'Calories', value: Math.round(apiData.caloriesConsumed), unit: `/ ${Math.round(apiData.calorieTarget)} kcal`, color: 'var(--color-primary)', progress: calProgress },
    { icon: Beef, label: 'Protein', value: `${Math.round(apiData.proteinConsumed)}g`, unit: `/ ${Math.round(apiData.proteinTarget)}g`, color: '#ff6b6b', progress: proProgress },
    { icon: Wheat, label: 'Carbs', value: '0g', unit: '/ - g', color: '#ffa502', progress: 0 },
    { icon: Droplet, label: 'Fats', value: '0g', unit: '/ - g', color: '#ff4757', progress: 0 },
  ];

  /* AI Insight mock data */
  const weeklyStats = [
    { label: 'Weekly Avg', value: '2,150 kcal' },
    { label: 'Adherence', value: '94%' },
    { label: 'Water Score', value: '●●○' },
  ];

  /* Recent intake entries */
  const recentIntake = [
    { name: 'Logging System Pending', meal: 'Analysis', time: '--:--', kcal: 0, tag: 'N/A', dots: ['#3838ff', '#ff6b6b'] }
  ];

  /* Weight journey data (mock for chart) */
  const weightDays = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
  const weightValues = [20, 30, 25, 35, 30, 60]; /* relative bar heights */

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
            />
            <button className="dashboard__log-mic" aria-label="Voice input">
              <Mic size={18} />
            </button>
          </div>
          <div className="dashboard__log-suggestions">
            {quickFoods.map((food, i) => (
              <span key={i} className="dashboard__log-tag">{food}</span>
            ))}
          </div>
          <button className="btn-primary dashboard__log-btn">
            <Sparkles size={14} />
            Analyze with AI
          </button>
        </div>
      </section>

      {/* ---- Bottom Row: Recent Intake + Weight Journey ---- */}
      <section className="dashboard__bottom-row">
        {/* Recent Intake */}
        <div className="dashboard__recent card">
          <div className="dashboard__recent-header">
            <h3>Recent Intake</h3>
            <button className="dashboard__recent-view label-ui">View All</button>
          </div>
          <div className="dashboard__recent-list">
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

        {/* Weight Journey */}
        <div className="dashboard__weight card">
          <div className="dashboard__weight-header">
            <h3>Weight Journey</h3>
            <span className="dashboard__weight-change">↓ 1.8 Kg This Week</span>
          </div>
          <div className="dashboard__weight-value">
            78.4
            <span className="dashboard__weight-label">Current Body Weight (Kg)</span>
          </div>
          {/* Simple bar chart */}
          <div className="dashboard__weight-chart">
            {weightDays.map((day, i) => (
              <div key={i} className="dashboard__weight-col">
                <div
                  className="dashboard__weight-bar"
                  style={{
                    height: `${weightValues[i]}%`,
                    backgroundColor: i === weightDays.length - 1 ? 'var(--color-primary)' : 'var(--color-surface-3)'
                  }}
                />
                <span className="dashboard__weight-day">{day}</span>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}