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

import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  User, SlidersHorizontal, Palette, Shield, CreditCard,
  Bell, Sparkles, Moon, Sun, Monitor, AlertTriangle, Pencil, Save, X
} from 'lucide-react';
import default_user from '../assets/default-user.jpg';
import './Profile.css';
import Cropper from 'react-easy-crop';

const createImage = (url) =>
  new Promise((resolve, reject) => {
    const image = new Image();
    image.addEventListener('load', () => resolve(image));
    image.addEventListener('error', (error) => reject(error));
    image.setAttribute('crossOrigin', 'anonymous');
    image.src = url;
  });

const getCroppedImgBase64 = async (imageSrc, pixelCrop) => {
  const image = await createImage(imageSrc);
  const canvas = document.createElement('canvas');
  const ctx = canvas.getContext('2d');

  if (!ctx) return null;

  canvas.width = 250;
  canvas.height = 250;

  ctx.drawImage(
    image,
    pixelCrop.x,
    pixelCrop.y,
    pixelCrop.width,
    pixelCrop.height,
    0,
    0,
    250,
    250
  );

  return canvas.toDataURL('image/jpeg', 0.8);
};

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
  const [profileImage, setProfileImage] = useState(() => {
    const saved = localStorage.getItem('profileImage');
    return saved && saved !== 'null' ? saved : default_user;
  });

  /* Cropper State */
  const [imageSrc, setImageSrc] = useState(null);
  const [crop, setCrop] = useState({ x: 0, y: 0 });
  const [zoom, setZoom] = useState(1);
  const [croppedAreaPixels, setCroppedAreaPixels] = useState(null);
  const [showCropModal, setShowCropModal] = useState(false);

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
  const [bioSaving, setBioSaving] = useState(false);

  /* Toggle states for Smart Alerts */
  const [mealReminders, setMealReminders] = useState(true);
  const [aiUpdates, setAiUpdates] = useState(true);

  /* Dietary Focus tags */
  const [dietaryTags, setDietaryTags] = useState(() => {
    const saved = localStorage.getItem('dietaryTags');
    return saved ? JSON.parse(saved) : [];
  });
  const [showTagModal, setShowTagModal] = useState(false);
  const [newTagInput, setNewTagInput] = useState('');

  /* System Aesthetics */
  const [selectedTheme, setSelectedTheme] = useState('obsidian');

  /* Glassmorphism and ambient glow toggles */
  const [glassmorphism, setGlassmorphism] = useState(true);
  const [ambientGlow, setAmbientGlow] = useState(true);

  /* Preferences State */
  const [targetKcal, setTargetKcal] = useState('2000');
  const [targetProtein, setTargetProtein] = useState('');
  const [targetCarbs, setTargetCarbs] = useState('');
  const [targetFats, setTargetFats] = useState('');
  const [weightGoal, setWeightGoal] = useState('');
  const [currentWeight, setCurrentWeight] = useState('');
  const [targetKcalSaving, setTargetKcalSaving] = useState(false);
  const [targetProteinSaving, setTargetProteinSaving] = useState(false);
  const [targetCarbsSaving, setTargetCarbsSaving] = useState(false);
  const [targetFatsSaving, setTargetFatsSaving] = useState(false);
  const [weightGoalSaving, setWeightGoalSaving] = useState(false);
  const [currentWeightSaving, setCurrentWeightSaving] = useState(false);
  const [saveAllSaving, setSaveAllSaving] = useState(false);
  const [preferencesMessage, setPreferencesMessage] = useState('');
  const [preferencesMessageType, setPreferencesMessageType] = useState('success');

  /* Danger Zone State */
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [deletePassword, setDeletePassword] = useState('');
  const [deleteError, setDeleteError] = useState('');
  const [isDeleting, setIsDeleting] = useState(false);
  const [isClearing, setIsClearing] = useState(false);

  const navigate = useNavigate();

  /* Fetch initial user profile on mount */
  useEffect(() => {
    const token = localStorage.getItem('accessToken');
    if (!token) return;
    fetch('http://localhost:8000/user/me', {
      headers: { Authorization: `Bearer ${token}` }
    })
      .then(res => res.json())
      .then(data => {
        if (data.daily_calorie_target) {
          setTargetKcal(String(data.daily_calorie_target));
        }
        if (data.daily_protein_target) {
          setTargetProtein(String(data.daily_protein_target));
        }
        if (data.daily_carbs_target) {
          setTargetCarbs(String(data.daily_carbs_target));
        }
        if (data.daily_fats_target) {
          setTargetFats(String(data.daily_fats_target));
        }
        if (data.weight_goal) {
          setWeightGoal(String(data.weight_goal));
        }
        if (data.current_weight) {
          setCurrentWeight(String(data.current_weight));
        }
      })
      .catch(err => console.error('Failed to fetch profile', err));
  }, []);

  /* --- Image Cropper Handlers --- */
  const onFileChange = async (e) => {
    if (e.target.files && e.target.files.length > 0) {
      const file = e.target.files[0];
      const imageDataUrl = await new Promise((resolve) => {
        const reader = new FileReader();
        reader.addEventListener('load', () => resolve(reader.result), false);
        reader.readAsDataURL(file);
      });
      setImageSrc(imageDataUrl);
      setShowCropModal(true);
    }
  };

  const onCropComplete = (croppedArea, croppedAreaPixels) => {
    setCroppedAreaPixels(croppedAreaPixels);
  };

  const handleSaveCrop = async () => {
    try {
      const croppedImage = await getCroppedImgBase64(imageSrc, croppedAreaPixels);
      setProfileImage(croppedImage);
      localStorage.setItem('profileImage', croppedImage);
      setShowCropModal(false);
      setImageSrc(null);
      window.dispatchEvent(new Event('profileImageUpdated'));
    } catch (e) {
      console.error(e);
      alert('Failed to crop image.');
    }
  };

  const handleSaveProfile = () => {
    setBioSaving(true);
    setTimeout(() => {
      try {
        const userData = JSON.parse(localStorage.getItem('user')) || {};
        userData.bio = bio;
        localStorage.setItem('user', JSON.stringify(userData));
      } catch (e) {
        console.error('Failed to save bio locally', e);
      }
      setBioSaving(false);
      // Optional: alert or toast message
    }, 500);
  };

  const handleAddTag = () => {
    if (!newTagInput.trim()) return;
    const updated = [...dietaryTags, newTagInput.trim()];
    setDietaryTags(updated);
    localStorage.setItem('dietaryTags', JSON.stringify(updated));
    setNewTagInput('');
    setShowTagModal(false);
  };

  const handleSaveField = async (field, value, setSaving) => {
    const token = localStorage.getItem('accessToken');
    if (!token) {
      navigate('/login');
      return;
    }
    setSaving(true);
    setPreferencesMessage('');

    let numVal;
    if (value === '' || isNaN(Number(value))) {
      setPreferencesMessage('Please enter a valid number.');
      setPreferencesMessageType('error');
      setSaving(false);
      return;
    }
    numVal = Number(value);

    const payload = {};
    payload[field] = numVal;

    try {
      const res = await fetch('http://localhost:8000/user/me/preferences', {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify(payload)
      });
      if (res.status === 401 || res.status === 403) {
        localStorage.removeItem('accessToken');
        setPreferencesMessage('Session expired. Redirecting to login...');
        setPreferencesMessageType('error');
        setTimeout(() => navigate('/login'), 1200);
        setSaving(false);
        return;
      }
      if (res.ok) {
        let fieldName = 'Preference';
        if (field === 'daily_calorie_target') fieldName = 'Calorie Target';
        if (field === 'daily_protein_target') fieldName = 'Protein Target';
        if (field === 'daily_carbs_target') fieldName = 'Carbs Target';
        if (field === 'daily_fats_target') fieldName = 'Fats Target';
        if (field === 'weight_goal') fieldName = 'Weight Goal';
        if (field === 'current_weight') fieldName = 'Current Weight';
        setPreferencesMessage(`${fieldName} saved successfully.`);
        setPreferencesMessageType('success');
      } else {
        const errData = await res.json().catch(() => ({}));
        setPreferencesMessage(errData.detail || 'Failed to save preference.');
        setPreferencesMessageType('error');
      }
    } catch (e) {
      console.error(e);
      setPreferencesMessage('Network error. Is the backend running?');
      setPreferencesMessageType('error');
    }
    setSaving(false);
  };

  /* Save All preferences in a single PATCH request */
  const handleSaveAll = async () => {
    const token = localStorage.getItem('accessToken');
    if (!token) {
      navigate('/login');
      return;
    }
    setSaveAllSaving(true);
    setPreferencesMessage('');

    // Validate all fields
    const fields = [
      { key: 'daily_calorie_target', value: targetKcal, label: 'Calorie Target' },
      { key: 'daily_protein_target', value: targetProtein, label: 'Protein Target' },
      { key: 'daily_carbs_target', value: targetCarbs, label: 'Carbs Target' },
      { key: 'daily_fats_target', value: targetFats, label: 'Fats Target' },
      { key: 'current_weight', value: currentWeight, label: 'Current Weight' },
      { key: 'weight_goal', value: weightGoal, label: 'Weight Goal' },
    ];

    const payload = {};
    for (const f of fields) {
      if (f.value !== '' && !isNaN(Number(f.value))) {
        payload[f.key] = Number(f.value);
      }
    }

    if (Object.keys(payload).length === 0) {
      setPreferencesMessage('No valid values to save.');
      setPreferencesMessageType('error');
      setSaveAllSaving(false);
      return;
    }

    try {
      const res = await fetch('http://localhost:8000/user/me/preferences', {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify(payload)
      });
      if (res.status === 401 || res.status === 403) {
        localStorage.removeItem('accessToken');
        setPreferencesMessage('Session expired. Redirecting to login...');
        setPreferencesMessageType('error');
        setTimeout(() => navigate('/login'), 1200);
        setSaveAllSaving(false);
        return;
      }
      if (res.ok) {
        setPreferencesMessage('All preferences saved successfully.');
        setPreferencesMessageType('success');
      } else {
        const errData = await res.json().catch(() => ({}));
        setPreferencesMessage(errData.detail || 'Failed to save preferences.');
        setPreferencesMessageType('error');
      }
    } catch (e) {
      console.error(e);
      setPreferencesMessage('Network error. Is the backend running?');
      setPreferencesMessageType('error');
    }
    setSaveAllSaving(false);
    setSaveAllSaving(false);
  };

  /* ---- Danger Zone Handlers ---- */
  const handleClearData = async () => {
    const token = localStorage.getItem('accessToken');
    if (!token) return;
    if (!window.confirm('Are you sure you want to clear all your AI data and logs? This cannot be undone.')) return;

    setIsClearing(true);
    try {
      const res = await fetch('http://localhost:8000/user/me/clear-data', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      if (res.ok) {
        alert('AI data and logs cleared successfully.');
        window.location.reload();
      } else {
        alert('Failed to clear data.');
      }
    } catch (err) {
      console.error(err);
      alert('Error clearing data.');
    } finally {
      setIsClearing(false);
    }
  };

  const handleDeleteAccount = async () => {
    setDeleteError('');
    if (!deletePassword) {
      setDeleteError('Please enter your password.');
      return;
    }

    const token = localStorage.getItem('accessToken');
    if (!token) return;

    setIsDeleting(true);
    try {
      const res = await fetch('http://localhost:8000/user/me/delete-account', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ password: deletePassword })
      });

      if (res.ok) {
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        navigate('/login');
      } else {
        setDeleteError('password does not match');
      }
    } catch (err) {
      console.error(err);
      setDeleteError('Error deleting account.');
    } finally {
      setIsDeleting(false);
    }
  };

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
              <div className="settings__section-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <h2>User Profile</h2>
                <button
                  className="settings__profile-save-btn"
                  onClick={handleSaveProfile}
                  disabled={bioSaving}
                >
                  {bioSaving ? 'Saving...' : 'Save changes'}
                </button>
              </div>

              {/* Profile image + form fields */}
              <div className="settings__profile-form">
                <div className="settings__avatar-section">
                  <div
                    className="settings__avatar-wrap"
                    onClick={() => document.getElementById('profileImgUpload').click()}
                    style={{ cursor: 'pointer' }}
                  >
                    <input
                      type="file"
                      id="profileImgUpload"
                      accept="image/*"
                      style={{ display: 'none' }}
                      onChange={onFileChange}
                    />
                    <img
                      src={profileImage}
                      alt="Profile"
                      className="settings__avatar"
                      onError={(e) => { e.target.src = default_user; }}
                    />
                    <button className="settings__avatar-edit" aria-label="Edit avatar" onClick={(e) => e.preventDefault()}>
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
                      disabled
                      style={{ opacity: 0.6, cursor: 'not-allowed' }}
                    />
                  </div>
                  <div className="settings__field">
                    <label className="label-ui">Email Address</label>
                    <input
                      type="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      disabled
                      style={{ opacity: 0.6, cursor: 'not-allowed' }}
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
                  <button className="settings__tag settings__tag--add" onClick={() => setShowTagModal(true)}>+ Add Goal</button>
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

          {/* ======= PREFERENCES TAB ======= */}
          {activeTab === 'preferences' && (
            <div className="settings__section">
              <div className="settings__section-header">
                <h2>Preferences</h2>
                <button
                  className="btn-primary settings__save-all-btn"
                  onClick={handleSaveAll}
                  disabled={saveAllSaving}
                >
                  <Save size={14} />
                  {saveAllSaving ? 'Saving...' : 'Save All'}
                </button>
              </div>

              {preferencesMessage && (
                <div className={`settings__pref-message ${preferencesMessageType === 'error' ? 'settings__pref-message--error' : 'settings__pref-message--success'}`}>
                  {preferencesMessage}
                </div>
              )}

              <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
                <div className="settings__field">
                  <label className="label-ui">Daily Calorie Target (kcal)</label>
                  <div style={{ display: 'flex', gap: '8px' }}>
                    <input
                      type="text"
                      value={targetKcal}
                      onChange={(e) => setTargetKcal(e.target.value)}
                    />
                    <button
                      className="btn-ghost"
                      onClick={() => handleSaveField('daily_calorie_target', targetKcal, setTargetKcalSaving)}
                      disabled={targetKcalSaving}
                    >
                      {targetKcalSaving ? 'Saving...' : 'Save'}
                    </button>
                  </div>
                </div>
                <div className="settings__field">
                  <label className="label-ui">Protein Target (g)</label>
                  <div style={{ display: 'flex', gap: '8px' }}>
                    <input
                      type="text"
                      value={targetProtein}
                      onChange={(e) => setTargetProtein(e.target.value)}
                    />
                    <button
                      className="btn-ghost"
                      onClick={() => handleSaveField('daily_protein_target', targetProtein, setTargetProteinSaving)}
                      disabled={targetProteinSaving}
                    >
                      {targetProteinSaving ? 'Saving...' : 'Save'}
                    </button>
                  </div>
                </div>
                <div className="settings__field">
                  <label className="label-ui">Carbs Target (g)</label>
                  <div style={{ display: 'flex', gap: '8px' }}>
                    <input
                      type="text"
                      value={targetCarbs}
                      onChange={(e) => setTargetCarbs(e.target.value)}
                    />
                    <button
                      className="btn-ghost"
                      onClick={() => handleSaveField('daily_carbs_target', targetCarbs, setTargetCarbsSaving)}
                      disabled={targetCarbsSaving}
                    >
                      {targetCarbsSaving ? 'Saving...' : 'Save'}
                    </button>
                  </div>
                </div>
                <div className="settings__field">
                  <label className="label-ui">Fats Target (g)</label>
                  <div style={{ display: 'flex', gap: '8px' }}>
                    <input
                      type="text"
                      value={targetFats}
                      onChange={(e) => setTargetFats(e.target.value)}
                    />
                    <button
                      className="btn-ghost"
                      onClick={() => handleSaveField('daily_fats_target', targetFats, setTargetFatsSaving)}
                      disabled={targetFatsSaving}
                    >
                      {targetFatsSaving ? 'Saving...' : 'Save'}
                    </button>
                  </div>
                </div>
                <div className="settings__field">
                  <label className="label-ui">Current Weight (kg)</label>
                  <div style={{ display: 'flex', gap: '8px' }}>
                    <input
                      type="text"
                      value={currentWeight}
                      onChange={(e) => setCurrentWeight(e.target.value)}
                    />
                    <button
                      className="btn-ghost"
                      onClick={() => handleSaveField('current_weight', currentWeight, setCurrentWeightSaving)}
                      disabled={currentWeightSaving}
                    >
                      {currentWeightSaving ? 'Saving...' : 'Save'}
                    </button>
                  </div>
                </div>
                <div className="settings__field">
                  <label className="label-ui">Weight Goal (kg)</label>
                  <div style={{ display: 'flex', gap: '8px' }}>
                    <input
                      type="text"
                      value={weightGoal}
                      onChange={(e) => setWeightGoal(e.target.value)}
                    />
                    <button
                      className="btn-ghost"
                      onClick={() => handleSaveField('weight_goal', weightGoal, setWeightGoalSaving)}
                      disabled={weightGoalSaving}
                    >
                      {weightGoalSaving ? 'Saving...' : 'Save'}
                    </button>
                  </div>
                </div>
              </div>
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
              <button
                className="settings__danger-btn settings__danger-btn--ghost"
                onClick={handleClearData}
                disabled={isClearing}
              >
                {isClearing ? 'Clearing...' : 'Clear AI Data'}
              </button>
              <button
                className="settings__danger-btn settings__danger-btn--destructive"
                onClick={() => {
                  setDeletePassword('');
                  setDeleteError('');
                  setShowDeleteModal(true);
                }}
              >
                Delete Account
              </button>
            </div>
          </div>

          {/* Delete Account Modal */}
          {showDeleteModal && (
            <div className="dashboard__modal-overlay" onClick={() => setShowDeleteModal(false)}>
              <div className="dashboard__modal" onClick={(e) => e.stopPropagation()} style={{ maxWidth: '480px' }}>
                <div className="dashboard__modal-header" style={{ borderBottom: 'none', justifyContent: 'center', position: 'relative' }}>
                  <h3 style={{ color: 'var(--color-danger)' }}>Confirm Account Deletion</h3>
                  <button className="dashboard__modal-close" onClick={() => setShowDeleteModal(false)} aria-label="Close" style={{ position: 'absolute', right: '0' }}>
                    <X size={18} />
                  </button>
                </div>
                <div style={{ padding: '20px 0' }}>
                  <p style={{ margin: '16px', color: 'var(--color-text)', textAlign: 'center' }}>
                    To confirm deletion, please enter your password. This action cannot be undone.
                  </p>
                  <input
                    type="password"
                    placeholder="Enter your password"
                    value={deletePassword}
                    onChange={(e) => setDeletePassword(e.target.value)}
                    style={{
                      width: '90%',
                      padding: '20px',
                      background: 'var(--color-surface)',
                      border: 'none',
                      color: 'var(--color-text)',
                      borderRadius: '4px'
                    }}
                  />
                  {deleteError && (
                    <p style={{ color: 'var(--color-danger)', marginTop: '8px', fontSize: '14px' }}>
                      {deleteError}
                    </p>
                  )}
                </div>
                <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end' }}>
                  <button
                    className="btn-ghost"
                    onClick={() => setShowDeleteModal(false)}
                    disabled={isDeleting}
                  >
                    Cancel
                  </button>
                  <button
                    className="settings__danger-btn settings__danger-btn--destructive"
                    onClick={handleDeleteAccount}
                    disabled={isDeleting}
                  >
                    {isDeleting ? 'Deleting...' : 'Delete'}
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Dietary Focus Modal */}
          {showTagModal && (
            <div className="dashboard__modal-overlay" style={{ backdropFilter: 'blur(5px)' }} onClick={() => setShowTagModal(false)}>
              <div className="dashboard__modal" onClick={(e) => e.stopPropagation()} style={{ maxWidth: '400px', position: 'relative' }}>
                <div className="dashboard__modal-header" style={{ borderBottom: 'none' }}>
                  <h3 style={{ margin: 0, color: 'var(--color-text)' }}>Add Dietary Focus</h3>
                </div>
                <div style={{ padding: '20px 0', display: 'flex', justifyContent: 'center' }}>
                  <button className="dashboard__modal-close" onClick={() => setShowTagModal(false)} aria-label="Close" style={{ position: 'absolute', right: '20px', top: '20px' }}>
                    <X size={18} />
                  </button>
                  <input
                    type="text"
                    placeholder="Enter your dietary focus"
                    value={newTagInput}
                    onChange={(e) => setNewTagInput(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleAddTag()}
                    style={{
                      width: '90%',
                      padding: '10px',
                      background: 'var(--color-surface)',
                      border: 'none',
                      color: 'var(--color-text)',
                      borderRadius: '4px',
                      fontFamily: 'var(--font-body)'
                    }}
                    autoFocus
                  />
                </div>
                <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end', margin: '0px 10px 10px 10px' }}>
                  <button className="settings__profile-save-btn" onClick={handleAddTag}>Add</button>
                </div>
              </div>
            </div>
          )}

          {/* Cropper Modal */}
          {showCropModal && (
            <div className="dashboard__modal-overlay" onClick={() => setShowCropModal(false)}>
              <div className="dashboard__modal" onClick={(e) => e.stopPropagation()} style={{ maxWidth: '400px', padding: 0, overflow: 'hidden' }}>
                <div className="dashboard__modal-header" style={{ borderBottom: 'none', position: 'relative', zIndex: 10, padding: '20px' }}>
                  <h3 style={{ margin: 0, color: 'var(--color-text)' }}>Adjust Profile Picture</h3>
                  <button className="dashboard__modal-close" onClick={() => setShowCropModal(false)} aria-label="Close" style={{ position: 'absolute', right: '20px', top: '20px' }}>
                    <X size={18} />
                  </button>
                </div>
                <div style={{ position: 'relative', width: '100%', height: '300px', backgroundColor: '#333' }}>
                  <Cropper
                    image={imageSrc}
                    crop={crop}
                    zoom={zoom}
                    aspect={1}
                    cropShape="round"
                    showGrid={false}
                    onCropChange={setCrop}
                    onCropComplete={onCropComplete}
                    onZoomChange={setZoom}
                  />
                </div>
                <div style={{ padding: '20px', display: 'flex', gap: '10px', justifyContent: 'flex-end', background: 'var(--color-surface)' }}>
                  <button className="btn-ghost" onClick={() => setShowCropModal(false)}>Cancel</button>
                  <button className="settings__danger-btn" style={{ background: 'var(--color-primary)', color: 'white' }} onClick={handleSaveCrop}>Save Picture</button>
                </div>
              </div>
            </div>
          )}

          {/* Footer */}
          <footer className="settings__footer label-ui">
            Mealimizer AI System v2.4.8 · Obsidian Build
          </footer>
        </div>
      </div>
    </div>
  );
}