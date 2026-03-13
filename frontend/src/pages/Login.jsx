import { useState, useEffect } from "react";
import "./Login.css";
import loginImg from "../assets/image.jpg";

export default function Login() {
  const [dark, setDark] = useState(() => {
  return localStorage.getItem("theme") === "dark";  
  })
  const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{8,}$/;
  const [error, setError] = useState("");const [email, setEmail] = useState(() => localStorage.getItem("rememberedEmail") || "");
  const [remember, setRemember] = useState(() => !!localStorage.getItem("rememberedEmail"));

useEffect(() => {
  if (dark) {
    document.body.classList.add("dark");
    localStorage.setItem("theme", "dark");
  } else {
    document.body.classList.remove("dark");
    localStorage.setItem("theme", "light");
  }
}, [dark]);

  const [show, setShow] = useState(false);
  const [password, setPassword] = useState("");

  const handleSubmit = async (e) => {
  e.preventDefault();

  // frontend password format validation
  if (!passwordRegex.test(password)) {
    setError(
      "Password must be at least 8 characters and include uppercase, lowercase, number, and symbol."
    );
    return;
  }

  setError("");

  try {
    const res = await fetch("http://localhost:8000/user/login", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        email,
        password
      })
    });

    const data = await res.json();

    // backend rejected login
    if (!res.ok) {
      setError(data.detail || data.message || "Login failed");
      return;
    }

    // store authentication token
    localStorage.setItem("accessToken", data.access_token);

    // store user info
    localStorage.setItem("user", JSON.stringify(data.user));

    // remember email logic
    if (remember) {
      localStorage.setItem("rememberedEmail", email);
    } else {
      localStorage.removeItem("rememberedEmail");
    }

    // redirect after login
    window.location.href = "/";

  } catch (err) {
    console.error(err);
    setError("Server error. Try again later.");
  }
};

  return (
    <>
      <header>
        <nav className="nav">
          <h1 className="sitename">Mealimizer</h1>
          <ul className="login-container">
            <li className="navbar"><a href="/">Home</a></li>
            <li className="navbar"><a href="/Dashboard">About</a></li>
            <li className="navbar"><a href="/Profile">Help and Support</a></li>
            <li>
              <button
                className={`mode-toggle ${dark ? "dark" : "light"}`}
                onClick={() => setDark(!dark)}
                aria-label="Toggle theme"
              >
                <span className="icon sun">☀</span>
                <span className="icon moon">🌙</span>
                <span className="knob"></span>
              </button>
            </li>
          </ul>
        </nav>
    
      </header>
      <div className="main">
        <div className="image"> <img src={loginImg} alt="Login" /></div>
        <div className="content">
          <h1>Welcome Back!</h1>
          <p>Log in to your account to continue</p>
          
          <form className="login-form" onSubmit={handleSubmit}>
          <input
            type="email"
            placeholder="Email"
            required
            className="emailInput"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
          <div className="password-container">
            {error && <div className="password-tooltip">{error}</div>}

            <div className="password-wrapper">
              <input
                type={show ? "text" : "password"}
                value={password}
                onChange={(e) => {
                setPassword(e.target.value);
                setError("");
              }}
              placeholder="Enter password"
              required
              className="password-input"
              />

              <button
              type="button"
              className="toggle-btn inside"
              onClick={() => setShow((prev) => !prev)}
              >
              {show ? "Hide" : "Show"}
              </button>
            </div>
          </div>
          <div className="links">
            <label htmlFor="remember" className="remember-label">
              <input
                type="checkbox"
                name="remember"
                id="remember"
                className="remember"
                checked={remember}
                onChange={(e) => setRemember(e.target.checked)}
              />
              Remember me
            </label>

            <a href="">Forgot your password?</a>
          </div>
          <button type="submit" className="login">Log In</button>
          <div className="newUser">
            Don't have an account? <a href="/Register">Sign Up</a>
          </div>
          </form>
        </div>
      </div>
    </>
  );
}