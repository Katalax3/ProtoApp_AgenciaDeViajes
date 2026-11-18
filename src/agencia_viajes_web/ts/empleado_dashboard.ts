document.addEventListener("DOMContentLoaded", () => {
    const navBtns = document.querySelectorAll<HTMLButtonElement>(".nav-btn");
    const sectionDisponibles = document.getElementById("section-disponibles") as HTMLElement;
    const sectionCrud = document.getElementById("section-crud") as HTMLElement;
    const viewTitle = document.getElementById("view-title") as HTMLHeadingElement;
    const viewSubtitle = document.getElementById("view-subtitle") as HTMLParagraphElement;
    
    const viajesGrid = document.getElementById("viajes-grid") as HTMLDivElement;
    const viajesTbody = document.getElementById("viajes-tbody") as HTMLTableSectionElement;
    
    const modal = document.getElementById("viaje-modal") as HTMLDivElement;
    const openModalBtn = document.getElementById("open-viaje-modal") as HTMLButtonElement;
    const closeModalBtn = document.getElementById("close-viaje-modal") as HTMLButtonElement;
    const viajeForm = document.getElementById("viaje-form") as HTMLFormElement;
    const modalTitle = document.getElementById("viaje-modal-title") as HTMLHeadingElement;

    let editingViajeId: number | null = null;
    let cachedViajes: any[] = [];

    const cambiarVista = (vista: string) => {
        if (vista === "disponibles") {
            sectionDisponibles.hidden = false;
            sectionCrud.hidden = true;
            viewTitle.textContent = "Viajes Disponibles";
            viewSubtitle.textContent = "Consulta la cartelera de viajes activos";
            cargarViajesDisponibles();
        } else {
            sectionDisponibles.hidden = true;
            sectionCrud.hidden = false;
            viewTitle.textContent = "Organizador de Viajes";
            viewSubtitle.textContent = "Administra, crea, actualiza o elimina viajes";
            cargarViajesCrud();
        }
    };

    navBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            navBtns.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            cambiarVista(btn.dataset.view || "disponibles");
        });
    });

    const cargarViajesDisponibles = async () => {
        try {
            const res = await fetch("/empleado/api/viajes");
            cachedViajes = await res.json();
            
            if (!cachedViajes.length) {
                viajesGrid.innerHTML = `<p style="color: var(--text-secondary);">No hay viajes disponibles.</p>`;
                return;
            }

            viajesGrid.innerHTML = cachedViajes.map(v => `
                <div class="viaje-card">
                    <h3>${v.nombre}</h3>
                    <div class="viaje-info"><span>Origen ID: ${v.id_ciudad_origen}</span><span>Destino ID: ${v.id_ciudad_destino}</span></div>
                    <div class="viaje-info"><span>Salida: ${String(v.fecha_salida).replace('T', ' ')}</span></div>
                    <div class="viaje-costo">$${v.costo}</div>
                </div>
            `).join("");
        } catch {
            viajesGrid.innerHTML = `<p style="color: var(--text-secondary);">Error al cargar los viajes.</p>`;
        }
    };

    const cargarViajesCrud = async () => {
        try {
            const res = await fetch("/empleado/api/viajes");
            cachedViajes = await res.json();

            if (!cachedViajes.length) {
                viajesTbody.innerHTML = `<tr><td colspan="8" style="text-align: center; color: var(--text-secondary);">Sin registros</td></tr>`;
                return;
            }

            viajesTbody.innerHTML = cachedViajes.map(v => `
                <tr data-id="${v.id_viaje}" style="cursor: pointer;" title="Haz clic para seleccionar este registro">
                    <td>${v.id_viaje}</td>
                    <td>${v.nombre}</td>
                    <td>${v.id_transporte}</td>
                    <td>${v.id_ciudad_origen}</td>
                    <td>${v.id_ciudad_destino}</td>
                    <td>${String(v.fecha_salida).replace('T', ' ')}</td>
                    <td>$${v.costo}</td>
                    <td style="text-align: right;">
                        <button type="button" class="btn-secondary" style="padding: 0.3rem 0.6rem; font-size: 0.8rem;" data-action="edit" data-id="${v.id_viaje}">Editar</button>
                        <button type="button" class="btn-secondary" style="padding: 0.3rem 0.6rem; font-size: 0.8rem; color: var(--danger); border-color: var(--danger);" data-action="delete" data-id="${v.id_viaje}">Eliminar</button>
                    </td>
                </tr>
            `).join("");
        } catch {
            viajesTbody.innerHTML = `<tr><td colspan="8" style="text-align: center; color: var(--text-secondary);">Error al cargar registros</td></tr>`;
        }
    };

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
        (viajeForm.elements.namedItem("nombre") as HTMLInputElement).value = viaje.nombre ?? "";
        (viajeForm.elements.namedItem("id_transporte") as HTMLInputElement).value = viaje.id_transporte ?? "";
        (viajeForm.elements.namedItem("id_ciudad_origen") as HTMLInputElement).value = viaje.id_ciudad_origen ?? "";
        (viajeForm.elements.namedItem("id_ciudad_destino") as HTMLInputElement).value = viaje.id_ciudad_destino ?? "";
        (viajeForm.elements.namedItem("fecha_salida") as HTMLInputElement).value = viaje.fecha_salida ? viaje.fecha_salida.slice(0, 16) : "";
        (viajeForm.elements.namedItem("fecha_llegada") as HTMLInputElement).value = viaje.fecha_llegada ? viaje.fecha_llegada.slice(0, 16) : "";
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
            nombre: String(data.nombre),
            id_transporte: Number(data.id_transporte),
            id_ciudad_origen: Number(data.id_ciudad_origen),
            id_ciudad_destino: Number(data.id_ciudad_destino),
            fecha_salida: new Date(data.fecha_salida as string).toISOString(),
            fecha_llegada: new Date(data.fecha_llegada as string).toISOString(),
            costo: Number(data.costo),
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
            cargarViajesCrud();
        } catch (error: any) {
            alert(error.message || "Error al guardar el viaje.");
        }
    });

    const eliminarViaje = async (id: number) => {
        if (confirm("¿Estás seguro de eliminar este viaje? Se comprobarán dependencias.")) {
            try {
                const res = await fetch(`/empleado/api/viajes/${id}`, { method: "DELETE" });
                if (!res.ok) {
                    const errData = await res.json().catch(() => ({}));
                    throw new Error(errData.detail || "El viaje tiene reservas u otros elementos asociados y no puede ser eliminado.");
                }
                cargarViajesCrud();
            } catch (error: any) {
                alert(`Advertencia: ${error.message}`);
                
                // Desactivar el botón de eliminar de esta fila específica al detectar dependencias
                const deleteBtn = viajesTbody.querySelector(`button[data-action="delete"][data-id="${id}"]`) as HTMLButtonElement;
                if (deleteBtn) {
                    deleteBtn.disabled = true;
                    deleteBtn.style.opacity = "0.4";
                    deleteBtn.style.cursor = "not-allowed";
                    deleteBtn.title = "No se puede eliminar porque tiene registros dependientes (hijos)";
                }
            }
        }
    };

    cargarViajesDisponibles();
});