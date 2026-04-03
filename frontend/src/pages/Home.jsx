/**
 * Home.jsx — Home page with dual layout
 * 
 * GUEST (no token): Landing page with hero section, features grid, 
 * Mealimizer Concierge section, and CTA — matching the landing screenshot.
 * 
 * LOGGED IN: Personalized dashboard-like view with:
 * - Welcome greeting using user.first_name
 * - Calorie intake card with progress
 * - Body mass card
 * - Last logged entries list
 * - CTA to scan & log a meal
 * 
 * Dynamic user data is read from localStorage("user").
 */

import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  ArrowRight, Play, Activity, Target, ShoppingCart,
  MessageSquare, Home as HomeIcon, TrendingDown, Utensils,
  Flame, Camera, ChevronDown, Trash2, SlidersHorizontal
} from 'lucide-react';
import './Home.css';

export default function Home() {
  /* Check auth state */
  const token = localStorage.getItem('accessToken');

  /* Parse user safely — avoid crash if JSON is invalid */
  const user = (() => {
    try {
      return JSON.parse(localStorage.getItem('user')) || null;
    } catch {
      return null;
    }
  })();

  /* ============ GUEST LANDING PAGE ============ */
  if (!token) {
    return (
      <div className="landing">
        {/* --- Top Navbar for guests --- */}
        <nav className="landing__nav">
          <span className="landing__brand">Mealimizer</span>
          <div className="landing__nav-right">
            <Link to="/login" className="btn-ghost">Login</Link>
            <Link to="/register" className="btn-primary">Get Started</Link>
          </div>
        </nav>

        {/* --- Hero Section --- */}
        <section className="landing__hero">
          <h1 className="landing__hero-title">
            Smart Nutrition<br />
            <span className="landing__hero-accent">Powered by AI</span>
          </h1>
          <p className="landing__hero-subtitle">
            Revolutionize your relationship with food. Our obsidian-grade engine
            optimizes your macros, predicts metabolic shifts, and generates hyper-personalized
            meal paths in real-time.
          </p>
          <div className="landing__hero-cta">
            <Link to="/register" className="btn-primary">
              Get Started <ArrowRight size={16} />
            </Link>
            <button className="btn-ghost">
              <Play size={16} /> View Demo
            </button>
          </div>
        </section>

        {/* --- Feature Preview Cards --- */}
        <section className="landing__preview">
          <div className="landing__preview-card landing__preview-card--dark">
            <h4>Dashboard Preview</h4>
            <p>Safe Work<br />Safe Work</p>
            <div className="landing__preview-label">
              <span className="label-ui">Optimal Flow</span>
              <strong>Bio-Dynamic Meal Scheduling</strong>
            </div>
          </div>
          <div className="landing__preview-card landing__preview-card--blue">
            <Target size={24} />
            <h4>Neural Recipe Generation</h4>
            <p>AI analyzes your biometrics to synthesize recipes for mental clarity and physical recovery.</p>
          </div>
        </section>

        {/* --- Intelligence Features --- */}
        <section className="landing__features">
          <span className="label-ui">The Intelligence</span>
          <h2 className="landing__features-title">Designed for Peak Performance</h2>
          <div className="landing__features-grid">
            <div className="landing__feature-card">
              <Activity size={24} />
              <h3>Metabolic Tracking</h3>
              <p>Connect your wearables and let Mealimizer adapt your daily nutrition based on your actual energy expenditure.</p>
            </div>
            <div className="landing__feature-card landing__feature-card--highlight">
              <Target size={24} />
              <h3>Macro Precision Optimization</h3>
              <p>Forget calorie counting. Our AI balances micronutrient density and glycemic load for sustained vitality.</p>
              <div className="landing__feature-progress">
                <span>Protein Range</span>
                <div className="landing__feature-bar">
                  <div className="landing__feature-bar-fill" style={{ width: '85%' }}></div>
                </div>
                <span>85%</span>
              </div>
            </div>
            <div className="landing__feature-card">
              <ShoppingCart size={24} />
              <h3>Smart Groceries</h3>
              <p>Auto-generated shopping lists that sync with local stores for zero-waste nutritional management.</p>
            </div>
          </div>
        </section>

        {/* --- Concierge Section --- */}
        <section className="landing__concierge">
          <div className="landing__concierge-content">
            <MessageSquare size={24} className="landing__concierge-icon" />
            <h3>The Mealimizer Concierge</h3>
            <p>Real-time nutritional advice via our neural chat interface. Ask about meal choices, prep shortcuts, or metabolic science.</p>
          </div>
        </section>

        {/* --- Final CTA --- */}
        <section className="landing__final-cta">
          <h2>Ready to Engineer Your Evolution?</h2>
          <Link to="/register" className="btn-primary">Get Started</Link>
          <p className="landing__final-sub">
            Join 10,000+ high-performers optimizing their biologic potential.
          </p>
        </section>

        {/* --- Footer --- */}
        <footer className="landing__footer">
          <span className="landing__footer-brand">Mealimizer</span>
          <div className="landing__footer-links">
            <a href="#">Privacy</a>
            <a href="#">Terms</a>
            <a href="#">Intelligence</a>
          </div>
          <p className="landing__footer-copy">
            &copy; 2024 Obsidian Nutrition Systems. All rights reserved.
          </p>
        </footer>
      </div>
    );
  }

  /* ============ AUTHENTICATED HOME ============ */
  /* Dynamic greeting with user's first name */
  const firstName = user?.first_name || 'User';

  const [nutritionData, setNutritionData] = useState({
    yesterdayCal: '0',
    targetCal: '2000',
    currentCal: '0',
    fuelingPercent: 0,
    weight: '0',
    weightChange: '0 kg this week',
    weightGoal: '0 kg',
  });

  const [recentEntries, setRecentEntries] = useState([
    { name: 'Logging System Pending', time: '--:--', kcal: 0, tag: 'N/A', tagColor: '#3838ff' },
  ]);

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
            const percent = data.calorie_target > 0 ? Math.round((data.calories_consumed / data.calorie_target) * 100) : 0;
            setNutritionData({
              yesterdayCal: 'N/A', // Endpoint doesn't return yesterday
              targetCal: data.calorie_target,
              currentCal: data.calories_consumed,
              fuelingPercent: percent > 100 ? 100 : percent,
              weight: '-',
              weightChange: 'N/A',
              weightGoal: '-'
            });
          }
        })
        .catch(err => console.error("Failed to fetch logs summary", err));
    }
  }, [token]);

  return (
    <div className="home">
      {/* Personalized welcome header */}
      <section className="home__welcome">
        <h1 className="home__greeting">
          Welcome, <em>{firstName}</em>
        </h1>
        <p className="home__subtitle">
          Your architectural meal plan for today is ready. You are currently{' '}
          <span className="home__highlight">1.2kg ahead</span> of your weekly projection.
        </p>
      </section>

      {/* Stats row: Calorie intake + Body mass */}
      <section className="home__stats-row">
        {/* Calorie Intake Card */}
        <div className="home__calorie-card card">
          <span className="label-ui">Calorie Intake</span>
          <h3 className="home__card-title">Daily Architecture</h3>
          <div className="home__calorie-boxes">
            <div className="home__cal-box">
              <span className="home__cal-label">Yesterday</span>
              <strong>{nutritionData.yesterdayCal}</strong>
              <span className="home__cal-unit">kcal</span>
            </div>
            <div className="home__cal-box home__cal-box--target">
              <span className="home__cal-label">Target</span>
              <strong>{nutritionData.targetCal}</strong>
              <span className="home__cal-unit">kcal</span>
            </div>
          </div>
          {/* Circular progress indicator */}
          <div className="home__fueling">
            <svg viewBox="0 0 120 120" className="home__fueling-ring">
              <circle cx="60" cy="60" r="50" fill="none" stroke="var(--color-surface-3)" strokeWidth="8" />
              <circle
                cx="60" cy="60" r="50" fill="none"
                stroke="var(--color-primary)"
                strokeWidth="8"
                strokeLinecap="round"
                strokeDasharray={`${nutritionData.fuelingPercent * 3.14} 314`}
                transform="rotate(-90 60 60)"
              />
              <text x="60" y="55" textAnchor="middle" fill="var(--color-text)" fontFamily="var(--font-ui)" fontSize="22" fontWeight="700">
                {nutritionData.fuelingPercent}%
              </text>
              <text x="60" y="72" textAnchor="middle" fill="var(--color-text-muted)" fontFamily="var(--font-ui)" fontSize="8" letterSpacing="2">
                FUELING
              </text>
            </svg>
          </div>
          {/* Progress bar */}
          <div className="home__progress-section">
            <span className="home__progress-label heading-ui" style={{ fontSize: '11px' }}>Today's Progress</span>
            <div className="home__progress-bar">
              <div
                className="home__progress-fill"
                style={{ width: `${nutritionData.fuelingPercent}%` }}
              />
            </div>
            <span className="home__progress-text">
              <span className="home__highlight">{nutritionData.currentCal}</span> / {nutritionData.targetCal} kcal
            </span>
          </div>
        </div>

        {/* Body Mass Card */}
        <div className="home__weight-card card">
          <div className="home__weight-header">
            <div>
              <span className="label-ui">Body Mass</span>
              <h3 className="home__card-title">Current Weight</h3>
            </div>
            <TrendingDown size={20} className="home__weight-icon" />
          </div>
          <div className="home__weight-value">
            {nutritionData.weight}<span className="home__weight-unit">kg</span>
          </div>
          <div className="home__weight-change">
            <ChevronDown size={14} />
            <span>{nutritionData.weightChange}</span>
            <br />
            <span className="home__weight-goal">On track for goal: {nutritionData.weightGoal}</span>
          </div>
        </div>
      </section>

      {/* Recent Logged Entries */}
      <section className="home__entries">
        <div className="home__entries-header">
          <div>
            <span className="label-ui">Neural Logs</span>
            <h3>Last Logged Entries</h3>
          </div>
          <button className="btn-ghost" style={{ padding: '8px 16px', fontSize: '11px' }}>View AI History</button>
        </div>
        <div className="home__entries-list">
          {recentEntries.map((entry, i) => (
            <div key={i} className="home__entry-item">
              <div className="home__entry-thumb">
                <Flame size={18} />
              </div>
              <div className="home__entry-info">
                <strong>{entry.name}</strong>
                <span>
                  <span className="home__entry-dot">●</span> {entry.time}
                  <span className="home__entry-dot">●</span> {entry.kcal} kcal
                  <span className="home__entry-tag" style={{ backgroundColor: entry.tagColor }}>{entry.tag}</span>
                </span>
              </div>
              <div className="home__entry-actions">
                <button aria-label="Adjust"><SlidersHorizontal size={16} /></button>
                <button aria-label="Delete"><Trash2 size={16} /></button>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/*Log CTA */}
      <section className="home__scan-cta">
        <div className="home__scan-text">
          <h2>Ready to Architect your next meal?</h2>
          <p>Our AI can analyze a photo of your fridge or a restaurant menu to calculate the perfect portion size for your goals.</p>
        </div>
        <button className="btn-primary home__scan-btn">
          Log Meal
        </button>
      </section>
    </div>
  );
}
