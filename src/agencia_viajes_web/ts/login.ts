import { CredencialesResponse } from "../types/api";
import { ErrorResponse } from "../types/api";

document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('login-form') as HTMLFormElement | null;
    if (!loginForm) return;

    loginForm.addEventListener('submit', async (event: SubmitEvent) => {
        event.preventDefault();

        const inputCorreo = document.getElementById('txt_correo') as HTMLInputElement | null;
        const inputContrasena = document.getElementById('txt_pass') as HTMLInputElement | null;
        const errorMessage = document.getElementById('error-message') as HTMLElement | null;

        if (!inputCorreo || !inputContrasena) return;

        const correo = inputCorreo.value;
        const contrasena = inputContrasena.value;

        const formData = new URLSearchParams();
        formData.append('correo', correo);
        formData.append('contrasena', contrasena);

        try {
            const response = await fetch('/login/', {
                method: 'POST',
                headers: {
                    'Content-Type':'application/json',
                },
                body: JSON.stringify({correo, contrasena})
            });

            if (response.ok){
                const data: CredencialesResponse = await response.json()
                console.log(`Bienvenido de nuevo, ${data.nombre} ${data.paterno} (${data.tipo_usuario})`);
                switch(data.tipo_usuario){
                    case 'Empleado':
                        window.location.href = '/empleado/dashboard';
                    case 'Cliente':
                        window.location.href = '/dashboard';
                    case 'DBA':
                        window.location.href = '/dba/dashboard'
                }
            } else {
                const errorData: ErrorResponse = await response.json();
                if (errorMessage) {
                    errorMessage.textContent = errorData.detail || 'Credenciales incorrectas';
                }
            }
        } catch (error) {
            console.error('Error de red:', error);
            if (errorMessage) {
                errorMessage.textContent = 'No se pudo conectar con el servidor.';
            }
        }
    });
});