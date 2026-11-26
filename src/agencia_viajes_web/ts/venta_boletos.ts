import type {
    AsientoVenta, CiudadVenta, ClienteVenta, ContextoVenta, FastAPIError,
    PaisVenta, ViajeVenta,
} from "../types/api";

const BASE = "/empleado/venta/api";
const MAX_PASAJEROS = 10;

interface PasajeroForm {
    nombre: string;
    paterno: string;
    materno: string;
    asiento: string;
    pais: string;
    tipo: string;
    numDoc: string;
}

const nuevoPasajero = (): PasajeroForm =>
    ({ nombre: "", paterno: "", materno: "", asiento: "", pais: "", tipo: "INE", numDoc: "" });

document.addEventListener("DOMContentLoaded", () => {
    const $ = <T extends HTMLElement>(id: string) => document.getElementById(id) as T;

    const fechaHoyEl = $<HTMLElement>("venta-fecha-hoy");
    const atiendeEl = $<HTMLElement>("venta-atiende");
    const clienteInput = $<HTMLInputElement>("venta-cliente");
    const sugerenciasUl = $<HTMLUListElement>("venta-sugerencias");
    const origenSel = $<HTMLSelectElement>("venta-origen");
    const destinoSel = $<HTMLSelectElement>("venta-destino");
    const fechaInput = $<HTMLInputElement>("venta-fecha");
    const numPasajerosInput = $<HTMLInputElement>("venta-num-pasajeros");
    const btnMenos = $<HTMLButtonElement>("venta-menos");
    const btnMas = $<HTMLButtonElement>("venta-mas");
    const viajesDiv = $<HTMLDivElement>("venta-viajes");
    const pasajerosDiv = $<HTMLDivElement>("venta-pasajeros");
    const msgEl = $<HTMLDivElement>("venta-msg");
    const btnVender = $<HTMLButtonElement>("venta-btn-vender"); // por ahora solo de adorno (después llevará al pago)
    const btnDescargar = $<HTMLButtonElement>("venta-btn-descargar");
    const btnCancelar = $<HTMLButtonElement>("venta-btn-cancelar");

    // Si la plantilla no trae la sección, no hacemos nada
    if (!fechaHoyEl || !btnVender) return;

    let viajes: ViajeVenta[] = [];
    let viajeSel: ViajeVenta | null = null;
    let asientos: AsientoVenta[] = [];
    let clienteId: number | null = null;
    let pasajeros: PasajeroForm[] = [nuevoPasajero()];
    let paisesHtml = '<option value="">Selecciona…</option>';

    const pad = (n: number) => String(n).padStart(2, "0");
    // Fecha del sistema operativo del equipo
    const hoyISO = (): string => {
        const d = new Date();
        return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
    };
    const fmtHora = (iso: string): string => {
        const m = iso.match(/[T ](\d{2}:\d{2})/);
        return m ? m[1] : iso;
    };
    const diaSemana = (iso: string): string => new Date(iso).toLocaleDateString("es-MX", { weekday: "long" });
    const diaMes = (iso: string): string => {
        const d = new Date(iso);
        const mes = d.toLocaleDateString("es-MX", { month: "short" }).replace(".", "");
        return `${d.getDate()} ${mes.charAt(0).toUpperCase()}${mes.slice(1)}`;
    };
    const dinero = (n: number): string =>
        "$" + n.toLocaleString("es-MX", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    const esc = (v: unknown): string =>
        String(v).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c] as string));

    const mensaje = (txt: string, tipo: "ok" | "err" | "" = ""): void => {
        msgEl.textContent = txt;
        msgEl.className = "venta-msg " + tipo;
    };

    const pedir = async <T>(url: string, init?: RequestInit): Promise<T> => {
        const ruta = new URL(url, window.location.href).pathname;
        const res = await fetch(url, init);
        // Si la sesión venció, el servidor redirige al login y regresa HTML en lugar de JSON
        if (res.redirected || (res.ok && !(res.headers.get("content-type") || "").includes("json"))) {
            throw new Error("tu sesión venció, vuelve a iniciar sesión");
        }
        if (!res.ok) {
            const err: FastAPIError = await res.json().catch(() => ({}));
            throw new Error(typeof err.detail === "string" ? err.detail : `error ${res.status} en ${ruta}`);
        }
        return res.json() as Promise<T>;
    };

    // La fecha de salida no puede ser menor a la fecha de hoy del sistema
    const fechaValida = (): boolean => fechaInput.value !== "" && fechaInput.value >= hoyISO();

    // ---------- Calendario (se abre al dar clic en cualquier parte del campo) ----------
    fechaInput.addEventListener("click", () => {
        try { fechaInput.showPicker(); } catch { /* el navegador no lo soporta: queda el icono normal */ }
    });

    // ---------- Catálogos (cada uno carga por separado: si uno falla, los demás siguen) ----------
    let ciudadesListas = false;
    const cargarCatalogos = async (): Promise<void> => {
        const [ctx, ciudades, paises] = await Promise.allSettled([
            pedir<ContextoVenta>(`${BASE}/contexto`),
            pedir<CiudadVenta[]>("/empleado/api/ciudades"),
            pedir<PaisVenta[]>(`${BASE}/paises`),
        ]);
        const fallos: string[] = [];
        const motivo = (r: PromiseRejectedResult): string => (r.reason as Error)?.message || "error desconocido";

        if (ctx.status === "fulfilled") atiendeEl.textContent = ctx.value.atiende;
        else fallos.push(`usuario (${motivo(ctx)})`);

        if (ciudades.status === "fulfilled") {
            const opciones = ciudades.value.map(c => `<option value="${c.id_ciudad}">${esc(c.nombre)}</option>`).join("");
            origenSel.innerHTML = `<option value="">Selecciona…</option>` + opciones;
            destinoSel.innerHTML = `<option value="">Selecciona…</option>` + opciones;
            ciudadesListas = true;
        } else {
            const aviso = '<option value="">Error al cargar (ver aviso abajo)</option>';
            origenSel.innerHTML = aviso;
            destinoSel.innerHTML = aviso;
            fallos.push(`ciudades (${motivo(ciudades)})`);
        }

        if (paises.status === "fulfilled") {
            paisesHtml = `<option value="">Selecciona…</option>` +
                paises.value.map(p => `<option value="${p.id_pais}">${esc(p.nombre)}</option>`).join("");
        } else {
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

    // ---------- Cliente: búsqueda por nombre o apellido ----------
    let sugerencias: ClienteVenta[] = [];
    let indiceSug = -1;
    let temporizador: number | undefined;

    const cerrarSugerencias = (): void => {
        sugerenciasUl.hidden = true;
        sugerenciasUl.innerHTML = "";
        sugerencias = [];
        indiceSug = -1;
    };

    const pintarSugerencias = (): void => {
        if (!sugerencias.length) {
            sugerenciasUl.innerHTML = '<li class="sin">Sin coincidencias</li>';
        } else {
            sugerenciasUl.innerHTML = sugerencias.map((c, i) =>
                `<li data-i="${i}" class="${i === indiceSug ? "activo" : ""}">${esc(c.nombre_completo)}</li>`).join("");
        }
        sugerenciasUl.hidden = false;
    };

    const elegirCliente = (c: ClienteVenta): void => {
        clienteInput.value = c.nombre_completo;
        clienteId = c.id_usuario;
        cerrarSugerencias();
    };

    clienteInput.addEventListener("input", () => {
        clienteId = null; // al escribir se invalida la selección anterior
        window.clearTimeout(temporizador);
        const q = clienteInput.value.trim();
        if (!q) return cerrarSugerencias();
        temporizador = window.setTimeout(async () => {
            try {
                const r = await pedir<ClienteVenta[]>(`${BASE}/clientes?q=${encodeURIComponent(q)}`);
                if (clienteInput.value.trim() !== q) return; // llegó una respuesta vieja
                sugerencias = r;
                indiceSug = -1;
                pintarSugerencias();
            } catch {
                cerrarSugerencias();
            }
        }, 200);
    });

    clienteInput.addEventListener("keydown", (e) => {
        if (sugerenciasUl.hidden || !sugerencias.length) return;
        if (e.key === "ArrowDown") { e.preventDefault(); indiceSug = (indiceSug + 1) % sugerencias.length; pintarSugerencias(); }
        else if (e.key === "ArrowUp") { e.preventDefault(); indiceSug = (indiceSug - 1 + sugerencias.length) % sugerencias.length; pintarSugerencias(); }
        else if (e.key === "Enter" && indiceSug >= 0) { e.preventDefault(); elegirCliente(sugerencias[indiceSug]); }
        else if (e.key === "Escape") cerrarSugerencias();
    });

    // mousedown (y no click) para que se elija antes de que el input pierda el foco
    sugerenciasUl.addEventListener("mousedown", (e) => {
        const li = (e.target as HTMLElement).closest<HTMLLIElement>("li[data-i]");
        if (!li) return;
        e.preventDefault();
        elegirCliente(sugerencias[Number(li.dataset.i)]);
    });
    document.addEventListener("click", (e) => {
        if (e.target !== clienteInput && !sugerenciasUl.contains(e.target as Node)) cerrarSugerencias();
    });

    // ---------- Pasajeros: un bloque por cada uno ----------
    const renderPasajeros = (): void => {
        pasajerosDiv.innerHTML = pasajeros.map((p, i) => {
            const campo = (id: string, etiqueta: string, control: string) =>
                `<div class="venta-campo"><label for="venta-p${i}-${id}">${etiqueta}</label>${control}</div>`;
            const texto = (id: string, valor: string, max: number) =>
                `<input id="venta-p${i}-${id}" type="text" data-i="${i}" data-campo="${id}" maxlength="${max}" autocomplete="off" value="${esc(valor)}">`;
            const tipos = ["INE", "Pasaporte", "Licencia"].map(t =>
                `<option value="${t}" ${p.tipo === t ? "selected" : ""}>${t === "Licencia" ? "Licencia de conducir" : t}</option>`).join("");
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
        pasajeros.forEach((p, i) => { $<HTMLSelectElement>(`venta-p${i}-pais`).value = p.pais; });
        pintarAsientos();
    };

    // Cada select de asiento muestra los libres del autobús, sin los que ya eligió otro pasajero
    const pintarAsientos = (): void => {
        pasajeros.forEach(p => {
            if (p.asiento && !asientos.some(a => a.num_asiento === p.asiento && !a.ocupado)) p.asiento = "";
        });
        const elegidos = pasajeros.map(p => p.asiento).filter(Boolean);
        pasajeros.forEach((p, i) => {
            const sel = document.getElementById(`venta-p${i}-asiento`) as HTMLSelectElement | null;
            if (!sel) return;
            if (!viajeSel) {
                sel.innerHTML = '<option value="">Selecciona un viaje</option>';
                sel.disabled = true;
                return;
            }
            const disponibles = asientos.filter(a => !a.ocupado && (a.num_asiento === p.asiento || !elegidos.includes(a.num_asiento)));
            sel.disabled = disponibles.length === 0;
            sel.innerHTML = disponibles.length
                ? '<option value="">Selecciona…</option>' + disponibles.map(a =>
                    `<option value="${esc(a.num_asiento)}" ${a.num_asiento === p.asiento ? "selected" : ""}>${esc(a.num_asiento)}</option>`).join("")
                : '<option value="">Sin asientos disponibles</option>';
        });
    };

    const alCambiarCampo = (e: Event): void => {
        const el = e.target as HTMLInputElement | HTMLSelectElement;
        const i = Number(el.dataset.i);
        const campo = el.dataset.campo as keyof PasajeroForm | undefined;
        if (!campo || Number.isNaN(i) || !pasajeros[i]) return;
        pasajeros[i][campo] = el.value;
        if (campo === "asiento") pintarAsientos();
    };
    pasajerosDiv.addEventListener("input", alCambiarCampo);
    pasajerosDiv.addEventListener("change", alCambiarCampo);

    const cargarAsientos = async (idViaje: number): Promise<void> => {
        asientos = await pedir<AsientoVenta[]>(`${BASE}/viajes/${idViaje}/asientos`);
        pintarAsientos();
    };

    // ---------- Contador de pasajeros ----------
    const cambiarPasajeros = (n: number): void => {
        n = Math.min(MAX_PASAJEROS, Math.max(1, n));
        if (n === pasajeros.length) return;
        while (pasajeros.length < n) pasajeros.push(nuevoPasajero());
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
    const vacio = (txt: string): void => {
        viajesDiv.innerHTML = `<div class="venta-vacio">${esc(txt)}</div>`;
    };

    function limpiarSeleccion(): void {
        viajeSel = null;
        asientos = [];
        pasajeros.forEach(p => { p.asiento = ""; });
        pintarAsientos();
    }

    function pintarViajes(): void {
        if (!viajes.length) return;
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

    const buscarViajes = async (): Promise<void> => {
        limpiarSeleccion();
        viajes = [];
        mensaje("");
        const o = origenSel.value, d = destinoSel.value;
        if (!fechaValida() || !o || !d) return vacio("Elige origen, destino y fecha para ver los viajes.");
        if (o === d) return vacio("El origen y el destino deben ser distintos.");
        try {
            viajes = await pedir<ViajeVenta[]>(
                `${BASE}/viajes?id_ciudad_origen=${o}&id_ciudad_destino=${d}&fecha=${fechaInput.value}`
            );
        } catch (e) {
            return vacio((e as Error).message);
        }
        if (!viajes.length) return vacio("No hay viajes para esa ruta y fecha.");
        pintarViajes();
    };

    viajesDiv.addEventListener("click", async (e) => {
        const btn = (e.target as HTMLElement).closest<HTMLButtonElement>("button[data-id]");
        if (!btn) return;
        const v = viajes.find(x => x.id_viaje === Number(btn.dataset.id));
        if (!v) return;
        viajeSel = v;
        pintarViajes();
        mensaje(`Viaje seleccionado: ${fmtHora(v.fecha_salida)}`, "ok");
        try {
            await cargarAsientos(v.id_viaje);
        } catch (err) {
            mensaje((err as Error).message, "err");
        }
    });

    origenSel.addEventListener("change", buscarViajes);
    destinoSel.addEventListener("change", buscarViajes);
    fechaInput.addEventListener("change", buscarViajes);

    // ---------- Boletos en PDF (una página por pasajero) ----------
    // El botón "Vender" todavía no hace nada: más adelante llevará a la pestaña de pago.
    btnDescargar.addEventListener("click", async () => {
        if (!clienteInput.value.trim()) return mensaje("Escribe el nombre del cliente.", "err");
        if (!clienteId) return mensaje("Elige un cliente de la lista de resultados.", "err");
        if (!fechaValida()) return mensaje("Elige la fecha del viaje.", "err");
        if (!viajeSel) return mensaje("Selecciona un viaje de la lista.", "err");
        if (viajeSel.asientos_libres < pasajeros.length) return mensaje("El viaje no tiene asientos suficientes.", "err");
        for (let i = 0; i < pasajeros.length; i++) {
            const p = pasajeros[i];
            if (!p.nombre.trim()) return mensaje(`Escribe el nombre del pasajero ${i + 1}.`, "err");
            if (!p.paterno.trim()) return mensaje(`Escribe el apellido paterno del pasajero ${i + 1}.`, "err");
            if (!p.asiento) return mensaje(`Selecciona el asiento del pasajero ${i + 1}.`, "err");
        }

        btnDescargar.disabled = true;
        try {
            // Se vuelve a consultar por si otro empleado ocupó un asiento mientras tanto
            await cargarAsientos(viajeSel.id_viaje);
            for (let i = 0; i < pasajeros.length; i++) {
                if (!pasajeros[i].asiento) return mensaje(`El asiento del pasajero ${i + 1} ya fue ocupado. Elige otro.`, "err");
            }

            const res = await fetch(`${BASE}/boleto-pdf`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    id_viaje: viajeSel.id_viaje,
                    id_cliente: clienteId,
                    pasajeros: pasajeros.map(p => ({
                        nombre: p.nombre.trim(),
                        paterno: p.paterno.trim(),
                        materno: p.materno.trim() || null,
                        num_asiento: p.asiento,
                    })),
                }),
            });
            if (!res.ok) {
                const err: FastAPIError = await res.json().catch(() => ({}));
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
        } catch (e) {
            mensaje((e as Error).message || "No se pudo generar el boleto.", "err");
        } finally {
            btnDescargar.disabled = false;
        }
    });

    const limpiar = (): void => {
        clienteInput.value = "";
        clienteId = null;
        cerrarSugerencias();
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

    // La pantalla controla su propio cambio de vista (se ejecuta después del handler del dashboard)
    const sectionDisp = document.getElementById("section-disponibles");
    const sectionCrud = document.getElementById("section-crud");
    const sectionVenta = document.getElementById("section-venta");
    const viewTitle = document.getElementById("view-title");
    const viewSubtitle = document.getElementById("view-subtitle");
    document.querySelectorAll<HTMLButtonElement>(".nav-btn").forEach(btn => {
        btn.addEventListener("click", () => {
            const esVenta = btn.dataset.view === "venta";
            if (!sectionVenta) return;
            sectionVenta.hidden = !esVenta;
            if (!esVenta) return;
            if (sectionDisp) sectionDisp.hidden = true;
            if (sectionCrud) sectionCrud.hidden = true;
            if (viewTitle) viewTitle.textContent = "Venta de Boletos";
            if (viewSubtitle) viewSubtitle.textContent = "Registra la venta de un boleto para un cliente";
            fechaInput.min = hoyISO(); // por si el equipo cambió de día con la pantalla abierta
            if (!ciudadesListas) cargarCatalogos(); // reintenta si la primera carga falló
            if (viajeSel || viajes.length) buscarViajes();
        });
    });
});
