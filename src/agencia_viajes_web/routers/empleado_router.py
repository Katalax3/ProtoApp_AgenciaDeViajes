from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from psycopg import Connection
from fpdf import FPDF

from agencia_viajes_web.core.templates import templates
from agencia_viajes_web.core.conexion import Conexion
from agencia_viajes_web.repositories.viaje_repo import ViajeRepo
from agencia_viajes_web.core.dependencies import require_role

db_manager = Conexion()

router = APIRouter(
    prefix="/empleado", 
    tags=["Empleado"],
    dependencies=[Depends(require_role("Empleado"))]
)

class ViajeDetalleOut(BaseModel):
    id_viaje: int
    id_nombre_viaje: int
    nombre_viaje: str | None = None
    id_transporte: int
    nombre_transporte: str | None = None
    id_ciudad_origen: int
    nombre_ciudad_origen: str | None = None
    id_ciudad_destino: int
    nombre_ciudad_destino: str | None = None
    fecha_salida: datetime | None = None
    fecha_llegada: datetime | None = None
    costo: float | None = 0.0

class ViajeCreateUpdate(BaseModel):
    id_nombre_viaje: int = Field(..., gt=0)
    id_transporte: int = Field(..., gt=0)
    id_ciudad_origen: int = Field(..., gt=0)
    id_ciudad_destino: int = Field(..., gt=0)
    fecha_salida: datetime
    fecha_llegada: datetime
    costo: float = Field(..., ge=0)

class CiudadOut(BaseModel):
    id_ciudad: int
    nombre: str

class TransporteOut(BaseModel):
    id_transporte: int
    nombre: str

class NombreViajeOut(BaseModel):
    id_nombre_viaje: int
    nombre: str

@router.get("/dashboard", response_class=HTMLResponse)
def empleado_dashboard(request: Request):
    usuario_sesion = request.session.get("usuario", {})
    nombre_completo = f"{usuario_sesion.get('nombre', '')} {usuario_sesion.get('paterno', '')}".strip()
    if not nombre_completo:
        nombre_completo = "Empleado"
        
    return templates.TemplateResponse(
        request, 
        "empleado_dashboard.html", 
        {"usuario_nombre": nombre_completo}
    )

@router.get("/api/viajes", response_model=list[ViajeDetalleOut])
def listar_viajes(db: Connection = Depends(db_manager.get_db)):
    return ViajeRepo(db).obtener_viaje()

@router.get("/api/ciudades", response_model=list[CiudadOut])
def listar_ciudades(db: Connection = Depends(db_manager.get_db)):
    return ViajeRepo(db).obtener_ciudades()

@router.get("/api/transportes", response_model=list[TransporteOut])
def listar_transportes(db: Connection = Depends(db_manager.get_db)):
    return ViajeRepo(db).obtener_transportes()

@router.get("/api/nombre_viajes", response_model=list[NombreViajeOut])
def listar_nombre_viajes(db: Connection = Depends(db_manager.get_db)):
    return ViajeRepo(db).obtener_nombre_viaje()

@router.get("/api/viajes/{id_viaje}/pdf")
def descargar_pdf_viaje(id_viaje: int, db: Connection = Depends(db_manager.get_db)):
    repo = ViajeRepo(db)
    viaje = repo.obtener_viaje_por_id(id_viaje)
    
    if not viaje:
        raise HTTPException(status_code=404, detail="Viaje no encontrado")

    pdf = FPDF()
    pdf.add_page()
    
    pdf.set_font("Helvetica", style="B", size=20)
    pdf.set_text_color(40, 40, 40)
    pdf.cell(0, 15, "Comprobante de Viaje", new_x="LMARGIN", new_y="NEXT", align="C")
    
    pdf.set_draw_color(100, 100, 100)
    pdf.line(10, 30, 200, 30)
    pdf.ln(10)

    def fila_pdf(etiqueta: str, valor: str):
        pdf.set_font("Helvetica", style="B", size=12)
        pdf.set_text_color(80, 80, 80)
        pdf.cell(50, 10, f"{etiqueta}:", new_x="RIGHT", new_y="TOP")
        
        pdf.set_font("Helvetica", size=12)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 10, valor, new_x="LMARGIN", new_y="NEXT")

    f_salida = viaje["fecha_salida"].strftime("%d/%m/%Y a las %H:%M") if viaje["fecha_salida"] else "No definida"
    f_llegada = viaje["fecha_llegada"].strftime("%d/%m/%Y a las %H:%M") if viaje["fecha_llegada"] else "No definida"

    fila_pdf("Nombre del Viaje", viaje["nombre_viaje"])
    fila_pdf("ID de Viaje", str(viaje["id_viaje"]))
    pdf.ln(5) 
    
    fila_pdf("Ciudad Origen", viaje["nombre_ciudad_origen"])
    fila_pdf("Ciudad Destino", viaje["nombre_ciudad_destino"])
    pdf.ln(5)
    
    fila_pdf("Transporte", viaje["nombre_transporte"])
    fila_pdf("Fecha de Salida", f_salida)
    fila_pdf("Fecha de Llegada", f_llegada)
    pdf.ln(5)

    pdf.set_font("Helvetica", style="B", size=16)
    pdf.set_text_color(0, 100, 0) 
    pdf.cell(0, 15, f"Costo Total: ${viaje['costo']:.2f}", new_x="LMARGIN", new_y="NEXT", align="R")

    pdf_bytes = bytes(pdf.output())
    
    headers = {
        "Content-Disposition": f"attachment; filename=viaje_{id_viaje}.pdf"
    }
    return Response(content=pdf_bytes, media_type="application/pdf", headers=headers)

@router.post("/api/viajes", status_code=201)
def crear_viaje(payload: ViajeCreateUpdate, db: Connection = Depends(db_manager.get_db)):
    repo = ViajeRepo(db)
    if not repo.insertar_registro(payload.model_dump()):
        raise HTTPException(status_code=400, detail="No se pudo registrar el viaje.")
    return {"mensaje": "Viaje registrado correctamente"}

@router.put("/api/viajes/{id_viaje}")
def actualizar_viaje(id_viaje: int, payload: ViajeCreateUpdate, db: Connection = Depends(db_manager.get_db)):
    repo = ViajeRepo(db)
    if not repo.actualizar_registro(payload.model_dump(), id_viaje, "id_viaje"):
        raise HTTPException(status_code=404, detail="Viaje no encontrado o no actualizado.")
    return {"mensaje": "Viaje actualizado correctamente"}

@router.delete("/api/viajes/{id_viaje}")
def eliminar_viaje(id_viaje: int, db: Connection = Depends(db_manager.get_db)):
    repo = ViajeRepo(db)
    if repo.tiene_registros_hijos(id_viaje, "id_viaje", "boleto", "id_viaje"):
        raise HTTPException(status_code=400, detail="El viaje tiene registros dependientes.")
    if not repo.eliminar_registro(id_viaje, "id_viaje"):
        raise HTTPException(status_code=404, detail="Viaje no encontrado.")
    return {"mensaje": "Viaje eliminado correctamente"}