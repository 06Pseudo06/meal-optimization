/**
 * Sidebar.jsx — Reusable sidebar navigation component
 * 
 * Used across ALL authenticated pages (Home, Dashboard, Chat, Profile)
 * via the AppLayout wrapper. Provides consistent navigation with:
 * - Logo + brand title
 * - Navigation items with active state highlighting
 * - Pro Plan upgrade CTA
 * - Logout button
 * 
 * Collapses off-screen on mobile with hamburger toggle from Navbar.
 */

import { Link, useLocation, useNavigate } from 'react-router-dom';
import { Home, LayoutDashboard, MessageSquare, LogOut, Utensils } from 'lucide-react';
import './Sidebar.css';

export default function Sidebar({ isOpen, onClose }) {
  const location = useLocation();
  const navigate = useNavigate();

  /* Navigation items config — single source of truth for sidebar links */
  const navItems = [
    { path: '/',          label: 'Home',      icon: Home },
    { path: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { path: '/chat',      label: 'Chat',      icon: MessageSquare },
  ];

  /**
   * Logout handler — clears all auth data from localStorage
   * and redirects to login page. Preserves theme preference.
   */
  const handleLogout = () => {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('user');
    navigate('/login');
  };

  /**
   * Check if a nav item is currently active.
   * Matches exact path for Home ("/"), startsWith for others.
   */
  const isActive = (path) => {
    if (path === '/') return location.pathname === '/';
    return location.pathname.startsWith(path);
  };

  return (
    <>
      {/* Dark overlay behind sidebar on mobile */}
      <div
        className={`sidebar-overlay ${isOpen ? 'sidebar-overlay--visible' : ''}`}
        onClick={onClose}
      />

      <aside className={`sidebar ${isOpen ? 'sidebar--open' : ''}`}>
        {/* Brand Logo */}
        <div className="sidebar__logo">
          <div className="sidebar__logo-icon">
            <Utensils />
          </div>
          <div className="sidebar__logo-text">
            <span className="sidebar__logo-title">Mealimizer</span>
            <span className="sidebar__logo-subtitle">AI Nutrition</span>
          </div>
        </div>

        {/* Navigation Links */}
        <nav className="sidebar__nav">
          {navItems.map(({ path, label, icon: Icon }) => (
            <Link
              key={path}
              to={path}
              className={`sidebar__nav-item ${isActive(path) ? 'sidebar__nav-item--active' : ''}`}
              onClick={onClose}
            >
              <Icon />
              {label}
            </Link>
          ))}
        </nav>

        {/* Pro Plan Upgrade Card */}
        <div className="sidebar__pro">
          <div className="sidebar__pro-label">Pro Plan</div>
          <p className="sidebar__pro-text">
            Unlock advanced meal tracking and AI insights.
          </p>
          <button className="sidebar__pro-btn">Upgrade to Pro</button>
        </div>

        {/* Logout */}
        <button className="sidebar__logout" onClick={handleLogout}>
          <LogOut />
          Logout
        </button>
      </aside>
    </>
  );
}
