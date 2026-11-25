document.addEventListener("DOMContentLoaded", () => {
    const navBtns = document.querySelectorAll<HTMLButtonElement>(".nav-btn");
    const sectionDisponibles = document.getElementById("section-disponibles") as HTMLElement;
    const sectionCrud = document.getElementById("section-crud") as HTMLElement;
    const sectionVenta = document.getElementById("section-venta") as HTMLElement;
    const viewTitle = document.getElementById("view-title") as HTMLHeadingElement;
    const viewSubtitle = document.getElementById("view-subtitle") as HTMLParagraphElement;

    const viajesGrid = document.getElementById("viajes-grid") as HTMLDivElement;
    const viajesTbody = document.getElementById("viajes-tbody") as HTMLTableSectionElement;

    const modal = document.getElementById("viaje-modal") as HTMLDivElement;
    const openModalBtn = document.getElementById("open-viaje-modal") as HTMLButtonElement;
    const closeModalBtn = document.getElementById("close-viaje-modal") as HTMLButtonElement;
    const viajeForm = document.getElementById("viaje-form") as HTMLFormElement;
    const modalTitle = document.getElementById("viaje-modal-title") as HTMLHeadingElement;

    // Inputs de búsqueda
    const searchDisponiblesInput = document.getElementById("search-disponibles") as HTMLInputElement;
    const searchCrudInput = document.getElementById("search-crud") as HTMLInputElement;

    let editingViajeId: number | null = null;
    let cachedViajes: any[] = [];

    const safe = (val: any, fallback: string = "&nbsp;"): string => {
        if (val === null || val === undefined || val === "undefined" || val === "null" || val === "") return fallback;
        return String(val);
    };

    const formatearFecha = (valor: unknown): string => {
        if (!valor || valor === "undefined" || valor === "null") return "&nbsp;";
        const strVal = String(valor);
        const match = strVal.match(/^(\d{4})-(\d{2})-(\d{2})[T ](\d{2}):(\d{2})/);
        if (match) {
            const [_, year, month, day, hour, minute] = match;
            return `${day}/${month}/${year} ${hour}:${minute}`;
        }
        return strVal;
    };

    const toDatetimeLocal = (valor: unknown): string => {
        if (!valor || valor === "undefined" || valor === "null") return "";
        const fecha = new Date(String(valor));
        if (!Number.isNaN(fecha.getTime())) {
            const pad = (n: number) => String(n).padStart(2, "0");
            return `${fecha.getFullYear()}-${pad(fecha.getMonth() + 1)}-${pad(fecha.getDate())}T${pad(fecha.getHours())}:${pad(fecha.getMinutes())}`;
        }
        return String(valor).slice(0, 16);
    };

    const cargarOpcionesFormulario = async () => {
        try {
            const [resCiudades, resTransportes] = await Promise.all([
                fetch("/empleado/api/ciudades"),
                fetch("/empleado/api/transportes")
            ]);

            const ciudades = await resCiudades.json();
            const transportes = await resTransportes.json();

            const selectOrigen = viajeForm.elements.namedItem("id_ciudad_origen") as HTMLSelectElement;
            const selectDestino = viajeForm.elements.namedItem("id_ciudad_destino") as HTMLSelectElement;
            const selectTransporte = viajeForm.elements.namedItem("id_transporte") as HTMLSelectElement;

            const ciudadesHtml = ciudades.map((c: any) => `<option value="${c.id_ciudad}">${c.nombre}</option>`).join("");
            selectOrigen.innerHTML = `<option value="">Seleccione Origen</option>` + ciudadesHtml;
            selectDestino.innerHTML = `<option value="">Seleccione Destino</option>` + ciudadesHtml;

            const transportesHtml = transportes.map((t: any) => `<option value="${t.id_transporte}">${t.nombre}</option>`).join("");
            selectTransporte.innerHTML = `<option value="">Seleccione Transporte</option>` + transportesHtml;
        } catch (error) {
            console.error("Error al cargar opciones de los combobox", error);
        }
    };

    // --- LÓGICA DE RENDERIZADO Y FILTRADO ---

    const renderViajesDisponibles = (viajes: any[]) => {
        if (!viajes.length) {
            viajesGrid.innerHTML = `<p style="color: var(--text-secondary);">No se encontraron viajes disponibles.</p>`;
            return;
        }

        viajesGrid.innerHTML = viajes.map(v => {
            const nombreViaje = safe(v.nombre_viaje, "Sin nombre");
            const origenNombre = safe(v.nombre_ciudad_origen, "N/A");
            const destinoNombre = safe(v.nombre_ciudad_destino, "N/A");
            const transporteNombre = safe(v.nombre_transporte, "N/A");
            const salida = formatearFecha(v.fecha_salida);
            const llegada = formatearFecha(v.fecha_llegada);
            const costo = safe(v.costo, "0");

            return `
                <div class="viaje-card">
                    <h3>${nombreViaje}</h3>
                    <div class="viaje-info">
                        <span>Origen: ${origenNombre}</span>
                        <span>Destino: ${destinoNombre}</span>
                    </div>
                    <div class="viaje-info">
                        <span>Transporte: ${transporteNombre}</span>
                    </div>
                    <div class="viaje-info">
                        <span>Salida: ${salida}</span>
                    </div>
                    <div class="viaje-info">
                        <span>Llegada: ${llegada}</span>
                    </div>
                    <div class="viaje-costo">$${costo}</div>
                    
                    <!-- NUEVO BOTÓN PARA DESCARGAR PDF -->
                    <div style="margin-top: 1rem; text-align: right;">
                        <a href="/empleado/api/viajes/${v.id_viaje}/pdf" target="_blank" class="btn-secondary" style="text-decoration: none; padding: 0.4rem 0.8rem; font-size: 0.85rem; display: inline-flex; align-items: center; gap: 5px;">
                            📄 Descargar PDF
                        </a>
                    </div>
                </div>
            `;
        }).join("");
    };

    const renderViajesCrud = (viajes: any[]) => {
        if (!viajes.length) {
            viajesTbody.innerHTML = `<tr><td colspan="12" style="text-align: center; color: var(--text-secondary);">No se encontraron registros</td></tr>`;
            return;
        }

        viajesTbody.innerHTML = viajes.map(v => {
            return `
                <tr data-id="${v.id_viaje}" style="cursor: pointer;" title="Haz clic para seleccionar este registro">
                    <td>${safe(v.id_viaje)}</td>
                    <td>${safe(v.nombre_viaje, "Sin nombre")}</td>
                    <td>${safe(v.id_transporte)}</td>
                    <td>${safe(v.nombre_transporte)}</td>
                    <td>${safe(v.id_ciudad_origen)}</td>
                    <td>${safe(v.nombre_ciudad_origen)}</td>
                    <td>${safe(v.id_ciudad_destino)}</td>
                    <td>${safe(v.nombre_ciudad_destino)}</td>
                    <td>${formatearFecha(v.fecha_salida)}</td>
                    <td>${formatearFecha(v.fecha_llegada)}</td>
                    <td>$${safe(v.costo, "0")}</td>
                    <td style="text-align: right; white-space: nowrap;">
                        <button type="button" class="btn-secondary" style="padding: 0.3rem 0.6rem; font-size: 0.8rem;" data-action="edit" data-id="${v.id_viaje}">Editar</button>
                        <button type="button" class="btn-secondary" style="padding: 0.3rem 0.6rem; font-size: 0.8rem; color: var(--danger); border-color: var(--danger);" data-action="delete" data-id="${v.id_viaje}">Eliminar</button>
                    </td>
                </tr>
            `;
        }).join("");
    };

    const filtrarDisponibles = () => {
        const term = searchDisponiblesInput.value.toLowerCase().trim();
        const filtrados = cachedViajes.filter(v => 
            safe(v.nombre_viaje, "").toLowerCase().includes(term)
        );
        renderViajesDisponibles(filtrados);
    };

    const filtrarCrud = () => {
        const term = searchCrudInput.value.toLowerCase().trim();
        const filtrados = cachedViajes.filter(v => 
            String(v.id_viaje).includes(term) || 
            safe(v.nombre_viaje, "").toLowerCase().includes(term)
        );
        renderViajesCrud(filtrados);
    };

    const fetchViajes = async () => {
        try {
            const res = await fetch("/empleado/api/viajes");
            cachedViajes = await res.json();
            
            // Ejecutar ambos filtros. Dependiendo de la vista activa, uno de los dos se mostrará
            filtrarDisponibles();
            filtrarCrud();
        } catch {
            viajesGrid.innerHTML = `<p style="color: var(--text-secondary);">Error al cargar los viajes.</p>`;
            viajesTbody.innerHTML = `<tr><td colspan="12" style="text-align: center; color: var(--text-secondary);">Error al cargar registros</td></tr>`;
        }
    };

    // Eventos de búsqueda
    searchDisponiblesInput.addEventListener("input", filtrarDisponibles);
    searchCrudInput.addEventListener("input", filtrarCrud);

    const cambiarVista = (vista: string) => {
        sectionDisponibles.hidden = vista !== "disponibles";
        sectionCrud.hidden = vista !== "crud";
        sectionVenta.hidden = vista !== "venta";

        if (vista === "disponibles") {
            viewTitle.textContent = "Viajes Disponibles";
            viewSubtitle.textContent = "Consulta la cartelera de viajes activos";
        } else if (vista === "crud") {
            viewTitle.textContent = "Organizador de Viajes";
            viewSubtitle.textContent = "Administra, crea, actualiza o elimina viajes";
        } else {
            viewTitle.textContent = "Venta de Boletos";
            viewSubtitle.textContent = "Registra la venta de un boleto para un cliente";
        }
        if (vista !== "venta") fetchViajes(); // Refrescar datos al cambiar de vista
    };

    navBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            navBtns.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            cambiarVista(btn.dataset.view || "disponibles");
        });
    });

    viajesTbody.addEventListener("click", (e) => {
        const target = e.target as HTMLElement;
        const btn = target.closest("button");
        const tr = target.closest("tr");
        if (!tr) return;
        const id = Number(tr.dataset.id);

        if (btn) {
            const action = btn.dataset.action;
            if (action === "edit") abrirModalEdicion(id);
            else if (action === "delete") eliminarViaje(id);
            return;
        }

        if (!modal.hidden) {
            cargarViajeEnFormulario(id);
        }
    });

    const cargarViajeEnFormulario = (id: number) => {
        editingViajeId = id;
        const viaje = cachedViajes.find(v => v.id_viaje === id);
        if (!viaje) return;

        modalTitle.textContent = `Editar Viaje (ID: ${id})`;
        (viajeForm.elements.namedItem("nombre") as HTMLInputElement).value = viaje.nombre_viaje || viaje.nombre || "";
        (viajeForm.elements.namedItem("id_transporte") as HTMLSelectElement).value = String(viaje.id_transporte || "");
        (viajeForm.elements.namedItem("id_ciudad_origen") as HTMLSelectElement).value = String(viaje.id_ciudad_origen || "");
        (viajeForm.elements.namedItem("id_ciudad_destino") as HTMLSelectElement).value = String(viaje.id_ciudad_destino || "");
        (viajeForm.elements.namedItem("fecha_salida") as HTMLInputElement).value = toDatetimeLocal(viaje.fecha_salida);
        (viajeForm.elements.namedItem("fecha_llegada") as HTMLInputElement).value = toDatetimeLocal(viaje.fecha_llegada);
        (viajeForm.elements.namedItem("costo") as HTMLInputElement).value = viaje.costo ?? "";
    };

    openModalBtn.addEventListener("click", () => {
        editingViajeId = null;
        modalTitle.textContent = "Registrar Nuevo Viaje";
        viajeForm.reset();
        modal.hidden = false;
        setTimeout(() => {
            const firstInput = viajeForm.querySelector("input");
            if (firstInput) firstInput.focus();
        }, 50);
    });

    closeModalBtn.addEventListener("click", () => modal.hidden = true);

    const abrirModalEdicion = (id: number) => {
        openModalBtn.click();
        cargarViajeEnFormulario(id);
    };

    viajeForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        if (!viajeForm.checkValidity()) {
            viajeForm.reportValidity();
            return;
        }

        const formData = new FormData(viajeForm);
        const data = Object.fromEntries(formData.entries());

        const payload = {
            nombre: String(data.nombre || "Sin nombre"),
            id_transporte: Number(data.id_transporte),
            id_ciudad_origen: Number(data.id_ciudad_origen),
            id_ciudad_destino: Number(data.id_ciudad_destino),
            fecha_salida: data.fecha_salida ? new Date(data.fecha_salida as string).toISOString() : new Date().toISOString(),
            fecha_llegada: data.fecha_llegada ? new Date(data.fecha_llegada as string).toISOString() : new Date().toISOString(),
            costo: Number(data.costo) || 0,
        };

        const url = editingViajeId ? `/empleado/api/viajes/${editingViajeId}` : `/empleado/api/viajes`;
        const method = editingViajeId ? "PUT" : "POST";

        try {
            const res = await fetch(url, {
                method,
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });

            if (!res.ok) {
                const errData = await res.json().catch(() => ({}));
                throw new Error(errData.detail || "No se pudo guardar el viaje.");
            }

            modal.hidden = true;
            fetchViajes(); // Recargar datos tras guardar
        } catch (error: any) {
            alert(error.message || "Error al guardar el viaje.");
        }
    });

    const eliminarViaje = async (id: number) => {
        if (confirm("¿Estás seguro de eliminar este viaje?")) {
            try {
                const res = await fetch(`/empleado/api/viajes/${id}`, { method: "DELETE" });
                if (!res.ok) {
                    const errData = await res.json().catch(() => ({}));
                    throw new Error(errData.detail || "El viaje tiene reservas asociadas.");
                }
                fetchViajes(); // Recargar datos tras eliminar
            } catch (error: any) {
                alert(`Advertencia: ${error.message}`);
                const deleteBtn = viajesTbody.querySelector(`button[data-action="delete"][data-id="${id}"]`) as HTMLButtonElement;
                if (deleteBtn) {
                    deleteBtn.disabled = true;
                    deleteBtn.style.opacity = "0.4";
                }
            }
        }
    };

    // Inicializar
    cargarOpcionesFormulario();
    fetchViajes();
});