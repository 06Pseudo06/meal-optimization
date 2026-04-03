/**
 * Navbar.jsx — Top navigation bar
 * 
 * Displayed across all authenticated pages above the main content.
 * Contains: page title, search bar, notification bell, profile dropdown.
 * On mobile: shows hamburger button to toggle sidebar.
 */

import { Search, Bell, Menu } from 'lucide-react';
import ProfileDropdown from './ProfileDropdown';
import './Navbar.css';

export default function Navbar({ pageTitle, onToggleSidebar }) {
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
        <button className="navbar__icon-btn" aria-label="Notifications">
          <Bell size={20} />
          <span className="navbar__badge" />
        </button>
        <ProfileDropdown />
      </div>
    </header>
  );
}
