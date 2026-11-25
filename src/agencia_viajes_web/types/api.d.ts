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

/* ---------- Venta de boletos ---------- */
export interface ContextoVenta {
    atiende: string;
}

export interface ClienteVenta {
    id_usuario: number;
    nombre_completo: string;
}

export interface CiudadVenta {
    id_ciudad: number;
    nombre: string;
}

export interface PaisVenta {
    id_pais: number;
    nombre: string;
}

export interface ViajeVenta {
    id_viaje: number;
    nombre: string;
    fecha_salida: string;
    fecha_llegada: string;
    costo: number;
    transporte: string;
    asientos_libres: number;
}

export interface AsientoVenta {
    id_asiento: number;
    num_asiento: string;
    ocupado: boolean;
}

export interface VentaCreate {
    id_viaje: number;
    id_cliente: number;
    id_pais_emision: number;
    tipo_documento: string;
    numero_documento: string;
    num_asiento: string;
}

export interface VentaResponse {
    id_boleto: number;
    num_boleto: string;
}
