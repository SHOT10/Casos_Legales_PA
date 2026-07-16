Auth.requireSession();
paintShell("/agenda");

const fFecha = document.getElementById("fFecha");
const btnHoy = document.getElementById("btnHoy");
const agendaList = document.getElementById("agendaList");
const agendaFechaLegible = document.getElementById("agendaFechaLegible");
const modalBackdrop = document.getElementById("modalBackdrop");
const eventoForm = document.getElementById("eventoForm");
const selExpediente = document.getElementById("id_expediente");

function hoyISO() {
  const d = new Date();
  return d.toISOString().slice(0, 10);
}

fFecha.value = hoyISO();

async function cargarExpedientesSelect() {
  const expedientes = await api("/expedientes");
  selExpediente.innerHTML = expedientes
    .map(e => `<option value="${e.id_expediente}">${e.numero_expediente} — ${e.asegurado_nombre}</option>`)
    .join("");
}

async function cargarAgenda() {
  agendaList.innerHTML = `<div class="empty">Cargando…</div>`;
  agendaFechaLegible.textContent = fechaLarga(fFecha.value);
  try {
    const eventos = await api(`/agenda?fecha=${fFecha.value}`);
    agendaList.innerHTML = eventos.length
      ? eventos.map(agendaRow).join("")
      : `<div class="empty">No hay eventos programados para esta fecha.</div>`;
  } catch (err) {
    agendaList.innerHTML = `<div class="empty">No se pudo cargar la agenda.</div>`;
    toast(err.message, true);
  }
}

function agendaRow(ev) {
  return `
    <div class="agenda-item">
      <div class="time">${ev.hora_evento ? ev.hora_evento.slice(0,5) : "—"}</div>
      <div class="body">
        <div class="t">${ev.titulo} ${ev.completado ? "✓" : ""}</div>
        <div class="d">${ev.numero_expediente ? ev.numero_expediente + " · " : ""}${ev.descripcion || ""}</div>
      </div>
    </div>
  `;
}

fFecha.addEventListener("change", cargarAgenda);
btnHoy.addEventListener("click", () => { fFecha.value = hoyISO(); cargarAgenda(); });

document.getElementById("btnNuevoEvento").addEventListener("click", () => {
  eventoForm.reset();
  document.getElementById("fecha_evento").value = fFecha.value || hoyISO();
  modalBackdrop.classList.add("is-open");
});
document.querySelectorAll("[data-close-modal]").forEach(btn =>
  btn.addEventListener("click", () => modalBackdrop.classList.remove("is-open"))
);
modalBackdrop.addEventListener("click", (e) => {
  if (e.target === modalBackdrop) modalBackdrop.classList.remove("is-open");
});

eventoForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  try {
    await api("/agenda", {
      method: "POST",
      body: {
        id_expediente: Number(selExpediente.value),
        titulo: document.getElementById("titulo").value.trim(),
        fecha_evento: document.getElementById("fecha_evento").value,
        hora_evento: document.getElementById("hora_evento").value || null,
        descripcion: document.getElementById("descripcion").value.trim(),
      },
    });
    toast("Evento creado");
    modalBackdrop.classList.remove("is-open");
    fFecha.value = document.getElementById("fecha_evento").value;
    cargarAgenda();
  } catch (err) {
    toast(err.message, true);
  }
});

(async function init() {
  try {
    await cargarExpedientesSelect();
    await cargarAgenda();
  } catch (err) {
    toast(err.message || "Error al inicializar la página", true);
  }
})();
