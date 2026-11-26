const BASE = "/cliente/venta/api";
const MAX_PASAJEROS = 10;
const nuevoPasajero = () => ({ nombre: "", paterno: "", materno: "", asiento: "", pais: "", tipo: "INE", numDoc: "" });
document.addEventListener("DOMContentLoaded", () => {
    const $ = (id) => document.getElementById(id);
    const fechaHoyEl = $("venta-fecha-hoy");
    const saludoEl = $("venta-saludo");
    const origenSel = $("venta-origen");
    const destinoSel = $("venta-destino");
    const fechaInput = $("venta-fecha");
    const numPasajerosInput = $("venta-num-pasajeros");
    const btnMenos = $("venta-menos");
    const btnMas = $("venta-mas");
    const viajesDiv = $("venta-viajes");
    const pasajerosDiv = $("venta-pasajeros");
    const msgEl = $("venta-msg");
    const btnVender = $("venta-btn-vender"); // por ahora solo de adorno (después llevará al pago)
    const btnDescargar = $("venta-btn-descargar");
    const btnCancelar = $("venta-btn-cancelar");
    // Si la plantilla no trae la sección, no hacemos nada
    if (!fechaHoyEl || !btnVender)
        return;
    let viajes = [];
    let viajeSel = null;
    let asientos = [];
    let pasajeros = [nuevoPasajero()];
    let paisesHtml = '<option value="">Selecciona…</option>';
    const pad = (n) => String(n).padStart(2, "0");
    // Fecha del sistema operativo del equipo
    const hoyISO = () => {
        const d = new Date();
        return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
    };
    const fmtHora = (iso) => {
        const m = iso.match(/[T ](\d{2}:\d{2})/);
        return m ? m[1] : iso;
    };
    const diaSemana = (iso) => new Date(iso).toLocaleDateString("es-MX", { weekday: "long" });
    const diaMes = (iso) => {
        const d = new Date(iso);
        const mes = d.toLocaleDateString("es-MX", { month: "short" }).replace(".", "");
        return `${d.getDate()} ${mes.charAt(0).toUpperCase()}${mes.slice(1)}`;
    };
    const dinero = (n) => "$" + n.toLocaleString("es-MX", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    const esc = (v) => String(v).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
    const mensaje = (txt, tipo = "") => {
        msgEl.textContent = txt;
        msgEl.className = "venta-msg " + tipo;
    };
    const pedir = async (url, init) => {
        const ruta = new URL(url, window.location.href).pathname;
        const res = await fetch(url, init);
        // Si la sesión venció, el servidor redirige al login y regresa HTML en lugar de JSON
        if (res.redirected || (res.ok && !(res.headers.get("content-type") || "").includes("json"))) {
            throw new Error("tu sesión venció, vuelve a iniciar sesión");
        }
        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            throw new Error(typeof err.detail === "string" ? err.detail : `error ${res.status} en ${ruta}`);
        }
        return res.json();
    };
    // La fecha de salida no puede ser menor a la fecha de hoy del sistema
    const fechaValida = () => fechaInput.value !== "" && fechaInput.value >= hoyISO();
    // ---------- Calendario (se abre al dar clic en cualquier parte del campo) ----------
    fechaInput.addEventListener("click", () => {
        try {
            fechaInput.showPicker();
        }
        catch { /* el navegador no lo soporta: queda el icono normal */ }
    });
    // ---------- Catálogos (cada uno carga por separado: si uno falla, los demás siguen) ----------
    let ciudadesListas = false;
    const cargarCatalogos = async () => {
        const [ctx, ciudades, paises] = await Promise.allSettled([
            pedir(`${BASE}/contexto`),
            pedir(`${BASE}/ciudades`),
            pedir(`${BASE}/paises`),
        ]);
        const fallos = [];
        const motivo = (r) => r.reason?.message || "error desconocido";
        if (ctx.status === "fulfilled")
            saludoEl.textContent = ctx.value.nombre_completo;
        else
            fallos.push(`usuario (${motivo(ctx)})`);
        if (ciudades.status === "fulfilled") {
            const opciones = ciudades.value.map(c => `<option value="${c.id_ciudad}">${esc(c.nombre)}</option>`).join("");
            origenSel.innerHTML = `<option value="">Selecciona…</option>` + opciones;
            destinoSel.innerHTML = `<option value="">Selecciona…</option>` + opciones;
            ciudadesListas = true;
        }
        else {
            const aviso = '<option value="">Error al cargar (ver aviso abajo)</option>';
            origenSel.innerHTML = aviso;
            destinoSel.innerHTML = aviso;
            fallos.push(`ciudades (${motivo(ciudades)})`);
        }
        if (paises.status === "fulfilled") {
            paisesHtml = `<option value="">Selecciona…</option>` +
                paises.value.map(p => `<option value="${p.id_pais}">${esc(p.nombre)}</option>`).join("");
        }
        else {
            paisesHtml = '<option value="">No se pudieron cargar los países</option>';
            fallos.push(`países (${motivo(paises)})`);
        }
        renderPasajeros();
        if (fallos.length) {
            const txt = `No se pudo cargar: ${fallos.join("; ")}.`;
            mensaje(txt, "err");
            vacio(txt);
        }
    };
    // ---------- Pasajeros: un bloque por cada uno ----------
    const renderPasajeros = () => {
        pasajerosDiv.innerHTML = pasajeros.map((p, i) => {
            const campo = (id, etiqueta, control) => `<div class="venta-campo"><label for="venta-p${i}-${id}">${etiqueta}</label>${control}</div>`;
            const texto = (id, valor, max) => `<input id="venta-p${i}-${id}" type="text" data-i="${i}" data-campo="${id}" maxlength="${max}" autocomplete="off" value="${esc(valor)}">`;
            const tipos = ["INE", "Pasaporte", "Licencia"].map(t => `<option value="${t}" ${p.tipo === t ? "selected" : ""}>${t === "Licencia" ? "Licencia de conducir" : t}</option>`).join("");
            return `
            <div class="venta-pasajero">
                <h4>Pasajero ${i + 1}</h4>
                <div class="venta-grid">
                    ${campo("nombre", "Nombre", texto("nombre", p.nombre, 30))}
                    ${campo("paterno", "Apellido paterno", texto("paterno", p.paterno, 30))}
                    ${campo("materno", "Apellido materno (opcional)", texto("materno", p.materno, 30))}
                    ${campo("asiento", "Asiento", `<select id="venta-p${i}-asiento" data-i="${i}" data-campo="asiento"></select>`)}
                    ${campo("pais", "País del documento", `<select id="venta-p${i}-pais" data-i="${i}" data-campo="pais">${paisesHtml}</select>`)}
                    ${campo("tipo", "Tipo de documento", `<select id="venta-p${i}-tipo" data-i="${i}" data-campo="tipo">${tipos}</select>`)}
                    ${campo("numDoc", "No. de documento", texto("numDoc", p.numDoc, 18))}
                </div>
            </div>`;
        }).join("");
        // el país elegido se restaura después de pintar las opciones
        pasajeros.forEach((p, i) => { $(`venta-p${i}-pais`).value = p.pais; });
        pintarAsientos();
    };
    // Cada select de asiento muestra los libres del autobús, sin los que ya eligió otro pasajero
    const pintarAsientos = () => {
        pasajeros.forEach(p => {
            if (p.asiento && !asientos.some(a => a.num_asiento === p.asiento && !a.ocupado))
                p.asiento = "";
        });
        const elegidos = pasajeros.map(p => p.asiento).filter(Boolean);
        pasajeros.forEach((p, i) => {
            const sel = document.getElementById(`venta-p${i}-asiento`);
            if (!sel)
                return;
            if (!viajeSel) {
                sel.innerHTML = '<option value="">Selecciona un viaje</option>';
                sel.disabled = true;
                return;
            }
            const disponibles = asientos.filter(a => !a.ocupado && (a.num_asiento === p.asiento || !elegidos.includes(a.num_asiento)));
            sel.disabled = disponibles.length === 0;
            sel.innerHTML = disponibles.length
                ? '<option value="">Selecciona…</option>' + disponibles.map(a => `<option value="${esc(a.num_asiento)}" ${a.num_asiento === p.asiento ? "selected" : ""}>${esc(a.num_asiento)}</option>`).join("")
                : '<option value="">Sin asientos disponibles</option>';
        });
    };
    const alCambiarCampo = (e) => {
        const el = e.target;
        const i = Number(el.dataset.i);
        const campo = el.dataset.campo;
        if (!campo || Number.isNaN(i) || !pasajeros[i])
            return;
        pasajeros[i][campo] = el.value;
        if (campo === "asiento")
            pintarAsientos();
    };
    pasajerosDiv.addEventListener("input", alCambiarCampo);
    pasajerosDiv.addEventListener("change", alCambiarCampo);
    const cargarAsientos = async (idViaje) => {
        asientos = await pedir(`${BASE}/viajes/${idViaje}/asientos`);
        pintarAsientos();
    };
    // ---------- Contador de pasajeros ----------
    const cambiarPasajeros = (n) => {
        n = Math.min(MAX_PASAJEROS, Math.max(1, n));
        if (n === pasajeros.length)
            return;
        while (pasajeros.length < n)
            pasajeros.push(nuevoPasajero());
        pasajeros.length = n;
        numPasajerosInput.value = String(n);
        if (viajeSel && viajeSel.asientos_libres < n) {
            limpiarSeleccion();
            mensaje("El viaje elegido no tiene asientos suficientes. Elige otro.", "err");
        }
        renderPasajeros();
        pintarViajes();
    };
    btnMas.addEventListener("click", () => cambiarPasajeros(pasajeros.length + 1));
    btnMenos.addEventListener("click", () => cambiarPasajeros(pasajeros.length - 1));
    // ---------- Lista de viajes ----------
    const vacio = (txt) => {
        viajesDiv.innerHTML = `<div class="venta-vacio">${esc(txt)}</div>`;
    };
    function limpiarSeleccion() {
        viajeSel = null;
        asientos = [];
        pasajeros.forEach(p => { p.asiento = ""; });
        pintarAsientos();
    }
    function pintarViajes() {
        if (!viajes.length)
            return;
        const n = pasajeros.length;
        viajesDiv.innerHTML = viajes.map(v => `
            <div class="venta-viaje ${viajeSel?.id_viaje === v.id_viaje ? "sel" : ""}" data-id="${v.id_viaje}">
                <div class="venta-tramo">
                    <small>Salida (${diaSemana(v.fecha_salida)})</small>
                    <strong>${diaMes(v.fecha_salida)}</strong>
                    <span>${fmtHora(v.fecha_salida)}</span>
                </div>
                <span class="venta-flecha">»</span>
                <div class="venta-tramo">
                    <small>Llegada (${diaSemana(v.fecha_llegada)})</small>
                    <strong>${diaMes(v.fecha_llegada)}</strong>
                    <span>${fmtHora(v.fecha_llegada)}</span>
                </div>
                <div class="venta-info">
                    <strong>${esc(v.nombre)}</strong>
                    <span>${esc(v.transporte)}</span>
                    <span>${v.asientos_libres} ${v.asientos_libres === 1 ? "asiento libre" : "asientos libres"}</span>
                </div>
                <div class="venta-precio">${dinero(v.costo * n)}${n > 1 ? `<small>${n} × ${dinero(v.costo)}</small>` : ""}</div>
                <button type="button" class="btn-sel" data-id="${v.id_viaje}"
                    ${v.asientos_libres < n ? "disabled" : ""}>Seleccionar</button>
            </div>`).join("");
    }
    const buscarViajes = async () => {
        limpiarSeleccion();
        viajes = [];
        mensaje("");
        const o = origenSel.value, d = destinoSel.value;
        if (!fechaValida() || !o || !d)
            return vacio("Elige origen, destino y fecha para ver los viajes.");
        if (o === d)
            return vacio("El origen y el destino deben ser distintos.");
        try {
            viajes = await pedir(`${BASE}/viajes?id_ciudad_origen=${o}&id_ciudad_destino=${d}&fecha=${fechaInput.value}`);
        }
        catch (e) {
            return vacio(e.message);
        }
        if (!viajes.length)
            return vacio("No hay viajes para esa ruta y fecha.");
        pintarViajes();
    };
    viajesDiv.addEventListener("click", async (e) => {
        const btn = e.target.closest("button[data-id]");
        if (!btn)
            return;
        const v = viajes.find(x => x.id_viaje === Number(btn.dataset.id));
        if (!v)
            return;
        viajeSel = v;
        pintarViajes();
        mensaje(`Viaje seleccionado: ${fmtHora(v.fecha_salida)}`, "ok");
        try {
            await cargarAsientos(v.id_viaje);
        }
        catch (err) {
            mensaje(err.message, "err");
        }
    });
    origenSel.addEventListener("change", buscarViajes);
    destinoSel.addEventListener("change", buscarViajes);
    fechaInput.addEventListener("change", buscarViajes);
    // ---------- Boletos en PDF (una página por pasajero) ----------
    // El botón "Vender" todavía no hace nada: más adelante llevará a la pestaña de pago.
    btnDescargar.addEventListener("click", async () => {
        if (!fechaValida())
            return mensaje("Elige la fecha del viaje.", "err");
        if (!viajeSel)
            return mensaje("Selecciona un viaje de la lista.", "err");
        if (viajeSel.asientos_libres < pasajeros.length)
            return mensaje("El viaje no tiene asientos suficientes.", "err");
        for (let i = 0; i < pasajeros.length; i++) {
            const p = pasajeros[i];
            if (!p.nombre.trim())
                return mensaje(`Escribe el nombre del pasajero ${i + 1}.`, "err");
            if (!p.paterno.trim())
                return mensaje(`Escribe el apellido paterno del pasajero ${i + 1}.`, "err");
            if (!p.asiento)
                return mensaje(`Selecciona el asiento del pasajero ${i + 1}.`, "err");
        }
        btnDescargar.disabled = true;
        try {
            // Se vuelve a consultar por si otra persona ocupó un asiento mientras tanto
            await cargarAsientos(viajeSel.id_viaje);
            for (let i = 0; i < pasajeros.length; i++) {
                if (!pasajeros[i].asiento)
                    return mensaje(`El asiento del pasajero ${i + 1} ya fue ocupado. Elige otro.`, "err");
            }
            const res = await fetch(`${BASE}/boleto-pdf`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    id_viaje: viajeSel.id_viaje,
                    pasajeros: pasajeros.map(p => ({
                        nombre: p.nombre.trim(),
                        paterno: p.paterno.trim(),
                        materno: p.materno.trim() || null,
                        num_asiento: p.asiento,
                    })),
                }),
            });
            if (!res.ok) {
                const err = await res.json().catch(() => ({}));
                return mensaje(typeof err.detail === "string" ? err.detail : "No se pudo generar el boleto.", "err");
            }
            const url = URL.createObjectURL(await res.blob());
            const enlace = document.createElement("a");
            enlace.href = url;
            enlace.download = pasajeros.length === 1 ? "boleto_de_autobus.pdf" : "boletos_de_autobus.pdf";
            document.body.appendChild(enlace);
            enlace.click();
            enlace.remove();
            URL.revokeObjectURL(url);
            mensaje(pasajeros.length === 1 ? "Boleto descargado." : "Boletos descargados.", "ok");
        }
        catch (e) {
            mensaje(e.message || "No se pudo generar el boleto.", "err");
        }
        finally {
            btnDescargar.disabled = false;
        }
    });
    const limpiar = () => {
        origenSel.value = "";
        destinoSel.value = "";
        fechaInput.value = hoyISO();
        pasajeros = [nuevoPasajero()];
        numPasajerosInput.value = "1";
        renderPasajeros();
        buscarViajes();
    };
    btnCancelar.addEventListener("click", limpiar);
    // ---------- Arranque ----------
    const hoy = new Date();
    fechaHoyEl.textContent = `${pad(hoy.getDate())}/${pad(hoy.getMonth() + 1)}/${hoy.getFullYear()}`;
    fechaInput.min = hoyISO();
    fechaInput.value = hoyISO();
    vacio("Elige origen, destino y fecha para ver los viajes.");
    renderPasajeros();
    cargarCatalogos();
    // Cambio de vista: muestra Venta de Boletos y oculta cualquier otra sección del panel
    const sectionVenta = document.getElementById("section-venta");
    const viewTitle = document.getElementById("view-title");
    const viewSubtitle = document.getElementById("view-subtitle");
    document.querySelectorAll(".nav-btn").forEach(btn => {
        btn.addEventListener("click", () => {
            const esVenta = btn.dataset.view === "venta";
            if (!sectionVenta)
                return;
            sectionVenta.hidden = !esVenta;
            if (!esVenta)
                return;
            document.querySelectorAll(".dashboard-section").forEach(sec => {
                if (sec !== sectionVenta)
                    sec.hidden = true;
            });
            if (viewTitle)
                viewTitle.textContent = "Venta de Boletos";
            if (viewSubtitle)
                viewSubtitle.textContent = "Elige tu viaje, tus asientos y descarga tus boletos";
            fechaInput.min = hoyISO(); // por si el equipo cambió de día con la pantalla abierta
            if (!ciudadesListas)
                cargarCatalogos(); // reintenta si la primera carga falló
            if (viajeSel || viajes.length)
                buscarViajes();
        });
    });
});
export {};
