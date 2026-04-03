/**
 * App.jsx — Root application component
 * 
 * Routing setup:
 * - Authenticated pages (/, /dashboard, /chat, /profile) are wrapped 
 *   in AppLayout for consistent sidebar + navbar
 * - Auth pages (/login, /register) use standalone layouts (no sidebar)
 * 
 * The AppLayout wrapper is what ensures sidebar consistency across
 * all authenticated pages — a single Sidebar component instance.
 */

import { BrowserRouter, Routes, Route } from 'react-router-dom';
import AppLayout from './components/AppLayout';
import Home from './pages/Home';
import Login from './pages/Login';
import Chat from './pages/Chat';
import Dashboard from './pages/Dashboard';
import Profile from './pages/Profile';
import Register from './pages/Register';

function App() {
  /**
   * Check if user is authenticated — determines whether
   * to show the AppLayout (sidebar + navbar) or standalone pages.
   */
  const token = localStorage.getItem('accessToken');

  return (
    <BrowserRouter>
      <Routes>
        {/* ====== Auth Pages (standalone, no sidebar) ====== */}
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />

        {/* ====== Authenticated Pages (with AppLayout) ====== */}
        {/* Home page: shows landing if guest, dashboard-like if logged in */}
        <Route
          path="/"
          element={
            token ? (
              <AppLayout pageTitle="">
                <Home />
              </AppLayout>
            ) : (
              <Home />
            )
          }
        />

        <Route
          path="/dashboard"
          element={
            <AppLayout pageTitle="Dashboard">
              <Dashboard />
            </AppLayout>
          }
        />

        <Route
          path="/chat"
          element={
            <AppLayout pageTitle="">
              <Chat />
            </AppLayout>
          }
        />

        <Route
          path="/profile"
          element={
            <AppLayout pageTitle="">
              <Profile />
            </AppLayout>
          }
        />
      </Routes>
    </BrowserRouter>
  );
}

export default App;