Auth.requireSession();
paintShell("/catalogos");

const listaAseguradoras = document.getElementById("listaAseguradoras");
const listaJuzgados = document.getElementById("listaJuzgados");

async function cargarAseguradoras() {
  try {
    const items = await api("/aseguradoras");
    listaAseguradoras.innerHTML = items.length
      ? items.map(a => filaCatalogo(a.nombre, a.telefono, "aseguradora", a.id_aseguradora)).join("")
      : `<div class="empty">Sin aseguradoras registradas.</div>`;
    bindEliminar(listaAseguradoras, "/aseguradoras");
  } catch (err) {
    toast(err.message, true);
  }
}

async function cargarJuzgados() {
  try {
    const items = await api("/juzgados");
    listaJuzgados.innerHTML = items.length
      ? items.map(j => filaCatalogo(j.nombre, j.circuito, "juzgado", j.id_juzgado)).join("")
      : `<div class="empty">Sin juzgados registrados.</div>`;
    bindEliminar(listaJuzgados, "/juzgados");
  } catch (err) {
    toast(err.message, true);
  }
}

function filaCatalogo(nombre, sub, tipo, id) {
  return `
    <div class="agenda-item" data-id="${id}">
      <div class="body" style="flex:1;">
        <div class="t">${nombre}</div>
        ${sub ? `<div class="d">${sub}</div>` : ""}
      </div>
      <button class="btn btn--ghost btn--sm" data-del="${id}">Desactivar</button>
    </div>
  `;
}

function bindEliminar(container, basePath) {
  container.querySelectorAll("[data-del]").forEach(btn => {
    btn.addEventListener("click", async () => {
      if (!confirm("¿Desactivar este registro?")) return;
      try {
        await api(`${basePath}/${btn.dataset.del}`, { method: "DELETE" });
        toast("Registro desactivado");
        cargarAseguradoras();
        cargarJuzgados();
      } catch (err) {
        toast(err.message, true);
      }
    });
  });
}

/* --- Modal aseguradora --- */
const modalAseguradora = document.getElementById("modalAseguradora");
document.getElementById("btnNuevaAseguradora").addEventListener("click", () => {
  document.getElementById("formAseguradora").reset();
  modalAseguradora.classList.add("is-open");
});
document.getElementById("formAseguradora").addEventListener("submit", async (e) => {
  e.preventDefault();
  try {
    await api("/aseguradoras", {
      method: "POST",
      body: {
        nombre: document.getElementById("asegNombre").value.trim(),
        telefono: document.getElementById("asegTelefono").value.trim(),
      },
    });
    toast("Aseguradora creada");
    modalAseguradora.classList.remove("is-open");
    cargarAseguradoras();
  } catch (err) {
    toast(err.message, true);
  }
});

/* --- Modal juzgado --- */
const modalJuzgado = document.getElementById("modalJuzgado");
document.getElementById("btnNuevoJuzgado").addEventListener("click", () => {
  document.getElementById("formJuzgado").reset();
  modalJuzgado.classList.add("is-open");
});
document.getElementById("formJuzgado").addEventListener("submit", async (e) => {
  e.preventDefault();
  try {
    await api("/juzgados", {
      method: "POST",
      body: {
        nombre: document.getElementById("juzNombre").value.trim(),
        circuito: document.getElementById("juzCircuito").value.trim(),
      },
    });
    toast("Juzgado creado");
    modalJuzgado.classList.remove("is-open");
    cargarJuzgados();
  } catch (err) {
    toast(err.message, true);
  }
});

document.querySelectorAll("[data-close-modal]").forEach(btn => {
  btn.addEventListener("click", () => {
    modalAseguradora.classList.remove("is-open");
    modalJuzgado.classList.remove("is-open");
  });
});
[modalAseguradora, modalJuzgado].forEach(m => {
  m.addEventListener("click", (e) => { if (e.target === m) m.classList.remove("is-open"); });
});

cargarAseguradoras();
cargarJuzgados();
