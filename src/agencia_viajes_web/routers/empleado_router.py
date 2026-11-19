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

# --- NUEVO ENDPOINT PARA EL PDF ---
@router.get("/api/viajes/{id_viaje}/pdf")
def descargar_pdf_viaje(id_viaje: int, db: Connection = Depends(db_manager.get_db)):
    repo = ViajeRepo(db)
    viaje = repo.obtener_viaje_por_id(id_viaje)
    
    if not viaje:
        raise HTTPException(status_code=404, detail="Viaje no encontrado")

    # --- CREACIÓN DEL PDF CON FPDF2 ---
    pdf = FPDF()
    pdf.add_page()
    
    # Título
    pdf.set_font("Helvetica", style="B", size=20)
    pdf.set_text_color(40, 40, 40)
    pdf.cell(0, 15, "Comprobante de Viaje", new_x="LMARGIN", new_y="NEXT", align="C")
    
    # Línea decorativa
    pdf.set_draw_color(100, 100, 100)
    pdf.line(10, 30, 200, 30)
    pdf.ln(10)

    # Función auxiliar para dibujar filas de datos
    def fila_pdf(etiqueta: str, valor: str):
        pdf.set_font("Helvetica", style="B", size=12)
        pdf.set_text_color(80, 80, 80)
        pdf.cell(50, 10, f"{etiqueta}:", new_x="RIGHT", new_y="TOP")
        
        pdf.set_font("Helvetica", size=12)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 10, valor, new_x="LMARGIN", new_y="NEXT")

    # Formatear fechas
    f_salida = viaje["fecha_salida"].strftime("%d/%m/%Y a las %H:%M") if viaje["fecha_salida"] else "No definida"
    f_llegada = viaje["fecha_llegada"].strftime("%d/%m/%Y a las %H:%M") if viaje["fecha_llegada"] else "No definida"

    # Datos del viaje
    fila_pdf("Nombre del Viaje", viaje["nombre_viaje"])
    fila_pdf("ID de Viaje", str(viaje["id_viaje"]))
    pdf.ln(5) # Espacio
    
    fila_pdf("Ciudad Origen", viaje["nombre_ciudad_origen"])
    fila_pdf("Ciudad Destino", viaje["nombre_ciudad_destino"])
    pdf.ln(5)
    
    fila_pdf("Transporte", viaje["nombre_transporte"])
    fila_pdf("Fecha de Salida", f_salida)
    fila_pdf("Fecha de Llegada", f_llegada)
    pdf.ln(5)

    # Costo destacado
    pdf.set_font("Helvetica", style="B", size=16)
    pdf.set_text_color(0, 100, 0) # Verde oscuro
    pdf.cell(0, 15, f"Costo Total: ${viaje['costo']:.2f}", new_x="LMARGIN", new_y="NEXT", align="R")

    # Generar los bytes del PDF
    pdf_bytes = bytes(pdf.output())
    
    headers = {
        "Content-Disposition": f"attachment; filename=viaje_{id_viaje}.pdf"
    }
    return Response(content=pdf_bytes, media_type="application/pdf", headers=headers)

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