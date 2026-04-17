/**
 * Navbar.jsx — Top navigation bar
 * 
 * Displayed across all authenticated pages above the main content.
 * Contains: page title, search bar, notification bell (with dropdown), profile dropdown.
 * On mobile: shows hamburger button to toggle sidebar.
 */

import { useState, useEffect, useRef } from 'react';
import { Search, Bell, Menu, X, Mail } from 'lucide-react';
import ProfileDropdown from './ProfileDropdown';
import './Navbar.css';

export default function Navbar({ pageTitle, onToggleSidebar }) {
  const [notifOpen, setNotifOpen] = useState(false);
  const notifRef = useRef(null);

  /* Mock notifications — empty array = "No Messages yet" */
  const [notifications] = useState([
    // Example populated notifications could look like:
    // { id: 1, title: 'Welcome!', body: 'Start by logging your first meal.', time: '2 min ago', read: false },
  ]);

  const unreadCount = notifications.filter((n) => !n.read).length;

  /* Close dropdown when clicking outside */
  useEffect(() => {
    function handleClickOutside(e) {
      if (notifRef.current && !notifRef.current.contains(e.target)) {
        setNotifOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <header className="navbar">
      {/* Left: hamburger (mobile) + page title */}
      <div className="navbar__left">
        <button
          className="navbar__hamburger"
          onClick={onToggleSidebar}
          aria-label="Toggle sidebar"
        >
          <Menu size={20} />
        </button>
        {pageTitle && <h1 className="navbar__title">{pageTitle}</h1>}
      </div>

      {/* Center: Search bar */}
      <div className="navbar__search">
        <Search size={16} />
        <input type="text" placeholder="Search nutrition or recipes..." />
      </div>

      {/* Right: Notifications + Profile */}
      <div className="navbar__right">
        {/* Notification Bell with Dropdown */}
        <div className="navbar__notif-wrapper" ref={notifRef}>
          <button
            className="navbar__icon-btn"
            aria-label="Notifications"
            onClick={() => setNotifOpen(!notifOpen)}
          >
            <Bell size={20} />
            {unreadCount > 0 && <span className="navbar__badge" />}
          </button>

          {/* Notification Dropdown Panel */}
          {notifOpen && (
            <div className="navbar__notif-dropdown">
              <div className="navbar__notif-header">
                <h4>Notifications</h4>
                <button
                  className="navbar__notif-close"
                  onClick={() => setNotifOpen(false)}
                  aria-label="Close notifications"
                >
                  <X size={14} />
                </button>
              </div>

              <div className="navbar__notif-list">
                {notifications.length === 0 ? (
                  <div className="navbar__notif-empty">
                    <Mail size={32} className="navbar__notif-empty-icon" />
                    <p className="navbar__notif-empty-text">No Messages yet</p>
                    <span className="navbar__notif-empty-sub">
                      You're all caught up! New notifications will appear here.
                    </span>
                  </div>
                ) : (
                  notifications.map((notif) => (
                    <div
                      key={notif.id}
                      className={`navbar__notif-item ${!notif.read ? 'navbar__notif-item--unread' : ''}`}
                    >
                      <div className="navbar__notif-dot" />
                      <div className="navbar__notif-content">
                        <strong>{notif.title}</strong>
                        <p>{notif.body}</p>
                        <span className="navbar__notif-time">{notif.time}</span>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}
        </div>

        <ProfileDropdown />
      </div>
    </header>
  );
}
