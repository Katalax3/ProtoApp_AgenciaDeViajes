document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("login-form");
    const correoInput = document.getElementById("correo");
    const contrasenaInput = document.getElementById("contrasena");
    const errorBanner = document.getElementById("error-message");
    const submitBtn = document.getElementById("submit-btn");
    if (!form || !correoInput || !contrasenaInput || !errorBanner || !submitBtn) {
        return;
    }
    const mostrarError = (mensaje) => {
        errorBanner.textContent = mensaje;
        errorBanner.hidden = false;
    };
    const limpiarError = () => {
        errorBanner.textContent = "";
        errorBanner.hidden = true;
    };
    const alternarCarga = (cargando) => {
        submitBtn.disabled = cargando;
        submitBtn.textContent = cargando ? "Verificando..." : "Entrar";
    };
    form.addEventListener("submit", async (event) => {
        event.preventDefault();
        limpiarError();
        const correo = correoInput.value.trim();
        const contrasena = contrasenaInput.value;
        if (!correo || !contrasena) {
            mostrarError("Por favor, completa todos los campos.");
            return;
        }
        const payload = {
            correo,
            contrasena,
        };
        alternarCarga(true);
        try {
            const response = await fetch("/login/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(payload),
            });
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || "No se pudo iniciar sesión.");
            }
            const usuario = await response.json();
            // Redirección tras guardar la sesión en el backend
            if (usuario.tipo_usuario === "DBA") {
                window.location.href = "/dba/dashboard";
            }
            else if (usuario.tipo_usuario === "Empleado") {
                window.location.href = "/empleado/dashboard";
            }
            else {
                window.location.href = "/cliente/dashboard";
            }
        }
        catch (error) {
            const mensaje = error instanceof Error
                ? error.message
                : "Error de conexión con el servidor.";
            mostrarError(mensaje);
        }
        finally {
            alternarCarga(false);
        }
    });
});
export {};
