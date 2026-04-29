/**
 * ProfileDropdown.jsx — User profile dropdown menu
 * 
 * Opens on CLICK (not hover) as per requirements.
 * Displays user info, navigation links, theme toggle, and logout.
 * Closes when clicking outside (useEffect click listener).
 * Falls back gracefully when user is not logged in.
 */

import { useState, useRef, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { User, Settings, LogOut } from 'lucide-react';
import ThemeToggle from './ThemeToggle';
import default_user from '../assets/default-user.jpg';

export default function ProfileDropdown() {
  const [open, setOpen] = useState(false);
  const dropdownRef = useRef(null);
  const navigate = useNavigate();

  /* Parse user from localStorage with safe fallback */
  const user = (() => {
    try {
      return JSON.parse(localStorage.getItem('user')) || null;
    } catch {
      return null;
    }
  })();

  /* Get profile image from localStorage, fall back to default */
  const [profileImage, setProfileImage] = useState(() => {
    const saved = localStorage.getItem('profileImage');
    return saved && saved !== 'null' ? saved : default_user;
  });

  useEffect(() => {
    const handleProfileUpdate = () => {
      const saved = localStorage.getItem('profileImage');
      setProfileImage(saved && saved !== 'null' ? saved : default_user);
    };

    window.addEventListener('profileImageUpdated', handleProfileUpdate);
    return () => window.removeEventListener('profileImageUpdated', handleProfileUpdate);
  }, []);

  /**
   * Close dropdown when clicking outside of it.
   * Uses mousedown to catch clicks before they propagate.
   */
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  /* Logout clears auth data and redirects */
  const handleLogout = () => {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('user');
    setOpen(false);
    navigate('/login');
  };

  return (
    <div className="profile-dropdown" ref={dropdownRef}>
      {/* Avatar button — opens dropdown on click */}
      <button
        className="profile-dropdown__trigger"
        onClick={() => setOpen(!open)}
        aria-label="Open profile menu"
      >
        <img
          src={profileImage}
          alt="Profile"
          className="profile-dropdown__avatar"
          onError={(e) => { e.target.src = default_user; }}
        />
      </button>

      {/* Dropdown panel — animated with CSS */}
      {open && (
        <div className="profile-dropdown__menu">
          {/* User info header */}
          {user && (
            <div className="profile-dropdown__header">
              <span className="profile-dropdown__name">
                {user.first_name} {user.last_name}
              </span>
              <span className="profile-dropdown__email">
                {user.email}
              </span>
            </div>
          )}

          {/* Nav links */}
          <Link
            to="/profile"
            className="profile-dropdown__item"
            onClick={() => setOpen(false)}
          >
            <User size={16} />
            My Profile
          </Link>
          <Link
            to="/profile"
            className="profile-dropdown__item"
            onClick={() => setOpen(false)}
          >
            <Settings size={16} />
            Settings
          </Link>

          {/* Theme toggle row */}
          <div className="profile-dropdown__item profile-dropdown__theme-row">
            <span>Appearance</span>
            <ThemeToggle />
          </div>

          {/* Logout */}
          <button
            className="profile-dropdown__logout"
            onClick={handleLogout}
          >
            <LogOut size={16} />
            Logout
          </button>
        </div>
      )}
    </div>
  );
}
