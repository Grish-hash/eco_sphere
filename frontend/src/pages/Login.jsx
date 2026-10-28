import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { api, setToken } from "../api";

export default function Login() {
  const [mode, setMode] = useState("login");
  const [company, setCompany] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  async function submit(e) {
    e.preventDefault();
    setError("");
    try {
      const res = mode === "login" ? await api.login(email, password) : await api.register(company, email, password);
      setToken(res.access_token);
      navigate("/");
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="login">
      <form className="panel" onSubmit={submit}>
        <h1>EcoSphere</h1>
        <p className="muted">Track the climate impact and weather risk of your supply chain.</p>
        {mode === "register" && (
          <label>Company name<input value={company} onChange={(e) => setCompany(e.target.value)} required /></label>
        )}
        <label>Email<input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required /></label>
        <label>Password<input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required /></label>
        {error && <p className="error">{error}</p>}
        <button type="submit">{mode === "login" ? "Log in" : "Create account"}</button>
        <button type="button" className="ghost" onClick={() => setMode(mode === "login" ? "register" : "login")}>
          {mode === "login" ? "New company? Register" : "Have an account? Log in"}
        </button>
      </form>
    </div>
  );
}
