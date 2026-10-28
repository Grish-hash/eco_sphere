import { useEffect, useState } from "react";
import { api } from "../api";

const MODES = ["truck", "rail", "ship", "air"];

export default function RoutesPage() {
  const [routes, setRoutes] = useState([]);
  const [warehouses, setWarehouses] = useState([]);
  const [form, setForm] = useState({ origin_id: "", destination_id: "", transport_mode: "truck", load_tons: 10 });
  const [error, setError] = useState("");

  const load = () => {
    api.routes().then(setRoutes).catch((e) => setError(e.message));
    api.warehouses().then(setWarehouses).catch(() => {});
  };
  useEffect(load, []);

  async function add(e) {
    e.preventDefault();
    setError("");
    try {
      await api.addRoute({
        origin_id: Number(form.origin_id),
        destination_id: Number(form.destination_id),
        transport_mode: form.transport_mode,
        load_tons: parseFloat(form.load_tons),
      });
      load();
    } catch (err) {
      setError(err.message);
    }
  }

  const options = (
    <>
      <option value="">Select…</option>
      {warehouses.map((w) => <option key={w.id} value={w.id}>{w.name}</option>)}
    </>
  );

  return (
    <>
      <h2>Routes</h2>
      <form className="inline" onSubmit={add}>
        <select value={form.origin_id} onChange={(e) => setForm({ ...form, origin_id: e.target.value })} required>{options}</select>
        <select value={form.destination_id} onChange={(e) => setForm({ ...form, destination_id: e.target.value })} required>{options}</select>
        <select value={form.transport_mode} onChange={(e) => setForm({ ...form, transport_mode: e.target.value })}>
          {MODES.map((m) => <option key={m}>{m}</option>)}
        </select>
        <input type="number" min="0.1" step="any" value={form.load_tons} onChange={(e) => setForm({ ...form, load_tons: e.target.value })} title="Load in tons" required />
        <button type="submit">Add route</button>
      </form>
      {error && <p className="error">{error}</p>}
      <table>
        <thead><tr><th>From</th><th>To</th><th>Mode</th><th>Load (t)</th><th>Distance (km)</th><th>CO₂ (kg)</th><th></th></tr></thead>
        <tbody>
          {routes.map((r) => (
            <tr key={r.id}>
              <td>{r.origin_name}</td><td>{r.destination_name}</td><td>{r.transport_mode}</td>
              <td>{r.load_tons}</td><td>{r.distance_km.toLocaleString()}</td><td>{r.emissions_kg.toLocaleString()}</td>
              <td><button className="ghost" onClick={() => api.deleteRoute(r.id).then(load)}>Delete</button></td>
            </tr>
          ))}
          {!routes.length && <tr><td colSpan="7" className="muted">No routes yet. Pick two warehouses above.</td></tr>}
        </tbody>
      </table>
    </>
  );
}
