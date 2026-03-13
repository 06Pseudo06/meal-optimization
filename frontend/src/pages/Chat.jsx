import { useState, useEffect } from "react";
import "./Home.css";
import { Link } from "react-router-dom";
import default_user from "../assets/default-user.jpg";

export default function Chat() {

  const [dark, setDark] = useState(() => {
    return localStorage.getItem("theme") === "dark";
  });
  const token = localStorage.getItem("accessToken");
  const [profileImage] = useState(() => {
    const savedImage = localStorage.getItem("profileImage");

    if (savedImage && savedImage !== "null") {
      return savedImage;
    }

    return default_user;
  });

  useEffect(() => {
    if (dark) {
      document.body.classList.add("dark");
      localStorage.setItem("theme", "dark");
    } else {
      document.body.classList.remove("dark");
      localStorage.setItem("theme", "light");
    }
  }, [dark]);

  const logout = () => {
    localStorage.removeItem("accessToken");
    window.location.href = "/Login";
  };

  return (
    <>
      <header>

        <nav className="nav">
          <h1 className="sitename">Mealimizer</h1>

          <ul className="login-container">

            <li className="navbar"><Link to="/">Home</Link></li>
            <li className="navbar"><Link to="/Dashboard">Dashboard</Link></li>
            <li className="navbar"><Link to="/Chat">Chat</Link></li>
            <li className="navbar profile-menu">

              <div className="profile-image-container">

                <img
                  src={profileImage}
                  alt="profile"
                  className="profile-icon"
                  onError={(e) => {
                    e.target.src = default_user;
                  }}
                />

              </div>

              <div className="dropdown">

                {token ? (
                  <>
                    <Link to="/Profile">My Profile</Link>
                    <Link to="/Settings">Settings</Link>

                    <div className="appearance-row">
                      <span>Appearance</span>

                      <button
                        className={`mode-toggle ${dark ? "dark" : "light"}`}
                        onClick={() => setDark(!dark)}
                      >
                        <span className="icon sun">☀</span>
                        <span className="icon moon">🌙</span>
                        <span className="knob"></span>
                      </button>
                    </div>

                    <button className="logout-btn" onClick={logout}>
                      Logout
                    </button>
                  </>
                ) : (
                  <>
                    <Link to="/Login" className="auth-btn">
                      Login
                    </Link>

                    <Link to="/Register" className="auth-btn register-btn">
                      Register
                    </Link>
                  </>
                )}

              </div>

            </li>

          </ul>
        </nav>

        <h1>Welcome to the Home Page</h1>

      </header>

      <footer>
        <p>&copy; 2024 Meal Optimization App. All rights reserved.</p>
      </footer>
    </>
  );
}