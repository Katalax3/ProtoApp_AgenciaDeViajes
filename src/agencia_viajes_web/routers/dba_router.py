from fastapi.responses import HTMLResponse
from agencia_viajes_web.core.dependencies import require_role
from fastapi import APIRouter, Depends, HTTPException, Request
from agencia_viajes_web.core.templates import templates
from agencia_viajes_web import Conexion
from agencia_viajes_web.repositories.base_repo import BaseRepo
from psycopg import Connection
from typing import Any

router = APIRouter(
    prefix="/dba", dependencies=[Depends(require_role("DBA"))], tags=["DBA"]
)

db_manager = Conexion()

# Mapeo de tablas permitidas y el nombre de su llave primaria en la BD
TABLAS_CONFIG = {
    "pais": {
        "id_tabla": "id_pais",
        "hijos": [{"tabla": "estado", "fk": "id_pais"}]
    },
    "parcialidad": {
        "id_tabla": "id_parcialidad",
        "hijos": [{"tabla": "pago", "fk": "id_parcialidad"}]
    },
    "banco": {
        "id_tabla": "id_banco",
        "hijos": [{"tabla": "cuenta", "fk": "id_banco"}]
    }
}

@router.get("/dashboard", response_class=HTMLResponse)
def dba_dashboard(request: Request):
    usuario_sesion = request.session.get("usuario", {})
    nombre_completo = f"{usuario_sesion.get('nombre', '')} {usuario_sesion.get('paterno', '')}".strip()
    if not nombre_completo:
        nombre_completo = "Administrador"
        
    return templates.TemplateResponse(
        request, 
        "dba_dashboard.html", 
        {"usuario_nombre": nombre_completo}
    )

@router.get("/api/{tabla}")
def obtener_registros(tabla: str, db: Connection = Depends(db_manager.get_db)):
    if tabla not in TABLAS_CONFIG:
        raise HTTPException(status_code=400, detail="Tabla no permitida")
    repo = BaseRepo(db, tabla)
    return repo.obtener_todos()

@router.post("/api/{tabla}")
def crear_registro(tabla: str, datos: dict[str, Any], db: Connection = Depends(db_manager.get_db)):
    if tabla not in TABLAS_CONFIG:
        raise HTTPException(status_code=400, detail="Tabla no permitida")
    repo = BaseRepo(db, tabla)
    resultado = repo.insertar_registro(datos)
    if not resultado:
        raise HTTPException(status_code=400, detail="No se pudo registrar el elemento")
    return resultado

@router.put("/api/{tabla}/{id_val}")
def actualizar_registro(tabla: str, id_val: int, datos: dict[str, Any], db: Connection = Depends(db_manager.get_db)):
    if tabla not in TABLAS_CONFIG:
        raise HTTPException(status_code=400, detail="Tabla no permitida")
    config = TABLAS_CONFIG[tabla]
    repo = BaseRepo(db, tabla)
    resultado = repo.actualizar_registro(datos, id_val, config["id_tabla"])
    if not resultado:
        raise HTTPException(status_code=404, detail="Registro no encontrado o no actualizado")
    return resultado

@router.delete("/api/{tabla}/{id_val}")
def eliminar_registro(tabla: str, id_val: int, db: Connection = Depends(db_manager.get_db)):
    if tabla not in TABLAS_CONFIG:
        raise HTTPException(status_code=400, detail="Tabla no permitida")
    
    config = TABLAS_CONFIG[tabla]
    repo = BaseRepo(db, tabla)
    
    # Verificar si tiene hijos antes de eliminar
    for hijo in config.get("hijos", []):
        if repo.tiene_registros_hijos(id_val, config["id_tabla"], hijo["tabla"], hijo["fk"]):
            raise HTTPException(
                status_code=400, 
                detail=f"No se puede eliminar el registro porque tiene dependencias en la tabla '{hijo['tabla']}'."
            )
            
    exito = repo.eliminar_registro(id_val, config["id_tabla"])
    if not exito:
        raise HTTPException(status_code=404, detail="Registro no encontrado")
    return {"mensaje": "Eliminado correctamente"}