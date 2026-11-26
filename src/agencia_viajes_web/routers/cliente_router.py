from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from psycopg import Connection

from agencia_viajes_web.core.dependencies import require_role
from agencia_viajes_web.core.templates import templates
from agencia_viajes_web.repositories.venta_repo import VentaRepo
from agencia_viajes_web.repositories.viaje_repo import ViajeRepo
# Se reutilizan los modelos, la conexión y el generador de PDF de la venta de empleado
from agencia_viajes_web.routers.venta_router import (
    AsientoOut, PaisOut, PasajeroIn, ViajeVentaOut, _pdf_boletos, db_manager,
)

rol_cliente = require_role("Cliente")

router = APIRouter(
    prefix="/cliente",
    tags=["Cliente"],
    dependencies=[Depends(rol_cliente)],
)


class ContextoClienteOut(BaseModel):
    nombre_completo: str


class CiudadClienteOut(BaseModel):
    id_ciudad: int
    nombre: str


class BoletosPdfCliente(BaseModel):
    id_viaje: int = Field(..., gt=0)
    pasajeros: list[PasajeroIn] = Field(..., min_length=1, max_length=10)


@router.get("/dashboard", response_class=HTMLResponse)
def cliente_dashboard(request: Request):
    return templates.TemplateResponse(request, "cliente_dashboard.html")


@router.get("/venta/api/contexto", response_model=ContextoClienteOut)
def contexto(usuario: dict = Depends(rol_cliente)):
    return {"nombre_completo": f"{usuario['nombre']} {usuario['paterno']}"}


@router.get("/venta/api/ciudades", response_model=list[CiudadClienteOut])
def listar_ciudades(db: Connection = Depends(db_manager.get_db)):
    return ViajeRepo(db).obtener_ciudades()


@router.get("/venta/api/paises", response_model=list[PaisOut])
def listar_paises(db: Connection = Depends(db_manager.get_db)):
    return VentaRepo(db).obtener_paises()


@router.get("/venta/api/viajes", response_model=list[ViajeVentaOut])
def listar_viajes(
    id_ciudad_origen: int = Query(..., gt=0),
    id_ciudad_destino: int = Query(..., gt=0),
    fecha: date = Query(...),
    db: Connection = Depends(db_manager.get_db),
):
    if id_ciudad_origen == id_ciudad_destino:
        raise HTTPException(status_code=400, detail="El origen y el destino deben ser distintos.")
    if fecha < date.today():
        raise HTTPException(status_code=400, detail="La fecha no puede ser menor a la actual.")
    return VentaRepo(db).buscar_viajes(id_ciudad_origen, id_ciudad_destino, fecha)


@router.get("/venta/api/viajes/{id_viaje}/asientos", response_model=list[AsientoOut])
def listar_asientos(id_viaje: int, db: Connection = Depends(db_manager.get_db)):
    return VentaRepo(db).obtener_asientos(id_viaje)


# Boletos con lo elegido en pantalla (todavía no se registra la compra).
# El nombre del cliente sale de la sesión: nunca se recibe del navegador.
@router.post("/venta/api/boleto-pdf")
def pdf_boletos_en_pantalla(
    payload: BoletosPdfCliente,
    usuario: dict = Depends(rol_cliente),
    db: Connection = Depends(db_manager.get_db),
):
    pasajeros = []
    for i, p in enumerate(payload.pasajeros, start=1):
        nombre, paterno = p.nombre.strip(), p.paterno.strip()
        if not nombre or not paterno:
            raise HTTPException(status_code=400, detail=f"Escribe el nombre y apellido paterno del pasajero {i}.")
        pasajeros.append({
            "nombre": nombre,
            "paterno": paterno,
            "materno": (p.materno or "").strip() or None,
            "num_asiento": p.num_asiento.strip(),
        })
    nombre_cliente = f"{usuario['nombre']} {usuario['paterno']}"
    try:
        base, boletos = VentaRepo(db).preparar_boletos(payload.id_viaje, None, pasajeros, nombre_cliente)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return _pdf_boletos(base, boletos)
