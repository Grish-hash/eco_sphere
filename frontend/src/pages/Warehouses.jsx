import { useEffect, useState } from "react";
import { api } from "../api";

export default function Warehouses() {
  const [items, setItems] = useState([]);
  const [form, setForm] = useState({ name: "", lat: "", lng: "" });
  const [error, setError] = useState("");

  const load = () => api.warehouses().then(setItems).catch((e) => setError(e.message));
  useEffect(() => { load(); }, []);

  async function add(e) {
    e.preventDefault();
    setError("");
    try {
      await api.addWarehouse({ name: form.name, lat: parseFloat(form.lat), lng: parseFloat(form.lng) });
      setForm({ name: "", lat: "", lng: "" });
      load();
    } catch (err) {
      setError(err.message);
    }
  }

  async function remove(w) {
    if (!confirm(`Delete ${w.name}? Routes using it are deleted too.`)) return;
    await api.deleteWarehouse(w.id);
    load();
  }

  return (
    <>
      <h2>Warehouses</h2>
      <form className="inline" onSubmit={add}>
        <input placeholder="Name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required />
        <input placeholder="Latitude" type="number" step="any" min="-90" max="90" value={form.lat} onChange={(e) => setForm({ ...form, lat: e.target.value })} required />
        <input placeholder="Longitude" type="number" step="any" min="-180" max="180" value={form.lng} onChange={(e) => setForm({ ...form, lng: e.target.value })} required />
        <button type="submit">Add warehouse</button>
      </form>
      {error && <p className="error">{error}</p>}
      <table>
        <thead><tr><th>Name</th><th>Latitude</th><th>Longitude</th><th></th></tr></thead>
        <tbody>
          {items.map((w) => (
            <tr key={w.id}>
              <td>{w.name}</td><td>{w.lat}</td><td>{w.lng}</td>
              <td><button className="ghost" onClick={() => remove(w)}>Delete</button></td>
            </tr>
          ))}
          {!items.length && <tr><td colSpan="4" className="muted">No warehouses yet.</td></tr>}
        </tbody>
      </table>
    </>
  );
}
