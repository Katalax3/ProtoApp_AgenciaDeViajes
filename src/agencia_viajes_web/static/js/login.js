document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('login-form');
    if (!loginForm)
        return;
    loginForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        const inputCorreo = document.getElementById('txt_correo');
        const inputContrasena = document.getElementById('txt_pass');
        const errorMessage = document.getElementById('error-message');
        if (!inputCorreo || !inputContrasena)
            return;
        const correo = inputCorreo.value;
        const contrasena = inputContrasena.value;
        const formData = new URLSearchParams();
        formData.append('correo', correo);
        formData.append('contrasena', contrasena);
        try {
            const response = await fetch('/login/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ correo, contrasena })
            });
            if (response.ok) {
                const data = await response.json();
                console.log(`Bienvenido de nuevo, ${data.nombre} ${data.paterno} (${data.tipo_usuario})`);
                if (data.tipo_usuario === 'Empleado') {
                    window.location.href = '/empleado/dashboard';
                }
                else {
                    window.location.href = '/dashboard';
                }
            }
            else {
                const errorData = await response.json();
                if (errorMessage) {
                    errorMessage.textContent = errorData.detail || 'Credenciales incorrectas';
                }
            }
        }
        catch (error) {
            console.error('Error de red:', error);
            if (errorMessage) {
                errorMessage.textContent = 'No se pudo conectar con el servidor.';
            }
        }
    });
});
export {};
