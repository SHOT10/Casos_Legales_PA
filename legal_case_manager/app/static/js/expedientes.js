Auth.requireSession();
paintShell("/expedientes");

const tablaBody = document.getElementById("tablaBody");
const totalCount = document.getElementById("totalCount");
const fBuscar = document.getElementById("fBuscar");
const fEstado = document.getElementById("fEstado");
const fAseguradora = document.getElementById("fAseguradora");

const modalBackdrop = document.getElementById("modalBackdrop");
const modalTitle = document.getElementById("modalTitle");
const expForm = document.getElementById("expForm");
const selAseguradora = document.getElementById("id_aseguradora");
const selJuzgado = document.getElementById("id_juzgado");
const selEstado = document.getElementById("id_estado");

let catalogos = { aseguradoras: [], juzgados: [], estados: [] };
let editandoId = null;
let debounceTimer = null;

async function cargarCatalogos() {
  const [aseguradoras, juzgados, estados] = await Promise.all([
    api("/aseguradoras"),
    api("/juzgados"),
    api("/catalogos/estados"),
  ]);
  catalogos = { aseguradoras, juzgados, estados };

  fAseguradora.innerHTML = `<option value="">Todas las aseguradoras</option>` +
    aseguradoras.map(a => `<option value="${a.id_aseguradora}">${a.nombre}</option>`).join("");

  selAseguradora.innerHTML = aseguradoras.map(a => `<option value="${a.id_aseguradora}">${a.nombre}</option>`).join("");
  selJuzgado.innerHTML = juzgados.map(j => `<option value="${j.id_juzgado}">${j.nombre}</option>`).join("");
  selEstado.innerHTML = estados.map(e => `<option value="${e.id_estado}">${e.nombre}</option>`).join("");
}

function buildQuery() {
  const params = new URLSearchParams();
  if (fBuscar.value.trim()) params.set("q", fBuscar.value.trim());
  if (fEstado.value) params.set("estado", fEstado.value);
  if (fAseguradora.value) params.set("aseguradora", fAseguradora.value);
  const qs = params.toString();
  return qs ? `?${qs}` : "";
}

async function cargarExpedientes() {
  tablaBody.innerHTML = `<tr><td colspan="6" class="empty">Cargando…</td></tr>`;
  try {
    const expedientes = await api(`/expedientes${buildQuery()}`);
    totalCount.textContent = `${expedientes.length} expediente${expedientes.length === 1 ? "" : "s"}`;

    tablaBody.innerHTML = expedientes.length
      ? expedientes.map(filaExpediente).join("")
      : `<tr><td colspan="6" class="empty">No se encontraron expedientes con estos filtros.</td></tr>`;

    tablaBody.querySelectorAll("[data-edit]").forEach(btn => {
      btn.addEventListener("click", () => abrirModalEditar(btn.dataset.edit, expedientes));
    });
    tablaBody.querySelectorAll("[data-delete]").forEach(btn => {
      btn.addEventListener("click", () => eliminarExpediente(btn.dataset.delete));
    });
  } catch (err) {
    tablaBody.innerHTML = `<tr><td colspan="6" class="empty">No se pudo cargar el listado.</td></tr>`;
    toast(err.message, true);
  }
}

function filaExpediente(exp) {
  const slug = statusSlug(exp.estado);
  return `
    <tr>
      <td class="docket">${exp.numero_expediente}</td>
      <td>${exp.asegurado_nombre}</td>
      <td>${exp.aseguradora || "—"}</td>
      <td>${exp.juzgado || "—"}</td>
      <td><span class="pill pill--${slug}">${exp.estado}</span></td>
      <td class="actions">
        <button class="btn btn--ghost btn--sm" data-edit="${exp.id_expediente}">Editar</button>
        <button class="btn btn--wine btn--sm" data-delete="${exp.id_expediente}">Eliminar</button>
      </td>
    </tr>
  `;
}

function abrirModalNuevo() {
  editandoId = null;
  modalTitle.textContent = "Nuevo expediente";
  expForm.reset();
  document.getElementById("btnGuardar").textContent = "Guardar expediente";
  modalBackdrop.classList.add("is-open");
}

function abrirModalEditar(id, expedientesCache) {
  const exp = expedientesCache.find(e => String(e.id_expediente) === String(id));
  if (!exp) return;
  editandoId = id;
  modalTitle.textContent = `Editar expediente ${exp.numero_expediente}`;
  document.getElementById("numero_expediente").value = exp.numero_expediente;
  document.getElementById("numero_expediente").disabled = true;
  document.getElementById("asegurado_nombre").value = exp.asegurado_nombre;
  document.getElementById("descripcion").value = exp.descripcion || "";

  const aseg = catalogos.aseguradoras.find(a => a.nombre === exp.aseguradora);
  const juz = catalogos.juzgados.find(j => j.nombre === exp.juzgado);
  const est = catalogos.estados.find(s => s.nombre === exp.estado);
  if (aseg) selAseguradora.value = aseg.id_aseguradora;
  if (juz) selJuzgado.value = juz.id_juzgado;
  if (est) selEstado.value = est.id_estado;

  document.getElementById("btnGuardar").textContent = "Actualizar expediente";
  modalBackdrop.classList.add("is-open");
}

function cerrarModal() {
  modalBackdrop.classList.remove("is-open");
  document.getElementById("numero_expediente").disabled = false;
  editandoId = null;
}

async function eliminarExpediente(id) {
  if (!confirm("¿Eliminar este expediente? Esta acción no se puede deshacer.")) return;
  try {
    await api(`/expedientes/${id}`, { method: "DELETE" });
    toast("Expediente eliminado");
    cargarExpedientes();
  } catch (err) {
    toast(err.message, true);
  }
}

expForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const payload = {
    asegurado_nombre: document.getElementById("asegurado_nombre").value.trim(),
    id_aseguradora: Number(selAseguradora.value),
    id_juzgado: Number(selJuzgado.value),
    id_estado: Number(selEstado.value),
    descripcion: document.getElementById("descripcion").value.trim(),
  };

  try {
    if (editandoId) {
      await api(`/expedientes/${editandoId}`, { method: "PUT", body: payload });
      toast("Expediente actualizado");
    } else {
      payload.numero_expediente = document.getElementById("numero_expediente").value.trim();
      await api("/expedientes", { method: "POST", body: payload });
      toast("Expediente creado");
    }
    cerrarModal();
    cargarExpedientes();
  } catch (err) {
    toast(err.message, true);
  }
});

document.getElementById("btnNuevo").addEventListener("click", abrirModalNuevo);
document.querySelectorAll("[data-close-modal]").forEach(btn => btn.addEventListener("click", cerrarModal));
modalBackdrop.addEventListener("click", (e) => { if (e.target === modalBackdrop) cerrarModal(); });

fBuscar.addEventListener("input", () => {
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(cargarExpedientes, 300);
});
fEstado.addEventListener("change", cargarExpedientes);
fAseguradora.addEventListener("change", cargarExpedientes);

(async function init() {
  try {
    await cargarCatalogos();
    await cargarExpedientes();
  } catch (err) {
    toast(err.message || "Error al inicializar la página", true);
  }
})();
