import { useEffect, useState } from "react";
import { Routes, Route, Navigate, NavLink, useNavigate } from "react-router-dom";
import { api, getToken, logout } from "./api";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import Warehouses from "./pages/Warehouses";
import RoutesPage from "./pages/RoutesPage";

function Layout({ children }) {
  const [company, setCompany] = useState("");
  const navigate = useNavigate();
  useEffect(() => {
    api.me().then((m) => setCompany(m.company)).catch(() => {});
  }, []);
  return (
    <>
      <header className="nav">
        <strong className="brand">EcoSphere</strong>
        <nav>
          <NavLink to="/" end>Dashboard</NavLink>
          <NavLink to="/warehouses">Warehouses</NavLink>
          <NavLink to="/routes">Routes</NavLink>
        </nav>
        <span className="spacer" />
        <span className="muted">{company}</span>
        <button className="ghost" onClick={() => { logout(); navigate("/login"); }}>Log out</button>
      </header>
      <main>{children}</main>
    </>
  );
}

function Protected({ children }) {
  return getToken() ? <Layout>{children}</Layout> : <Navigate to="/login" replace />;
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/" element={<Protected><Dashboard /></Protected>} />
      <Route path="/warehouses" element={<Protected><Warehouses /></Protected>} />
      <Route path="/routes" element={<Protected><RoutesPage /></Protected>} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
