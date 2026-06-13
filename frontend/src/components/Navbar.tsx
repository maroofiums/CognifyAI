import { NavLink } from "react-router-dom";

export default function Navbar() {
  return (
    <header className="navbar">
      <div className="navbar-brand">
        <span className="navbar-logo">⚡</span>
        <span className="navbar-title">CognifyAI</span>
      </div>
      <nav className="navbar-links">
        <NavLink to="/" className={({ isActive }) => (isActive ? "nav-link active" : "nav-link")} end>
          Home
        </NavLink>
        <NavLink to="/results" className={({ isActive }) => (isActive ? "nav-link active" : "nav-link")}>
          Results
        </NavLink>
        <NavLink to="/history" className={({ isActive }) => (isActive ? "nav-link active" : "nav-link")}>
          History
        </NavLink>
      </nav>
    </header>
  );
}
