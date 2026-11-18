from typing import Any
from fastapi.responses import HTMLResponse
from agencia_viajes_web.core.dependencies import require_role
from fastapi import APIRouter, Depends, HTTPException, Request
from agencia_viajes_web.core.templates import templates
from agencia_viajes_web import Conexion
from agencia_viajes_web.repositories.viaje_repo import ViajeRepo
from psycopg import Connection

router = APIRouter(
    prefix="/empleado", dependencies=[Depends(require_role("Empleado"))], tags=["Empleado"]
)

db_manager = Conexion()

@router.get("/dashboard", response_class=HTMLResponse)
def empleado_dashboard(request: Request):
    return templates.TemplateResponse(request, "empleado_dashboard.html")

@router.get("/api/viajes")
def obtener_viajes(db: Connection = Depends(db_manager.get_db)):
    repo = ViajeRepo(db)
    return repo.obtener_todos()

@router.post("/api/viajes")
def crear_viaje(datos: dict[str, Any], db: Connection = Depends(db_manager.get_db)):
    repo = ViajeRepo(db)
    resultado = repo.insertar_registro(datos)
    if not resultado:
        raise HTTPException(status_code=400, detail="No se pudo registrar el viaje")
    return resultado

@router.put("/api/viajes/{id_viaje}")
def actualizar_viaje(id_viaje: int, datos: dict[str, Any], db: Connection = Depends(db_manager.get_db)):
    repo = ViajeRepo(db)
    resultado = repo.actualizar_registro(datos, id_viaje, "id_viaje")
    if not resultado:
        raise HTTPException(status_code=404, detail="Viaje no encontrado o no actualizado")
    return resultado

@router.delete("/api/viajes/{id_viaje}")
def eliminar_viaje(id_viaje: int, db: Connection = Depends(db_manager.get_db)):
    repo = ViajeRepo(db)
    exito = repo.eliminar_registro(id_viaje, "id_viaje")
    if not exito:
        raise HTTPException(status_code=404, detail="Viaje no encontrado")
    return {"mensaje": "Viaje eliminado correctamente"}