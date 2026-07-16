/* =====================================================================
   api.js — capa delgada sobre fetch para hablar con la API REST del SGCL.
   Guarda el token JWT en localStorage (solo para este taller/demo).
   ===================================================================== */

const API_BASE = "/api";

const Auth = {
  getToken() { return localStorage.getItem("sgcl_token"); },
  getUser() {
    const raw = localStorage.getItem("sgcl_user");
    return raw ? JSON.parse(raw) : null;
  },
  setSession(token, user) {
    localStorage.setItem("sgcl_token", token);
    localStorage.setItem("sgcl_user", JSON.stringify(user));
  },
  clear() {
    localStorage.removeItem("sgcl_token");
    localStorage.removeItem("sgcl_user");
  },
  requireSession() {
    if (!this.getToken()) {
      window.location.href = "/login";
    }
  },
  logout() {
    this.clear();
    window.location.href = "/login";
  },
};

async function api(path, { method = "GET", body = null, auth = true } = {}) {
  const headers = { "Content-Type": "application/json" };
  if (auth) {
    const token = Auth.getToken();
    if (!token) { Auth.logout(); return; }
    headers["Authorization"] = `Bearer ${token}`;
  }

  const res = await fetch(`${API_BASE}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : null,
  });

  if (res.status === 401) {
    Auth.logout();
    return;
  }

  let data = null;
  try { data = await res.json(); } catch (_e) { data = null; }

  if (!res.ok) {
    const msg = (data && data.error) ? data.error : `Error ${res.status}`;
    throw new Error(msg);
  }
  return data;
}

function toast(message, isError = false) {
  const existing = document.querySelector(".toast");
  if (existing) existing.remove();

  const el = document.createElement("div");
  el.className = "toast" + (isError ? " is-error" : "");
  el.textContent = message;
  document.body.appendChild(el);
  setTimeout(() => el.remove(), 3800);
}

function initials(fullName) {
  if (!fullName) return "?";
  const parts = fullName.replace(/^Lic\.\s*/i, "").trim().split(/\s+/);
  return (parts[0]?.[0] || "").toUpperCase() + (parts[1]?.[0] || "").toUpperCase();
}

function statusSlug(estado) {
  if (!estado) return "pendiente";
  const s = estado.toLowerCase();
  if (s.includes("curso")) return "en-curso";
  if (s.includes("cerrado")) return "cerrado";
  return "pendiente";
}

function fechaLarga(isoDate) {
  if (!isoDate) return "";
  const d = new Date(isoDate + "T00:00:00");
  return d.toLocaleDateString("es-PA", { weekday: "long", day: "numeric", month: "long", year: "numeric" });
}

/* Pinta el nombre/avatar del usuario y activa el link del rail correspondiente */
function paintShell(activeHref) {
  const user = Auth.getUser();
  const nameEl = document.querySelector("[data-user-name]");
  const roleEl = document.querySelector("[data-user-role]");
  const avEl = document.querySelector("[data-user-avatar]");
  if (user) {
    if (nameEl) nameEl.textContent = user.nombre_completo || user.usuario;
    if (roleEl) roleEl.textContent = user.rol || "";
    if (avEl) avEl.textContent = initials(user.nombre_completo || user.usuario);
  }
  document.querySelectorAll(".rail__link").forEach((a) => {
    a.classList.toggle("is-active", a.getAttribute("href") === activeHref);
  });
  const logoutBtn = document.querySelector("[data-logout]");
  if (logoutBtn) logoutBtn.addEventListener("click", () => Auth.logout());

  const toggle = document.querySelector("[data-mobile-toggle]");
  const rail = document.querySelector(".rail");
  if (toggle && rail) {
    toggle.addEventListener("click", () => rail.classList.toggle("is-open"));
  }
}
