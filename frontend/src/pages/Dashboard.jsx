import "./Dashboard.css";
import { useState, useEffect } from "react";
import "./Home.css";

export default function Dashboard() {
  const [dark, setDark] = useState(false);

  useEffect(() => {
    if (dark) {
      document.body.classList.add("dark");
    } else {
      document.body.classList.remove("dark");
    }
  }, [dark]);
    return(
      <>
        <header>
          <nav className="nav">
          <h1 className="sitename">Mealimizer</h1>
            <ul className="login-container">
              <li className="navbar"><a href="/">Home</a></li>
              <li className="navbar"><a href="/Dashboard">Dashboard</a></li>
              <li className="navbar"><a href="/Login">Login</a></li>
              <li className="navbar"><a href="/Chat">Chat</a></li>
              <li className="navbar"><a href="/Profile">Profile</a></li>
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
          
          <h1>Welcome to the Home Page</h1>
      </header>
      <footer>
        <p>&copy; 2024 Meal Optimization App. All rights reserved.</p>
      </footer>
      </>
    )
}