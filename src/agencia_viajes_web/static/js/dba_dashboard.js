"use strict";
document.addEventListener("DOMContentLoaded", () => {
    const navBtns = document.querySelectorAll(".nav-btn");
    const tableTitle = document.getElementById("table-title");
    const tableHeadRow = document.getElementById("table-head-row");
    const tableBody = document.getElementById("table-body");
    const modal = document.getElementById("record-modal");
    const openModalBtn = document.getElementById("open-create-modal");
    const closeModalBtn = document.getElementById("close-modal");
    const recordForm = document.getElementById("record-form");
    const formFields = document.getElementById("form-fields");
    const modalTitle = document.getElementById("modal-title");
    const searchInput = document.getElementById("search-input");
    const searchBtn = document.getElementById("search-btn");
    let currentTable = "pais";
    let editingId = null;
    let cachedData = [];
    const tableConfigs = {
        pais: {
            title: "Gestión de Países",
            pk: "id_pais",
            fields: [
                { name: "iso_alfa3", label: "ISO Alfa-3", maxlength: 3 },
                { name: "nombre", label: "Nombre", maxlength: 30 }
            ]
        },
        parcialidad: {
            title: "Gestión de Parcialidades",
            pk: "id_parcialidad",
            fields: [
                { name: "id_factura", label: "ID Factura", type: "number", min: 1 },
                { name: "num_parcia", label: "Número Parcialidad", type: "number", min: 1 },
                { name: "fecha_vencimiento", label: "Vencimiento", type: "date" },
                { name: "total_parcia", label: "Total Parcialidad", type: "number", min: 0.01, step: "0.01" }
            ]
        },
        banco: {
            title: "Gestión de Bancos",
            pk: "id_banco",
            fields: [
                { name: "nombre", label: "Nombre del Banco", maxlength: 30 }
            ]
        }
    };
    const cargarDatos = async (filtro = "") => {
        try {
            const res = await fetch(`/dba/api/${currentTable}`);
            if (!res.ok)
                throw new Error("Error al obtener registros");
            cachedData = await res.json();
            renderizarTabla(cachedData, filtro);
        }
        catch {
            cachedData = [];
            renderizarTabla([], filtro);
        }
    };
    const renderizarTabla = (data, filtro) => {
        const config = tableConfigs[currentTable];
        tableTitle.textContent = config.title;
        tableHeadRow.innerHTML = `
            <th>ID</th>
            ${config.fields.map(f => `<th>${f.label}</th>`).join("")}
            <th style="text-align: right;">Acciones</th>
        `;
        const filtrados = data.filter(row => {
            if (!filtro)
                return true;
            return Object.values(row).some(val => String(val).toLowerCase().includes(filtro.toLowerCase()));
        });
        if (!filtrados.length) {
            tableBody.innerHTML = `<tr><td colspan="${config.fields.length + 2}" style="text-align: center; color: var(--text-secondary);">No hay registros</td></tr>`;
            return;
        }
        tableBody.innerHTML = filtrados.map(row => {
            const recordId = row[config.pk];
            return `
                <tr data-id="${recordId}" style="cursor: pointer;" title="Haz clic para seleccionar este registro">
                    <td>${recordId}</td>
                    ${config.fields.map(f => `<td>${row[f.name] ?? ""}</td>`).join("")}
                    <td style="text-align: right;">
                        <button type="button" class="btn-secondary" style="padding: 0.3rem 0.6rem; font-size: 0.8rem;" data-action="edit" data-id="${recordId}">Editar</button>
                        <button type="button" class="btn-secondary" style="padding: 0.3rem 0.6rem; font-size: 0.8rem; color: var(--danger); border-color: var(--danger);" data-action="delete" data-id="${recordId}">Eliminar</button>
                    </td>
                </tr>
            `;
        }).join("");
    };
    tableBody.addEventListener("click", (e) => {
        const target = e.target;
        const btn = target.closest("button");
        const tr = target.closest("tr");
        if (!tr)
            return;
        const id = Number(tr.dataset.id);
        if (btn) {
            const action = btn.dataset.action;
            if (action === "edit")
                abrirModalEdicion(id);
            else if (action === "delete")
                eliminarRegistro(id);
            return;
        }
        if (!modal.hidden && editingId !== null) {
            cargarDatosEnFormulario(id);
        }
    });
    const cargarDatosEnFormulario = (id) => {
        const config = tableConfigs[currentTable];
        const record = cachedData.find(r => r[config.pk] === id);
        if (!record)
            return;
        editingId = id;
        modalTitle.textContent = `Registro encontrado (${config.pk}: ${id})`;
        config.fields.forEach(f => {
            const input = recordForm.elements.namedItem(f.name);
            if (input)
                input.value = record[f.name] ?? "";
        });
    };
    navBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            navBtns.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            currentTable = btn.dataset.table || "pais";
            searchInput.value = "";
            cargarDatos();
        });
    });
    openModalBtn.addEventListener("click", () => {
        editingId = null;
        modalTitle.textContent = `Nuevo registro en ${tableConfigs[currentTable].title}`;
        const config = tableConfigs[currentTable];
        formFields.innerHTML = config.fields.map((f, index) => `
            <div>
                <label style="font-size: 0.8rem; color: var(--text-secondary); display: block; margin-bottom: 0.3rem;">${f.label}</label>
                <input 
                    type="${f.type || 'text'}" 
                    name="${f.name}" 
                    ${f.maxlength ? `maxlength="${f.maxlength}"` : ''} 
                    ${f.min !== undefined ? `min="${f.min}"` : ''} 
                    ${f.step ? `step="${f.step}"` : ''} 
                    required 
                    placeholder="Ingrese ${f.label.toLowerCase()}"
                    tabindex="${index + 1}"
                >
            </div>
        `).join("");
        recordForm.reset();
        modal.hidden = false;
        setTimeout(() => {
            const firstInput = formFields.querySelector("input");
            if (firstInput)
                firstInput.focus();
        }, 50);
    });
    closeModalBtn.addEventListener("click", () => modal.hidden = true);
    const abrirModalEdicion = (id) => {
        openModalBtn.click();
        cargarDatosEnFormulario(id);
    };
    recordForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        if (!recordForm.checkValidity()) {
            recordForm.reportValidity();
            return;
        }
        const formData = new FormData(recordForm);
        const rawData = Object.fromEntries(formData.entries());
        const config = tableConfigs[currentTable];
        const data = {};
        config.fields.forEach(f => {
            if (rawData[f.name] !== undefined) {
                data[f.name] = f.type === 'number' ? Number(rawData[f.name]) : rawData[f.name];
            }
        });
        const url = editingId ? `/dba/api/${currentTable}/${editingId}` : `/dba/api/${currentTable}`;
        const method = editingId ? "PUT" : "POST";
        try {
            const res = await fetch(url, {
                method,
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(data)
            });
            if (!res.ok) {
                const errData = await res.json().catch(() => ({}));
                throw new Error(errData.detail || "No se pudo guardar el registro.");
            }
            modal.hidden = true;
            cargarDatos();
        }
        catch (error) {
            alert(error.message || "Error al procesar la solicitud.");
        }
    });
    const eliminarRegistro = async (id) => {
        if (confirm("¿Estás seguro de eliminar este registro? Se verificarán restricciones de integridad.")) {
            try {
                const res = await fetch(`/dba/api/${currentTable}/${id}`, { method: "DELETE" });
                if (!res.ok) {
                    const errData = await res.json().catch(() => ({}));
                    throw new Error(errData.detail || "El registro tiene elementos dependientes (hijos) y no puede ser eliminado.");
                }
                cargarDatos();
            }
            catch (error) {
                alert(`Advertencia: ${error.message}`);
                // Desactivar el botón de eliminar de esta fila específica al detectar hijos
                const deleteBtn = tableBody.querySelector(`button[data-action="delete"][data-id="${id}"]`);
                if (deleteBtn) {
                    deleteBtn.disabled = true;
                    deleteBtn.style.opacity = "0.4";
                    deleteBtn.style.cursor = "not-allowed";
                    deleteBtn.title = "No se puede eliminar porque tiene registros dependientes (hijos)";
                }
            }
        }
    };
    searchBtn.addEventListener("click", () => cargarDatos(searchInput.value.trim()));
    searchInput.addEventListener("keyup", (e) => { if (e.key === "Enter")
        cargarDatos(searchInput.value.trim()); });
    cargarDatos();
});
