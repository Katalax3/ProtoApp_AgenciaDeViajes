export interface CredencialesCreate {
    correo: string;
    contrasena: string;
}

export interface CredencialesResponse {
    nombre: string;
    paterno: string;
    tipo_usuario: string;
}

export interface FastAPIError {
    detail?: string;
}