from decimal import Decimal
from datetime import date
from agencia_viajes_web import Conexion
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from psycopg import Connection
from agencia_viajes_web.repositories.parcia_repo import ParciaRepo

class ParciaCreate(BaseModel):
    id_factura: int
    num_parcia: int = Field(ge=1, le=32767)
    fecha_vencimiento: date
    total_parcia: Decimal

class ParciaRespose(BaseModel):
    id_parcialidad: int
    id_factura: int
    num_parcia: int = Field(ge=1, le=32767)
    fecha_vencimiento: date
    total_parcia: Decimal = Field(max_digits=8, decimal_places=2)

class ParciaDetallesRespose(BaseModel):
    num_parcia: int
    fecha_vencimiento: date
    total_parcia: Decimal = Field(max_digits=8, decimal_places=2)


router = APIRouter(prefix="/parcialidad", tags=["Parcialidad"])

db_manager = Conexion()

@router.post("/", response_model=ParciaRespose)
def registrar_parcialidad(datos_registro: ParciaCreate, db: Connection = Depends(db_manager.get_db)):
    repo=ParciaRepo(conn=db)
    try:
        respuesta = repo.insertar_registro(datos_registro.model_dump())
        return respuesta
    except ValueError as e:
            raise HTTPException(status_code=401, detail=str(e))


@router.get("/{id_parcia}", response_model=ParciaDetallesRespose)
def buscar_parcialidad_por_id(id_parcia: int, db: Connection = Depends(db_manager.get_db)):
     repo=ParciaRepo(conn=db)
     try:
          registro = repo.consultar_por_id(id_parcia, id_tabla="id_parcialidad")
          return registro
     except ValueError as e:
          raise HTTPException(status_code=401, detail=str(e))