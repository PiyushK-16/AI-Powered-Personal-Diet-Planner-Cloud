/**
 * frontend/js/api.js
 *
 * Thin wrapper around fetch() so every page talks to the backend the
 * same way. In a real cloud deployment, API_BASE_URL would point at
 * your deployed backend URL instead of localhost.
 *
 * SECURITY NOTE (documented, not hidden): this demo stores the JWT in
 * localStorage for simplicity, which is fine for a local student demo.
 * A production app would prefer an httpOnly cookie to reduce XSS risk --
 * see docs/CLOUD_CONCEPTS.md "Security" section.
 */

const API_BASE_URL = "http://127.0.0.1:5000";

function getToken() {
  return localStorage.getItem("token");
}

function setToken(token) {
  localStorage.setItem("token", token);
}

function clearToken() {
  localStorage.removeItem("token");
}

function requireAuthOrRedirect() {
  if (!getToken()) {
    window.location.href = "login.html";
  }
}

async function apiRequest(path, { method = "GET", body = null, isForm = false } = {}) {
  const headers = {};
  const token = getToken();
  if (token) headers["Authorization"] = `Bearer ${token}`;
  if (!isForm && body) headers["Content-Type"] = "application/json";

  const response = await fetch(`${API_BASE_URL}${path}`, {
    method,
    headers,
    body: isForm ? body : body ? JSON.stringify(body) : undefined,
  });

  let data = {};
  try { data = await response.json(); } catch (e) { /* no JSON body */ }

  if (!response.ok) {
    throw new Error(data.error || `Request failed (${response.status})`);
  }
  return data;
}

function showMessage(elementId, text, type = "error") {
  const el = document.getElementById(elementId);
  if (!el) return;
  el.textContent = text;
  el.className = `msg ${type}`;
  el.style.display = "block";
}
