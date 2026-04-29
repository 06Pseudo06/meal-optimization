/**
 * Login.jsx — User authentication login page
 * 
 * ⚠️ ALL EXISTING AUTH LOGIC IS PRESERVED:
 * - Password regex validation
 * - Remember me (localStorage)
 * - POST to http://localhost:8000/user/login
 * - Store accessToken + user in localStorage
 * - Redirect to "/" on success
 * 
 * Only the UI/styling has been updated to match the design system.
 * Uses Link components for SPA navigation instead of <a> tags.
 */

import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Eye, EyeOff } from 'lucide-react';
import './Login.css';
import AnimatedCharacters from '../components/AnimatedCharacters';

export default function Login() {
  /* Theme state — persisted to localStorage */
  const [dark, setDark] = useState(() => {
    return localStorage.getItem('theme') !== 'light';
  });

  /* Password validation regex — requires uppercase, lowercase, number, symbol, 8+ chars */
  const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{8,}$/;

  /* Form state */
  const [error, setError] = useState('');
  const [email, setEmail] = useState(() => localStorage.getItem('rememberedEmail') || '');
  const [remember, setRemember] = useState(() => !!localStorage.getItem('rememberedEmail'));
  const [show, setShow] = useState(false);
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  /* Apply dark mode class to body */
  useEffect(() => {
    if (dark) {
      document.body.classList.add('dark');
      localStorage.setItem('theme', 'dark');
    } else {
      document.body.classList.remove('dark');
      localStorage.setItem('theme', 'light');
    }
  }, [dark]);

  /**
   * Form submission handler
   */
  const handleSubmit = async (e) => {
    e.preventDefault();

    /* Frontend password format validation */
    if (!passwordRegex.test(password)) {
      setError(
        'Password must be at least 8 characters and include uppercase, lowercase, number, and symbol.'
      );
      return;
    }

    setError('');
    setLoading(true);

    try {
      const res = await fetch('http://localhost:8000/user/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email,
          password,
        }),
      });

      const data = await res.json();

      /* Backend rejected login */
      if (!res.ok) {
        setError(data.detail || data.message || 'Login failed');
        setLoading(false);
        return;
      }

      /* Store authentication token */
      localStorage.setItem('accessToken', data.access_token);

      /* Store user info */
      localStorage.setItem('user', JSON.stringify(data.user));

      /* Remember email logic */
      if (remember) {
        localStorage.setItem('rememberedEmail', email);
      } else {
        localStorage.removeItem('rememberedEmail');
      }

      /* Redirect after login */
      window.location.href = '/';
    } catch (err) {
      console.error(err);
      setError('Server error. Try again later.');
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      {/* Brand logo at the top left */}
      <div className="auth-brand-container">
        <Link to="/" className="auth-brand-logo">
          Mealimizer
        </Link>
      </div>

      {/* Login split card */}
      <div className="auth-split-card">
        {/* Left side: Graphic */}
        <div className="auth-card-left">
          <AnimatedCharacters isPasswordVisible={show} />
        </div>

        {/* Right side: Form */}
        <div className="auth-card-right">
          <div className="auth-card__header">
            <h1 className="heading-nosifer">WELCOME BACK!</h1>
            <p className="subtitle-geo">Log in to your account to continue</p>
          </div>

          <form className="auth-form" onSubmit={handleSubmit}>
            {/* Error message display */}
            {error && <div className="auth-error">{error}</div>}

            {/* Email field */}
            <div className="auth-field">
              <input
                type="email"
                placeholder="ashmit0203@gmail.com"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>

            {/* Password field */}
            <div className="auth-field">
              <div className="auth-password-wrap">
                <input
                  type={show ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => {
                    setPassword(e.target.value);
                    setError('');
                  }}
                  placeholder="Enter password"
                  required
                />
                <button
                  type="button"
                  className="auth-password-toggle-text"
                  onClick={() => setShow((prev) => !prev)}
                  aria-label={show ? 'Hide password' : 'Show password'}
                >
                  {show ? 'Hide' : 'Show'}
                </button>
              </div>
            </div>

            {/* Remember me + Forgot password */}
            <div className="auth-options">
              <label className="auth-checkbox">
                <input
                  type="checkbox"
                  checked={remember}
                  onChange={(e) => setRemember(e.target.checked)}
                />
                <span>Remember me</span>
              </label>
              <a href="#" className="auth-forgot">Forgot your password?</a>
            </div>

            {/* Submit button */}
            <button type="submit" className="btn-solid auth-submit" disabled={loading}>
              {loading ? 'Logging in...' : 'Log In'}
            </button>

            {/* Register link */}
            <div className="auth-switch">
              Don't have an account?{' '}
              <Link to="/register">Sign Up</Link>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}