import { useState, useEffect } from "react";
import "./Register.css";
import loginImg from "../assets/image.jpg";

export default function Register() {
  const [dark, setDark] = useState(false);
  const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{8,}$/;
  const [error, setError] = useState("");
  const [email, setEmail] = useState("");


  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [age, setAge] = useState("");
  const [gender, setGender] = useState("");
  const [phone, setPhone] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  useEffect(() => {
    if (dark) {
      document.body.classList.add("dark");
    } else {
      document.body.classList.remove("dark");
    }
  }, [dark]);

  const [show, setShow] = useState(false);
  const [password, setPassword] = useState("");

  const handleSubmit = async (e) => {
  e.preventDefault();

  // 1. Check password strength
  if (!passwordRegex.test(password)) {
    setError(
      "Password must be at least 8 characters and include uppercase, lowercase, number, and symbol."
    );
    return;
  }

  // 2. Check password == confirmPassword
  if (password !== confirmPassword) {
    setError("Passwords do not match.");
    return;
  }

  // 3. If both checks pass, clear error
  setError("");

  // 4. Send data to backend
  try {
   const res = await fetch("http://localhost:8000/user/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        first_name: firstName,
        last_name: lastName,
        age: Number(age),
        gender,
        phone,
        email,
        password,
      })
    });       

    const data = await res.json();

    if (!res.ok) {
      setError(data.detail || "Registration failed");
      return;
    }

    // 5. Success
    localStorage.setItem("user", JSON.stringify(data.user));
    window.location.href = "/";
  } catch (err) {
    setError("Server error. Try again later.");
    console.log(err);
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
          <h1>Hi there!</h1>
          <p>Please enter your details to register</p>
          
          <form className="login-form" onSubmit={handleSubmit}>
          <input
            type="text" 
            placeholder="First Name"
            required
            value={firstName}
            onChange={(e) => setFirstName(e.target.value)}
            className="firstName"
          />

          <input
            type="text"
            placeholder="Last Name"
            required
            value={lastName}
            onChange={(e) => setLastName(e.target.value)}
            className="lastName"
          />

          <div className="ageGenderRow">
            <input
              type="number"
              placeholder="Age"
              required
              value={age}
              onChange={(e) => setAge(e.target.value)}
              min={5}
              max={120}
              className="age"
            />

            <select
              required
              value={gender}
              onChange={(e) => setGender(e.target.value)}
              className="gender" 
              >
              <option value="">Select Gender</option>
              <option value="male">Male</option>
              <option value="female">Female</option>
              <option value="other">Other</option>
            </select>
          </div>

        <input
          type="tel"
          placeholder="Phone Number"
          required
          value={phone}
          onChange={(e) => setPhone(e.target.value)}
          className="phone"
        />

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
        <div className="password-container">
          <div className="password-wrapper">
            <input
              type="password"
              value={confirmPassword}
              onChange={(e) => {
                setConfirmPassword(e.target.value);
                setError("");
              }}
              placeholder="Confirm password"
              required
              className="password-input"
            />
          </div>
        </div>
          <button type="submit" className="register">Register</button>
          <div className="oldUser">
            Already a user? <a href="/Login">Login</a>
          </div>
          </form>
        </div>
      </div>
    </>
  );
}