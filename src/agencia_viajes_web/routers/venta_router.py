from datetime import date, datetime

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from fpdf import FPDF
from pydantic import BaseModel, Field
from psycopg import Connection

from agencia_viajes_web.core.conexion import Conexion
from agencia_viajes_web.core.dependencies import require_role
from agencia_viajes_web.repositories.venta_repo import VentaRepo

db_manager = Conexion()
rol_empleado = require_role("Empleado")

router = APIRouter(
    prefix="/empleado/venta",
    tags=["Venta de boletos"],
    dependencies=[Depends(rol_empleado)],
)


class ContextoOut(BaseModel):
    atiende: str


class ClienteOut(BaseModel):
    id_usuario: int
    nombre_completo: str


class PaisOut(BaseModel):
    id_pais: int
    nombre: str


class ViajeVentaOut(BaseModel):
    id_viaje: int
    nombre: str
    fecha_salida: datetime
    fecha_llegada: datetime
    costo: float
    transporte: str
    asientos_libres: int


class AsientoOut(BaseModel):
    id_asiento: int
    num_asiento: str
    ocupado: bool


class VentaCreate(BaseModel):
    id_viaje: int = Field(..., gt=0)
    id_cliente: int = Field(..., gt=0)
    id_pais_emision: int = Field(..., gt=0)
    tipo_documento: str = Field(..., min_length=1, max_length=30)
    numero_documento: str = Field(..., min_length=1, max_length=18)
    num_asiento: str = Field(..., min_length=1, max_length=3)


class VentaOut(BaseModel):
    id_boleto: int
    num_boleto: str


@router.get("/api/contexto", response_model=ContextoOut)
def contexto(usuario: dict = Depends(rol_empleado)):
    return {"atiende": f"{usuario['nombre']} {usuario['paterno']}"}


@router.get("/api/clientes", response_model=list[ClienteOut])
def buscar_clientes(q: str = Query("", max_length=60), db: Connection = Depends(db_manager.get_db)):
    return VentaRepo(db).buscar_clientes(q)


@router.get("/api/paises", response_model=list[PaisOut])
def listar_paises(db: Connection = Depends(db_manager.get_db)):
    return VentaRepo(db).obtener_paises()


@router.get("/api/viajes", response_model=list[ViajeVentaOut])
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


@router.get("/api/viajes/{id_viaje}/asientos", response_model=list[AsientoOut])
def listar_asientos(id_viaje: int, db: Connection = Depends(db_manager.get_db)):
    return VentaRepo(db).obtener_asientos(id_viaje)


@router.post("/api/boletos", response_model=VentaOut, status_code=201)
def vender_boleto(
    payload: VentaCreate,
    usuario: dict = Depends(rol_empleado),
    db: Connection = Depends(db_manager.get_db),
):
    repo = VentaRepo(db)
    try:
        id_agencia = repo.obtener_agencia_empleado(usuario["nombre"], usuario["paterno"])
        id_boleto = repo.vender_boleto(payload.model_dump(), id_agencia)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    boleto = repo.obtener_boleto(id_boleto)
    if not boleto:
        raise HTTPException(status_code=500, detail="La venta se registró pero no se pudo leer el boleto.")
    return {"id_boleto": id_boleto, "num_boleto": boleto["num_boleto"]}


MESES = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]


def _pdf_boleto(b: dict) -> Response:
    """Arma el PDF 'Boleto de Autobús'. b trae: cliente, fecha_salida, origen, destino, num_asiento, transporte."""

    # Las fuentes base de fpdf2 solo soportan latin-1
    def t(valor) -> str:
        return str(valor).encode("latin-1", "replace").decode("latin-1")

    f = b["fecha_salida"]
    fecha_salida = f"{f.day:02d}/{MESES[f.month - 1]}/{f.year}"
    hora_salida = f.strftime("%H:%M")

    pdf = FPDF()
    pdf.add_page()
    pdf.set_margins(20, 20, 20)
    pdf.set_y(25)
    pdf.set_font("Helvetica", style="B", size=20)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 12, "BOLETO DE AUTOBÚS", new_x="LMARGIN", new_y="NEXT")
    pdf.set_draw_color(0, 0, 0)
    pdf.line(20, pdf.get_y() + 1, 190, pdf.get_y() + 1)
    pdf.ln(10)

    def fila(etiqueta: str, valor: str, espacio: float = 0):
        pdf.set_font("Helvetica", style="B", size=13)
        ancho = pdf.get_string_width(etiqueta + " ") + 1
        pdf.cell(ancho, 9, etiqueta, new_x="RIGHT", new_y="TOP")
        pdf.set_font("Helvetica", size=13)
        pdf.cell(0, 9, t(valor), new_x="LMARGIN", new_y="NEXT")
        if espacio:
            pdf.ln(espacio)

    fila("Cliente:", b["cliente"], espacio=4)
    fila("Fecha de salida:", fecha_salida)
    fila("Hora de salida:", hora_salida, espacio=4)
    fila("Origen:", b["origen"])
    fila("Destino:", b["destino"], espacio=4)
    fila("Asiento:", b["num_asiento"])
    fila("Autobús:", b["transporte"])

    return Response(
        content=bytes(pdf.output()),
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=boleto_de_autobus.pdf"},
    )


# Boleto con lo elegido en pantalla (todavía no se registra la venta)
@router.get("/api/boleto-pdf")
def pdf_boleto_en_pantalla(
    id_viaje: int = Query(..., gt=0),
    id_cliente: int = Query(..., gt=0),
    num_asiento: str = Query(..., min_length=1, max_length=3),
    db: Connection = Depends(db_manager.get_db),
):
    try:
        datos = VentaRepo(db).preparar_boleto(id_viaje, id_cliente, num_asiento)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return _pdf_boleto(datos)


# Boleto ya registrado en la BD (se usará cuando exista el paso de pago)
@router.get("/api/boletos/{id_boleto}/pdf")
def descargar_pdf_boleto(id_boleto: int, db: Connection = Depends(db_manager.get_db)):
    b = VentaRepo(db).obtener_boleto(id_boleto)
    if not b:
        raise HTTPException(status_code=404, detail="Boleto no encontrado")
    return _pdf_boleto(b)
