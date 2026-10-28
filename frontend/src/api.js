const API = import.meta.env.VITE_API_URL || "http://localhost:8000";

export const getToken = () => localStorage.getItem("token");
export const setToken = (t) => localStorage.setItem("token", t);
export const logout = () => localStorage.removeItem("token");

async function request(path, { method = "GET", body, form } = {}) {
  const headers = {};
  if (getToken()) headers.Authorization = `Bearer ${getToken()}`;
  let payload;
  if (form) {
    payload = new URLSearchParams(form);
  } else if (body) {
    headers["Content-Type"] = "application/json";
    payload = JSON.stringify(body);
  }
  const res = await fetch(API + path, { method, headers, body: payload });
  if (res.status === 401 && path !== "/auth/login") {
    logout();
    window.location.href = "/login";
  }
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(typeof data.detail === "string" ? data.detail : "Request failed");
  return data;
}

export const api = {
  login: (email, password) => request("/auth/login", { method: "POST", form: { username: email, password } }),
  register: (company_name, email, password) =>
    request("/auth/register", { method: "POST", body: { company_name, email, password } }),
  me: () => request("/auth/me"),

  warehouses: () => request("/warehouses"),
  addWarehouse: (w) => request("/warehouses", { method: "POST", body: w }),
  deleteWarehouse: (id) => request(`/warehouses/${id}`, { method: "DELETE" }),

  routes: () => request("/routes"),
  addRoute: (r) => request("/routes", { method: "POST", body: r }),
  deleteRoute: (id) => request(`/routes/${id}`, { method: "DELETE" }),

  riskNodes: () => request("/risk/nodes"),
  refreshRisk: () => request("/risk/refresh", { method: "POST" }),
  vehicles: () => request("/vehicles"),
};
