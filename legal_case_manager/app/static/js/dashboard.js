Auth.requireSession();
paintShell("/dashboard");

const fechaHoyEl = document.getElementById("fechaHoy");
const statRow = document.getElementById("statRow");
const recientesList = document.getElementById("recientesList");
const agendaList = document.getElementById("agendaList");
const agendaCount = document.getElementById("agendaCount");

async function cargarDashboard() {
  try {
    const [resumen, expedientes] = await Promise.all([
      api("/dashboard"),
      api("/expedientes"),
    ]);

    fechaHoyEl.textContent = fechaLarga(resumen.fecha);

    const c = resumen.contadores || {};
    statRow.innerHTML = `
      <div class="stat stat--pendiente"><span class="n">${c["Pendiente"] || 0}</span><span class="label">Pendientes</span></div>
      <div class="stat stat--curso"><span class="n">${c["En curso"] || 0}</span><span class="label">En curso</span></div>
      <div class="stat stat--cerrado"><span class="n">${c["Cerrado"] || 0}</span><span class="label">Cerrados</span></div>
    `;

    const recientes = expedientes.slice(0, 6);
    recientesList.innerHTML = recientes.length
      ? recientes.map(folioRow).join("")
      : `<div class="empty">Aún no hay expedientes registrados.</div>`;

    const eventos = resumen.agenda_del_dia || [];
    agendaCount.textContent = `${eventos.length} evento${eventos.length === 1 ? "" : "s"}`;
    agendaList.innerHTML = eventos.length
      ? eventos.map(agendaRow).join("")
      : `<div class="empty">No hay eventos programados para hoy.</div>`;

  } catch (err) {
    toast(err.message || "No se pudo cargar el panel", true);
  }
}

function folioRow(exp) {
  const slug = statusSlug(exp.estado);
  return `
    <a class="folio folio--${slug}" href="/expedientes?id=${exp.id_expediente}">
      <span class="folio__num">${exp.numero_expediente}</span>
      <div class="folio__main">
        <div class="name">${exp.asegurado_nombre}</div>
        <div class="meta">${exp.aseguradora || "—"} · ${exp.juzgado || "—"}</div>
      </div>
      <span class="pill pill--${slug}">${exp.estado}</span>
    </a>
  `;
}

function agendaRow(ev) {
  return `
    <div class="agenda-item">
      <div class="time">${ev.hora_evento ? ev.hora_evento.slice(0,5) : "—"}</div>
      <div class="body">
        <div class="t">${ev.titulo}</div>
        <div class="d">${ev.numero_expediente || ""} ${ev.descripcion ? "· " + ev.descripcion : ""}</div>
      </div>
    </div>
  `;
}

cargarDashboard();
