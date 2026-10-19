from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, model_validator


def validar_rango_fechas(
    fecha_salida: Optional[datetime],
    fecha_llegada_est: Optional[datetime],
) -> None:
    if fecha_salida is None or fecha_llegada_est is None:
        return

    salida_aware = fecha_salida.utcoffset() is not None
    llegada_aware = fecha_llegada_est.utcoffset() is not None
    if salida_aware != llegada_aware:
        raise ValueError(
            "Las fechas de salida y llegada deben usar la misma zona horaria"
        )
    if fecha_llegada_est <= fecha_salida:
        raise ValueError("La fecha de llegada debe ser posterior a la fecha de salida")


class ViajeCreate(BaseModel):
    tipo_mercancia: str
    peso_total_kg: float = Field(gt=0, allow_inf_nan=False)
    dimensiones: Optional[str] = None
    numero_contenedor: Optional[str] = None
    peso_contenedor_kg: Optional[float] = Field(
        default=None, gt=0, allow_inf_nan=False
    )
    origen: str
    destino: str
    # ⭐ COORDENADAS GPS (Patrón Adapter - convierte direcciones en coordenadas)
    latitud_origen: Optional[float] = None
    longitud_origen: Optional[float] = None
    latitud_destino: Optional[float] = None
    longitud_destino: Optional[float] = None
    punto_recepcion: Optional[str] = None
    destinatario_nombre: Optional[str] = None
    destinatario_tel: Optional[str] = None
    destinatario_correo: Optional[str] = None
    fecha_salida: Optional[datetime] = None
    fecha_llegada_est: Optional[datetime] = None
    observaciones: Optional[str] = None

    @model_validator(mode="after")
    def validar_fechas(self):
        validar_rango_fechas(self.fecha_salida, self.fecha_llegada_est)
        return self


class ViajeUpdate(BaseModel):
    ruta_json: Optional[str] = None
    fecha_salida: Optional[datetime] = None
    fecha_llegada_est: Optional[datetime] = None
    observaciones: Optional[str] = None


class ReprogramarViajeRequest(BaseModel):
    causa: str
    horas_retraso: float
    observaciones: Optional[str] = None


class CancelarViajeRequest(BaseModel):
    causa_cancelacion: str
    evidencia_url: Optional[str] = None


class PlanificarRutaRequest(BaseModel):
    origen: str
    destino: str
    tramos_intermedios: Optional[List[str]] = []
    ruta_json: Optional[str] = None


# ⚠️ NUEVO SCHEMA (FALTABA)
class AsignarTransportistaRequest(BaseModel):
    transportista_id: int


class ViajeOut(BaseModel):
    id: int
    codigo: str
    estado: str
    tipo_mercancia: str
    peso_total_kg: float
    dimensiones: Optional[str]
    numero_contenedor: Optional[str]
    origen: str
    destino: str
    # ⭐ COORDENADAS GPS para mapas (Patrón Adapter)
    latitud_origen: Optional[float]
    longitud_origen: Optional[float]
    latitud_destino: Optional[float]
    longitud_destino: Optional[float]
    latitud_actual: Optional[float]
    longitud_actual: Optional[float]
    punto_recepcion: Optional[str]
    destinatario_nombre: Optional[str]
    destinatario_tel: Optional[str]
    destinatario_correo: Optional[str]
    fecha_salida: Optional[datetime]
    fecha_llegada_est: Optional[datetime]
    fecha_llegada_real: Optional[datetime]
    horas_retraso: Optional[float]
    causa_retraso: Optional[str]
    causa_cancelacion: Optional[str]
    observaciones: Optional[str]
    transportista_id: Optional[int]
    transportista_nombres: Optional[str]
    ruta_json: Optional[str]
    creado_en: datetime

    class Config:
        from_attributes = True


class ModificarRutaRequest(BaseModel):
    nueva_ruta_json: str
    motivo: str