/**
 * Profile.jsx — System Settings / Profile page
 * 
 * Matching the Settings screenshot with:
 * - Sidebar tabs (Profile, Preferences, Appearance, Security, Billing)
 * - User Profile section with dynamic data from localStorage
 * - Smart Alerts toggles
 * - Dietary Focus tags
 * - System Aesthetics theme selector
 * - Danger Zone (clear data, delete account)
 * 
 * User data (name, email) is read from localStorage("user").
 * Profile image from localStorage("profileImage").
 */

import { useState } from 'react';
import {
  User, SlidersHorizontal, Palette, Shield, CreditCard,
  Bell, Sparkles, Moon, Sun, Monitor, AlertTriangle, Pencil
} from 'lucide-react';
import default_user from '../assets/default-user.jpg';
import './Profile.css';

export default function Profile() {
  /* Parse user from localStorage with safe fallback */
  const user = (() => {
    try {
      return JSON.parse(localStorage.getItem('user')) || {};
    } catch {
      return {};
    }
  })();

  /* Profile image from localStorage */
  const profileImage = (() => {
    const saved = localStorage.getItem('profileImage');
    return saved && saved !== 'null' ? saved : default_user;
  })();

  /* Active settings tab */
  const [activeTab, setActiveTab] = useState('profile');

  /* Form state — initialized from user data */
  const [fullName, setFullName] = useState(
    `${user.first_name || ''} ${user.last_name || ''}`.trim() || 'User'
  );
  const [email, setEmail] = useState(user.email || '');
  const [bio, setBio] = useState(
    user.bio || 'Tech entrepreneur with a focus on high-performance lifestyle and data-driven nutrition.'
  );

  /* Toggle states for Smart Alerts */
  const [mealReminders, setMealReminders] = useState(true);
  const [aiUpdates, setAiUpdates] = useState(true);

  /* Dietary Focus tags */
  const [dietaryTags] = useState(['Keto', 'Vegan', 'Intermittent Fasting', 'Paleo']);

  /* System Aesthetics */
  const [selectedTheme, setSelectedTheme] = useState('obsidian');

  /* Glassmorphism and ambient glow toggles */
  const [glassmorphism, setGlassmorphism] = useState(true);
  const [ambientGlow, setAmbientGlow] = useState(true);

  /* Settings tabs configuration */
  const tabs = [
    { id: 'profile', label: 'Profile', icon: User },
    { id: 'preferences', label: 'Preferences', icon: SlidersHorizontal },
    { id: 'appearance', label: 'Appearance', icon: Palette },
    { id: 'security', label: 'Security', icon: Shield },
    { id: 'billing', label: 'Billing', icon: CreditCard },
  ];

  /* Theme options */
  const themes = [
    { id: 'obsidian', label: 'Obsidian', desc: 'Default nocturnal theme.', icon: Moon, active: true },
    { id: 'clinical', label: 'Clinical', desc: 'High-contrast light mode.', icon: Sun, active: false },
    { id: 'system', label: 'System', desc: 'Sync with your device.', icon: Monitor, active: false },
  ];

  return (
    <div className="settings">
      {/* Page Header */}
      <div className="settings__header">
        <h1 className="settings__title heading-ui" style={{ fontSize: '24px', letterSpacing: '3px' }}>
          System Settings
        </h1>
        <p className="settings__subtitle">
          Configure your AI nutrition assistant and personal workspace.
        </p>
      </div>

      <div className="settings__layout">
        {/* Settings Sidebar Tabs */}
        <nav className="settings__tabs">
          {tabs.map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              className={`settings__tab ${activeTab === id ? 'settings__tab--active' : ''}`}
              onClick={() => setActiveTab(id)}
            >
              <Icon size={16} />
              {label}
            </button>
          ))}
        </nav>

        {/* Settings Content */}
        <div className="settings__content">
          {/* ======= PROFILE TAB ======= */}
          {activeTab === 'profile' && (
            <div className="settings__section">
              <div className="settings__section-header">
                <h2>User Profile</h2>
                <button className="btn-ghost" style={{ padding: '8px 16px', fontSize: '11px' }}>
                  Save Changes
                </button>
              </div>

              {/* Profile image + form fields */}
              <div className="settings__profile-form">
                <div className="settings__avatar-section">
                  <div className="settings__avatar-wrap">
                    <img
                      src={profileImage}
                      alt="Profile"
                      className="settings__avatar"
                      onError={(e) => { e.target.src = default_user; }}
                    />
                    <button className="settings__avatar-edit" aria-label="Edit avatar">
                      <Pencil size={12} />
                    </button>
                  </div>
                </div>

                <div className="settings__form-grid">
                  <div className="settings__field">
                    <label className="label-ui">Full Name</label>
                    <input
                      type="text"
                      value={fullName}
                      onChange={(e) => setFullName(e.target.value)}
                    />
                  </div>
                  <div className="settings__field">
                    <label className="label-ui">Email Address</label>
                    <input
                      type="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                    />
                  </div>
                </div>

                <div className="settings__field settings__field--full">
                  <label className="label-ui">Short Bio</label>
                  <textarea
                    value={bio}
                    onChange={(e) => setBio(e.target.value)}
                    rows={3}
                  />
                </div>
              </div>

              {/* Smart Alerts */}
              <div className="settings__card">
                <div className="settings__card-header">
                  <Bell size={18} className="settings__card-icon" />
                  <h3>Smart Alerts</h3>
                </div>
                <div className="settings__toggle-row">
                  <span>Meal reminders</span>
                  <button
                    className={`settings__toggle ${mealReminders ? 'settings__toggle--on' : ''}`}
                    onClick={() => setMealReminders(!mealReminders)}
                  >
                    <span className="settings__toggle-knob" />
                  </button>
                </div>
                <div className="settings__toggle-row">
                  <span>AI Analysis updates</span>
                  <button
                    className={`settings__toggle ${aiUpdates ? 'settings__toggle--on' : ''}`}
                    onClick={() => setAiUpdates(!aiUpdates)}
                  >
                    <span className="settings__toggle-knob" />
                  </button>
                </div>
              </div>

              {/* Dietary Focus */}
              <div className="settings__card">
                <div className="settings__card-header">
                  <Sparkles size={18} className="settings__card-icon" />
                  <h3>Dietary Focus</h3>
                </div>
                <div className="settings__tags">
                  {dietaryTags.map((tag, i) => (
                    <span key={i} className="settings__tag">{tag}</span>
                  ))}
                  <button className="settings__tag settings__tag--add">+ Add Goal</button>
                </div>
              </div>
            </div>
          )}

          {/* ======= APPEARANCE TAB ======= */}
          {activeTab === 'appearance' && (
            <div className="settings__section">
              <h2>System Aesthetics</h2>
              <div className="settings__themes">
                {themes.map((theme) => (
                  <button
                    key={theme.id}
                    className={`settings__theme-card ${selectedTheme === theme.id ? 'settings__theme-card--active' : ''}`}
                    onClick={() => setSelectedTheme(theme.id)}
                  >
                    <theme.icon size={24} />
                    <strong>{theme.label}</strong>
                    <span>{theme.desc}</span>
                  </button>
                ))}
              </div>

              <div className="settings__toggle-row" style={{ marginTop: '24px' }}>
                <div>
                  <strong>Dynamic Glassmorphism</strong>
                  <p className="settings__toggle-desc">Enable backdrop blur on interface elements.</p>
                </div>
                <button
                  className={`settings__toggle ${glassmorphism ? 'settings__toggle--on' : ''}`}
                  onClick={() => setGlassmorphism(!glassmorphism)}
                >
                  <span className="settings__toggle-knob" />
                </button>
              </div>

              <div className="settings__toggle-row">
                <div>
                  <strong>Ambient Glow</strong>
                  <p className="settings__toggle-desc">Visual highlights/shadows for active interactions.</p>
                </div>
                <button
                  className={`settings__toggle ${ambientGlow ? 'settings__toggle--on' : ''}`}
                  onClick={() => setAmbientGlow(!ambientGlow)}
                >
                  <span className="settings__toggle-knob" />
                </button>
              </div>
            </div>
          )}

          {/* ======= OTHER TABS (placeholder) ======= */}
          {activeTab === 'preferences' && (
            <div className="settings__section">
              <h2>Preferences</h2>
              <p className="settings__placeholder-text">Nutritional preferences and goal configuration coming soon.</p>
            </div>
          )}

          {activeTab === 'security' && (
            <div className="settings__section">
              <h2>Security</h2>
              <p className="settings__placeholder-text">Password change, 2FA, and session management coming soon.</p>
            </div>
          )}

          {activeTab === 'billing' && (
            <div className="settings__section">
              <h2>Billing</h2>
              <p className="settings__placeholder-text">Subscription management and payment history coming soon.</p>
            </div>
          )}

          {/* ======= DANGER ZONE (always visible) ======= */}
          <div className="settings__danger">
            <div className="settings__danger-header">
              <AlertTriangle size={18} />
              <h3>Danger Zone</h3>
            </div>
            <p>Once you delete your account or reset AI training data, there is no going back. Please be certain.</p>
            <div className="settings__danger-actions">
              <button className="settings__danger-btn settings__danger-btn--ghost">Clear AI Data</button>
              <button className="settings__danger-btn settings__danger-btn--destructive">Delete Account</button>
            </div>
          </div>

          {/* Footer */}
          <footer className="settings__footer label-ui">
            Mealimizer AI System v2.4.8 · Obsidian Build
          </footer>
        </div>
      </div>
    </div>
  );
}