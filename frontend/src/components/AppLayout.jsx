/**
 * AppLayout.jsx — Layout wrapper for authenticated pages
 * 
 * Wraps every authenticated page (Home, Dashboard, Chat, Profile)
 * to provide consistent structure:
 *   - Sidebar (left, fixed)
 *   - Navbar (top, sticky)
 *   - Content area (scrollable, where page content renders)
 * 
 * Manages sidebar open/close state for mobile responsiveness.
 * This is the component that ensures sidebar consistency across pages.
 */

import { useState } from 'react';
import Sidebar from './Sidebar';
import Navbar from './Navbar';
import './AppLayout.css';

export default function AppLayout({ children, pageTitle }) {
  /* Sidebar open state — only relevant on mobile */
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="app-layout">
      {/* Sidebar — same instance across all pages */}
      <Sidebar
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
      />

      {/* Main content area (right of sidebar) */}
      <div className="app-layout__main">
        {/* Top navbar with search and profile */}
        <Navbar
          pageTitle={pageTitle}
          onToggleSidebar={() => setSidebarOpen(!sidebarOpen)}
        />

        {/* Page content — each page renders here */}
        <main className="app-layout__content">
          {children}
        </main>
      </div>
    </div>
  );
}
