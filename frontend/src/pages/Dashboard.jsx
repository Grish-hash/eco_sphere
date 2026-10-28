import { useEffect, useState, useCallback } from "react";
import { MapContainer, TileLayer, CircleMarker, Polyline, Tooltip, useMap } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import { api } from "../api";

const COLORS = { High: "#c0392b", Medium: "#d98e04", Low: "#2e8b57", Unknown: "#8a94a0" };

function FitBounds({ nodes }) {
  const map = useMap();
  useEffect(() => {
    if (nodes.length) map.fitBounds(nodes.map((n) => [n.lat, n.lng]), { padding: [40, 40], maxZoom: 6 });
  }, [nodes.length]);
  return null;
}

export default function Dashboard() {
  const [nodes, setNodes] = useState([]);
  const [routes, setRoutes] = useState([]);
  const [vehicles, setVehicles] = useState([]);
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState("");

  const load = useCallback(async () => {
    const [n, r] = await Promise.all([api.riskNodes(), api.routes()]);
    setNodes(n);
    setRoutes(r);
  }, []);

  useEffect(() => {
    load().catch((e) => setMsg(e.message));
  }, [load]);

  // simulated live fleet: poll every 10s
  useEffect(() => {
    const tick = () => api.vehicles().then(setVehicles).catch(() => {});
    tick();
    const id = setInterval(tick, 10000);
    return () => clearInterval(id);
  }, []);

  async function refreshWeather() {
    setBusy(true);
    setMsg("");
    try {
      const res = await api.refreshRisk();
      setMsg(res.failed.length ? `Could not fetch: ${res.failed.join(", ")}` : `Updated ${res.updated} locations`);
      await load();
    } catch (e) {
      setMsg(e.message);
    }
    setBusy(false);
  }

  const high = nodes.filter((n) => n.level === "High");
  const totalCo2 = routes.reduce((s, r) => s + r.emissions_kg, 0);

  return (
    <>
      <div className="stats">
        <div className="stat"><span className="num">{nodes.length}</span>warehouses</div>
        <div className="stat"><span className="num" style={{ color: high.length ? COLORS.High : undefined }}>{high.length}</span>high-risk nodes</div>
        <div className="stat"><span className="num">{(totalCo2 / 1000).toFixed(1)} t</span>CO₂ across {routes.length} routes</div>
        <div className="stat actions">
          <button onClick={refreshWeather} disabled={busy}>{busy ? "Fetching…" : "Refresh weather risk"}</button>
          <span className="muted">{msg}</span>
        </div>
      </div>

      <MapContainer center={[20, 40]} zoom={2} className="map">
        <TileLayer
          attribution='&copy; OpenStreetMap contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <FitBounds nodes={nodes} />
        {routes.map((r) => (
          <Polyline key={r.id} positions={[[r.origin_lat, r.origin_lng], [r.dest_lat, r.dest_lng]]}
            pathOptions={{ color: "#3b6ea5", weight: 2, dashArray: r.transport_mode === "air" ? "6 6" : undefined }}>
            <Tooltip sticky>{r.origin_name} to {r.destination_name} by {r.transport_mode}: {r.emissions_kg} kg CO₂</Tooltip>
          </Polyline>
        ))}
        {nodes.map((n) => (
          <CircleMarker key={n.id} center={[n.lat, n.lng]} radius={11}
            pathOptions={{ color: "#fff", weight: 2, fillColor: COLORS[n.level], fillOpacity: 0.95 }}>
            <Tooltip>
              <strong>{n.name}</strong><br />
              {n.risk_score == null ? "No weather data yet" : `${n.level} risk (${n.risk_score}) · peak on ${n.peak_day}`}
            </Tooltip>
          </CircleMarker>
        ))}
        {vehicles.map((v) => (
          <CircleMarker key={v.route_id} center={[v.lat, v.lng]} radius={5}
            pathOptions={{ color: "#1d2733", weight: 1, fillColor: "#ffd24a", fillOpacity: 1 }}>
            <Tooltip>{v.mode} · {Math.round(v.progress * 100)}% of the way</Tooltip>
          </CircleMarker>
        ))}
      </MapContainer>

      <h2>Forecast risk by location</h2>
      <table>
        <thead><tr><th>Warehouse</th><th>Risk</th><th>Level</th><th>Worst day</th></tr></thead>
        <tbody>
          {nodes.map((n) => (
            <tr key={n.id}>
              <td>{n.name}</td>
              <td>{n.risk_score ?? "–"}</td>
              <td><span className="pill" style={{ background: COLORS[n.level] }}>{n.level}</span></td>
              <td>{n.peak_day ?? "–"}</td>
            </tr>
          ))}
          {!nodes.length && <tr><td colSpan="4" className="muted">No warehouses yet. Add one on the Warehouses page.</td></tr>}
        </tbody>
      </table>
    </>
  );
}
