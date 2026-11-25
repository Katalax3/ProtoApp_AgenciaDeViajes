const BASE = "/empleado/venta/api";
document.addEventListener("DOMContentLoaded", () => {
    const $ = (id) => document.getElementById(id);
    const fechaHoyEl = $("venta-fecha-hoy");
    const atiendeEl = $("venta-atiende");
    const clienteInput = $("venta-cliente");
    const sugerenciasUl = $("venta-sugerencias");
    const origenSel = $("venta-origen");
    const destinoSel = $("venta-destino");
    const fechaInput = $("venta-fecha");
    const viajesDiv = $("venta-viajes");
    const asientoSel = $("venta-asiento");
    const paisSel = $("venta-pais");
    const tipoDocSel = $("venta-tipo-doc");
    const numDocInput = $("venta-num-doc");
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
    let clienteId = null;
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
        const res = await fetch(url, init);
        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            throw new Error(typeof err.detail === "string" ? err.detail : "Ocurrió un error en el servidor.");
        }
        return res.json();
    };
    // La fecha de salida no puede ser menor a la fecha de hoy del sistema
    const fechaValida = () => fechaInput.value !== "" && fechaInput.value >= hoyISO();
    // ---------- Calendario (se abre al dar clic en cualquier parte del campo) ----------
    const abrirCalendario = () => {
        try {
            fechaInput.showPicker();
        }
        catch { /* el navegador no lo soporta: queda el icono normal */ }
    };
    fechaInput.addEventListener("click", abrirCalendario);
    // ---------- Catálogos ----------
    const cargarCatalogos = async () => {
        try {
            const [ctx, ciudades, paises] = await Promise.all([
                pedir(`${BASE}/contexto`),
                pedir("/empleado/api/ciudades"),
                pedir(`${BASE}/paises`),
            ]);
            atiendeEl.textContent = ctx.atiende;
            const opciones = ciudades.map(c => `<option value="${c.id_ciudad}">${esc(c.nombre)}</option>`).join("");
            origenSel.innerHTML = `<option value="">Selecciona…</option>` + opciones;
            destinoSel.innerHTML = `<option value="">Selecciona…</option>` + opciones;
            paisSel.innerHTML = `<option value="">Selecciona…</option>` +
                paises.map(p => `<option value="${p.id_pais}">${esc(p.nombre)}</option>`).join("");
        }
        catch (e) {
            mensaje(e.message || "No se pudieron cargar los catálogos.", "err");
        }
    };
    // ---------- Cliente: búsqueda por nombre o apellido ----------
    let sugerencias = [];
    let indiceSug = -1;
    let temporizador;
    const cerrarSugerencias = () => {
        sugerenciasUl.hidden = true;
        sugerenciasUl.innerHTML = "";
        sugerencias = [];
        indiceSug = -1;
    };
    const pintarSugerencias = () => {
        if (!sugerencias.length) {
            sugerenciasUl.innerHTML = '<li class="sin">Sin coincidencias</li>';
        }
        else {
            sugerenciasUl.innerHTML = sugerencias.map((c, i) => `<li data-i="${i}" class="${i === indiceSug ? "activo" : ""}">${esc(c.nombre_completo)}</li>`).join("");
        }
        sugerenciasUl.hidden = false;
    };
    const elegirCliente = (c) => {
        clienteInput.value = c.nombre_completo;
        clienteId = c.id_usuario;
        cerrarSugerencias();
    };
    clienteInput.addEventListener("input", () => {
        clienteId = null; // al escribir se invalida la selección anterior
        window.clearTimeout(temporizador);
        const q = clienteInput.value.trim();
        if (!q)
            return cerrarSugerencias();
        temporizador = window.setTimeout(async () => {
            try {
                const r = await pedir(`${BASE}/clientes?q=${encodeURIComponent(q)}`);
                if (clienteInput.value.trim() !== q)
                    return; // llegó una respuesta vieja
                sugerencias = r;
                indiceSug = -1;
                pintarSugerencias();
            }
            catch {
                cerrarSugerencias();
            }
        }, 200);
    });
    clienteInput.addEventListener("keydown", (e) => {
        if (sugerenciasUl.hidden || !sugerencias.length)
            return;
        if (e.key === "ArrowDown") {
            e.preventDefault();
            indiceSug = (indiceSug + 1) % sugerencias.length;
            pintarSugerencias();
        }
        else if (e.key === "ArrowUp") {
            e.preventDefault();
            indiceSug = (indiceSug - 1 + sugerencias.length) % sugerencias.length;
            pintarSugerencias();
        }
        else if (e.key === "Enter" && indiceSug >= 0) {
            e.preventDefault();
            elegirCliente(sugerencias[indiceSug]);
        }
        else if (e.key === "Escape")
            cerrarSugerencias();
    });
    // mousedown (y no click) para que se elija antes de que el input pierda el foco
    sugerenciasUl.addEventListener("mousedown", (e) => {
        const li = e.target.closest("li[data-i]");
        if (!li)
            return;
        e.preventDefault();
        elegirCliente(sugerencias[Number(li.dataset.i)]);
    });
    document.addEventListener("click", (e) => {
        if (e.target !== clienteInput && !sugerenciasUl.contains(e.target))
            cerrarSugerencias();
    });
    // ---------- Asientos disponibles del autobús del viaje elegido ----------
    const pintarAsientos = () => {
        if (!viajeSel) {
            asientoSel.innerHTML = '<option value="">Selecciona un viaje</option>';
            asientoSel.disabled = true;
            return;
        }
        const libres = asientos.filter(a => !a.ocupado);
        asientoSel.disabled = libres.length === 0;
        asientoSel.innerHTML = libres.length
            ? '<option value="">Selecciona…</option>' +
                libres.map(a => `<option value="${esc(a.num_asiento)}">${esc(a.num_asiento)}</option>`).join("")
            : '<option value="">Sin asientos disponibles</option>';
    };
    const cargarAsientos = async (idViaje) => {
        asientos = await pedir(`${BASE}/viajes/${idViaje}/asientos`);
        pintarAsientos();
    };
    // ---------- Lista de viajes ----------
    const vacio = (txt) => {
        viajesDiv.innerHTML = `<div class="venta-vacio">${esc(txt)}</div>`;
    };
    const limpiarSeleccion = () => {
        viajeSel = null;
        asientos = [];
        pintarAsientos();
    };
    const buscarViajes = async () => {
        limpiarSeleccion();
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
        viajesDiv.innerHTML = viajes.map(v => `
            <div class="venta-viaje" data-id="${v.id_viaje}">
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
                    <span>${v.asientos_libres} asientos libres</span>
                </div>
                <div class="venta-precio">${dinero(v.costo)}</div>
                <button type="button" class="btn-sel" data-id="${v.id_viaje}"
                    ${v.asientos_libres <= 0 ? "disabled" : ""}>Seleccionar</button>
            </div>`).join("");
    };
    viajesDiv.addEventListener("click", async (e) => {
        const btn = e.target.closest("button[data-id]");
        if (!btn)
            return;
        const v = viajes.find(x => x.id_viaje === Number(btn.dataset.id));
        if (!v)
            return;
        viajeSel = v;
        viajesDiv.querySelectorAll(".venta-viaje").forEach(r => r.classList.toggle("sel", Number(r.dataset.id) === v.id_viaje));
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
    // ---------- Boleto en PDF ----------
    // El botón "Vender" todavía no hace nada: más adelante llevará a la pestaña de pago.
    btnDescargar.addEventListener("click", async () => {
        if (!clienteInput.value.trim())
            return mensaje("Escribe el nombre del cliente.", "err");
        if (!clienteId)
            return mensaje("Elige un cliente de la lista de resultados.", "err");
        if (!fechaValida())
            return mensaje("Elige la fecha del viaje.", "err");
        if (!viajeSel)
            return mensaje("Selecciona un viaje de la lista.", "err");
        const num = asientoSel.value;
        if (!num)
            return mensaje("Selecciona un asiento.", "err");
        btnDescargar.disabled = true;
        try {
            // Se vuelve a consultar por si otro empleado ocupó el asiento mientras tanto
            await cargarAsientos(viajeSel.id_viaje);
            const a = asientos.find(x => x.num_asiento === num);
            if (!a)
                return mensaje(`El asiento ${num} no existe en este autobús.`, "err");
            if (a.ocupado)
                return mensaje(`El asiento ${num} ya fue ocupado. Elige otro.`, "err");
            const qs = new URLSearchParams({
                id_viaje: String(viajeSel.id_viaje),
                id_cliente: String(clienteId),
                num_asiento: num,
            });
            const res = await fetch(`${BASE}/boleto-pdf?${qs.toString()}`);
            if (!res.ok) {
                const err = await res.json().catch(() => ({}));
                return mensaje(typeof err.detail === "string" ? err.detail : "No se pudo generar el boleto.", "err");
            }
            const url = URL.createObjectURL(await res.blob());
            const enlace = document.createElement("a");
            enlace.href = url;
            enlace.download = "boleto_de_autobus.pdf";
            document.body.appendChild(enlace);
            enlace.click();
            enlace.remove();
            URL.revokeObjectURL(url);
            mensaje("Boleto descargado.", "ok");
        }
        catch (e) {
            mensaje(e.message || "No se pudo generar el boleto.", "err");
        }
        finally {
            btnDescargar.disabled = false;
        }
    });
    const limpiar = () => {
        clienteInput.value = "";
        clienteId = null;
        cerrarSugerencias();
        origenSel.value = "";
        destinoSel.value = "";
        fechaInput.value = hoyISO();
        paisSel.value = "";
        numDocInput.value = "";
        buscarViajes();
    };
    btnCancelar.addEventListener("click", limpiar);
    // ---------- Arranque ----------
    const hoy = new Date();
    fechaHoyEl.textContent = `${pad(hoy.getDate())}/${pad(hoy.getMonth() + 1)}/${hoy.getFullYear()}`;
    fechaInput.min = hoyISO();
    fechaInput.value = hoyISO();
    vacio("Elige origen, destino y fecha para ver los viajes.");
    pintarAsientos();
    cargarCatalogos();
    // La pantalla controla su propio cambio de vista (se ejecuta después del handler del dashboard)
    const sectionDisp = document.getElementById("section-disponibles");
    const sectionCrud = document.getElementById("section-crud");
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
            if (sectionDisp)
                sectionDisp.hidden = true;
            if (sectionCrud)
                sectionCrud.hidden = true;
            if (viewTitle)
                viewTitle.textContent = "Venta de Boletos";
            if (viewSubtitle)
                viewSubtitle.textContent = "Registra la venta de un boleto para un cliente";
            fechaInput.min = hoyISO(); // por si el equipo cambió de día con la pantalla abierta
            if (viajeSel || viajes.length)
                buscarViajes();
        });
    });
});
export {};
