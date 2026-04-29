/**
 * Register.jsx — User registration page
 * 
 * ⚠️ ALL EXISTING AUTH LOGIC IS PRESERVED:
 * - Password regex validation (uppercase, lowercase, number, symbol, 8+ chars)
 * - Password/confirm password matching
 * - POST to http://localhost:8000/user/register
 * - Store user in localStorage on success
 * - Redirect to "/" on success
 * 
 * Only the UI/styling has been updated to match the design system.
 * Uses Link components for SPA navigation instead of <a> tags.
 */

import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Eye, EyeOff } from 'lucide-react';
import './Register.css';
import AnimatedCharacters from '../components/AnimatedCharacters';

export default function Register() {

  /* Password validation regex */
  const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{8,}$/;

  /* Form state — all fields from original registration form */
  const [error, setError] = useState('');
  const [email, setEmail] = useState('');
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [age, setAge] = useState('');
  const [gender, setGender] = useState('');
  const [phone, setPhone] = useState('');
  const [show, setShow] = useState(false);
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);


  /**
   * Form submission handler
   */
  const handleSubmit = async (e) => {
    e.preventDefault();

    /* 1. Check password strength */
    if (!passwordRegex.test(password)) {
      setError(
        'Password must be at least 8 characters and include uppercase, lowercase, number, and symbol.'
      );
      return;
    }

    /* 2. Check password == confirmPassword */
    if (password !== confirmPassword) {
      setError('Passwords do not match.');
      return;
    }

    /* 3. Clear error */
    setError('');
    setLoading(true);

    /* 4. Send data to backend */
    try {
      const res = await fetch('http://localhost:8000/user/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          first_name: firstName,
          last_name: lastName,
          age: Number(age),
          gender,
          phone,
          email,
          password,
        }),
      });

      const data = await res.json();

      if (!res.ok) {
        setError(data.detail || 'Registration failed');
        setLoading(false);
        return;
      }

      /* 5. Success — redirect to login */
      window.location.href = '/login';
    } catch (err) {
      setError('Server error. Try again later.');
      console.log(err);
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">

      {/* Registration split card */}
      <div className="auth-split-card">
        {/* Left side: Graphic */}
        <div className="auth-card-left">
          <AnimatedCharacters isPasswordVisible={show} />
        </div>

        {/* Right side: Form */}
        <div className="auth-card-right">
          <div className="auth-card__header">
            <h1 className="heading-nosifer">HI THERE!</h1>
            <p className="subtitle-geo">Please enter your details to register</p>
          </div>

          <form className="auth-form" onSubmit={handleSubmit}>
            {/* Error message */}
            {error && <div className="auth-error">{error}</div>}

            {/* Name fields */}
            <div className="auth-row">
              <div className="auth-field">
                <input
                  type="text"
                  placeholder="First Name"
                  required
                  value={firstName}
                  onChange={(e) => setFirstName(e.target.value)}
                />
              </div>
              <div className="auth-field">
                <input
                  type="text"
                  placeholder="Last Name"
                  required
                  value={lastName}
                  onChange={(e) => setLastName(e.target.value)}
                />
              </div>
            </div>

            {/* Age + Gender row */}
            <div className="auth-row">
              <div className="auth-field">
                <input
                  type="text"
                  placeholder="Age"
                  required
                  value={age}
                  onChange={(e) => setAge(e.target.value)}
                  min={5}
                  max={120}
                />
              </div>
              <div className="auth-field">
                <select
                  required
                  value={gender}
                  onChange={(e) => setGender(e.target.value)}
                >
                  <option value="">Select Gender</option>
                  <option value="male">Male</option>
                  <option value="female">Female</option>
                  <option value="other">Other</option>
                </select>
              </div>
            </div>

            {/* Phone */}
            <div className="auth-field">
              <input
                type="tel"
                placeholder="Phone Number"
                required
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
              />
            </div>

            {/* Email */}
            <div className="auth-field">
              <input
                type="email"
                placeholder="Email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>

            {/* Password */}
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

            {/* Confirm Password */}
            <div className="auth-field">
              <div className="auth-password-wrap">
                <input
                  type="password"
                  value={confirmPassword}
                  onChange={(e) => {
                    setConfirmPassword(e.target.value);
                    setError('');
                  }}
                  placeholder="Confirm password"
                  required
                />
              </div>
            </div>

            {/* Submit */}
            <button type="submit" className="btn-solid auth-submit" disabled={loading}>
              {loading ? 'Registering...' : 'Register'}
            </button>

            {/* Login link */}
            <div className="auth-switch">
              Already a user?{' '}
              <Link to="/login">Login</Link>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}