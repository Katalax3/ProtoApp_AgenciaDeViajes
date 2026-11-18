import { CredencialesResponse } from "../types/api";
import { FastAPIError } from "../types/api";
import { CredencialesCreate } from "../types/api";

document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("login-form") as HTMLFormElement | null;
    const correoInput = document.getElementById("correo") as HTMLInputElement | null;
    const contrasenaInput = document.getElementById("contrasena") as HTMLInputElement | null;
    const errorBanner = document.getElementById("error-message") as HTMLDivElement | null;
    const submitBtn = document.getElementById("submit-btn") as HTMLButtonElement | null;

    if (!form || !correoInput || !contrasenaInput || !errorBanner || !submitBtn) {
        return;
    }

    const mostrarError = (mensaje: string): void => {
        errorBanner.textContent = mensaje;
        errorBanner.hidden = false;
    };

    const limpiarError = (): void => {
        errorBanner.textContent = "";
        errorBanner.hidden = true;
    };

    const alternarCarga = (cargando: boolean): void => {
        submitBtn.disabled = cargando;
        submitBtn.textContent = cargando ? "Verificando..." : "Entrar";
    };

    form.addEventListener("submit", async (event: SubmitEvent) => {
        event.preventDefault();
        limpiarError();

        const correo = correoInput.value.trim();
        const contrasena = contrasenaInput.value;

        if (!correo || !contrasena) {
            mostrarError("Por favor, completa todos los campos.");
            return;
        }

        const payload: CredencialesCreate = {
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
                const errorData: FastAPIError = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || "No se pudo iniciar sesión.");
            }

            const usuario: CredencialesResponse = await response.json();

            // Redirección tras guardar la sesión en el backend
            if (usuario.tipo_usuario === "DBA") {
                window.location.href = "/dba/dashboard";
            } else if(usuario.tipo_usuario === "Empleado") {
                window.location.href = "/empleado/dashboard";
            } else {
                window.location.href = "/cliente/dashboard"
            }
        } catch (error) {
            const mensaje =
                error instanceof Error
                    ? error.message
                    : "Error de conexión con el servidor.";
            mostrarError(mensaje);
        } finally {
            alternarCarga(false);
        }
    });
});