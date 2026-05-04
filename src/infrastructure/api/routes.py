from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List

from src.application.use_cases.sensor_use_case import SensorUseCase
from src.infrastructure.adapters.postgres_repository import PostgresSensorRepository
from src.application.use_cases.user_use_case import UserUseCase
from src.infrastructure.adapters.postgres_user_repository import PostgresUserRepository
from src.application.use_cases.alerta_use_case import AlertaUseCase
from src.infrastructure.adapters.postgres_alerta_repository import PostgresAlertaRepository
from src.application.use_cases.recomendacion_use_case import RecomendacionUseCase
from src.infrastructure.adapters.postgres_recomendacion_repository import PostgresRecomendacionRepository
from src.application.use_cases.experimento_use_case import ExperimentoUseCase
from src.infrastructure.adapters.postgres_experimento_repository import PostgresExperimentoRepository
from src.application.use_cases.etapa_use_case import EtapaUseCase
from src.infrastructure.adapters.postgres_etapa_repository import PostgresEtapaRepository
from src.infrastructure.database import SessionLocal, SystemConfigDB
from sqlalchemy.exc import OperationalError

router = APIRouter()

# ─── Pydantic models ──────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    username: str
    password: str

class CreateUserRequest(BaseModel):
    nombre: str
    username: str
    email: Optional[str] = None
    password: str
    rol: str = 'estudiante'

class UpdateUserRequest(BaseModel):
    nombre: Optional[str] = None
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    rol: Optional[str] = None

class ExperimentoRequest(BaseModel):
    titulo: str
    hipotesis: str
    cultivo: Optional[str] = None
    duracion: Optional[int] = None
    progreso: int = 0
    estado: str = 'pendiente'
    observaciones: int = 0
    variables: List[str] = []

class ExperimentoUpdateRequest(BaseModel):
    titulo: Optional[str] = None
    hipotesis: Optional[str] = None
    cultivo: Optional[str] = None
    duracion: Optional[int] = None
    progreso: Optional[int] = None
    estado: Optional[str] = None
    observaciones: Optional[int] = None
    variables: Optional[List[str]] = None

class EtapaUpdateRequest(BaseModel):
    estado: Optional[str] = None
    fecha: Optional[str] = None
    descripcion: Optional[str] = None

class ConfigRequest(BaseModel):
    humedad_min: Optional[float] = None
    humedad_max: Optional[float] = None
    temp_min: Optional[float] = None
    temp_max: Optional[float] = None
    luz_min: Optional[float] = None
    luz_max: Optional[float] = None
    intervalo_sensor: Optional[int] = None
    alertas_email: Optional[bool] = None
    alertas_dashboard: Optional[bool] = None
    cultivo_actual: Optional[str] = None
    etapa_actual: Optional[str] = None


class RecomendacionCreateRequest(BaseModel):
    prioridad: str = 'media'
    accion: str
    descripcion: Optional[str] = None
    variable: Optional[str] = None
    icono: Optional[str] = '💡'
    confianza: Optional[float] = None

# ─── Dependency injection ─────────────────────────────────────────────────────

def get_user_uc():
    return UserUseCase(PostgresUserRepository())

def get_sensor_uc():
    return SensorUseCase(PostgresSensorRepository())

def get_alerta_uc():
    return AlertaUseCase(PostgresAlertaRepository())

def get_recomendacion_uc():
    return RecomendacionUseCase(PostgresRecomendacionRepository())

def get_experimento_uc():
    return ExperimentoUseCase(PostgresExperimentoRepository())

def get_etapa_uc():
    return EtapaUseCase(PostgresEtapaRepository())

# ─── Auth ─────────────────────────────────────────────────────────────────────

@router.post("/users/login")
async def login(request: LoginRequest, uc: UserUseCase = Depends(get_user_uc)):
    return uc.login(request.username, request.password)

# ─── Users CRUD ───────────────────────────────────────────────────────────────

@router.get("/users")
async def get_users(uc: UserUseCase = Depends(get_user_uc)):
    try:
        return uc.get_all_users()
    except OperationalError:
        return []

@router.post("/users")
async def create_user(req: CreateUserRequest, uc: UserUseCase = Depends(get_user_uc)):
    try:
        result = uc.create_user(req.nombre, req.username, req.email, req.password, req.rol)
    except OperationalError:
        raise HTTPException(status_code=503, detail="Base de datos no disponible. Configura DATABASE_URL_POOLER o inténtalo más tarde.")
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@router.put("/users/{user_id}")
async def update_user(user_id: str, req: UpdateUserRequest, uc: UserUseCase = Depends(get_user_uc)):
    result = uc.update_user(user_id, req.dict())
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result

@router.delete("/users/{user_id}")
async def delete_user(user_id: str, uc: UserUseCase = Depends(get_user_uc)):
    result = uc.delete_user(user_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result

@router.patch("/users/{user_id}/toggle")
async def toggle_user(user_id: str, uc: UserUseCase = Depends(get_user_uc)):
    result = uc.toggle_active(user_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result

# ─── Sensors ──────────────────────────────────────────────────────────────────

@router.post("/sensors/reading")
async def create_reading(data: dict, uc: SensorUseCase = Depends(get_sensor_uc)):
    return uc.registrar_lectura(data).to_dict()

@router.get("/sensors/current")
async def get_current(uc: SensorUseCase = Depends(get_sensor_uc)):
    reading = uc.obtener_estado_actual()
    return reading.to_dict() if reading else {"message": "No data available"}

@router.get("/sensors/history")
async def get_history(limit: int = 24, uc: SensorUseCase = Depends(get_sensor_uc)):
    return [r.to_dict() for r in uc.obtener_historial(limit)]

# ─── Alertas ──────────────────────────────────────────────────────────────────

@router.get("/alertas")
async def get_alertas(uc: AlertaUseCase = Depends(get_alerta_uc)):
    return [a.to_dict() for a in uc.obtener_alertas()]

@router.post("/alertas")
async def create_alerta(data: dict, uc: AlertaUseCase = Depends(get_alerta_uc)):
    return uc.crear_alerta(data).to_dict()

# ─── Recomendaciones ──────────────────────────────────────────────────────────

@router.get("/recomendaciones")
async def get_recomendaciones(uc: RecomendacionUseCase = Depends(get_recomendacion_uc)):
    return [r.to_dict() for r in uc.obtener_recomendaciones()]


@router.post("/recomendaciones")
async def create_recomendacion(req: RecomendacionCreateRequest, uc: RecomendacionUseCase = Depends(get_recomendacion_uc)):
    result = uc.crear_recomendacion(req.dict())
    if not result:
        raise HTTPException(status_code=503, detail="No se pudo crear la recomendación (BD no disponible)")
    return result.to_dict()

@router.patch("/recomendaciones/{rec_id}/aplicar")
async def aplicar_recomendacion(rec_id: int, uc: RecomendacionUseCase = Depends(get_recomendacion_uc)):
    result = uc.aplicar_recomendacion(rec_id)
    if not result:
        raise HTTPException(status_code=404, detail="Recomendación no encontrada")
    return result.to_dict()

# ─── Experimentos ─────────────────────────────────────────────────────────────

@router.get("/experimentos")
async def get_experimentos(uc: ExperimentoUseCase = Depends(get_experimento_uc)):
    return [e.to_dict() for e in uc.obtener_experimentos()]

@router.post("/experimentos")
async def create_experimento(req: ExperimentoRequest, uc: ExperimentoUseCase = Depends(get_experimento_uc)):
    return uc.crear_experimento(req.dict()).to_dict()

@router.put("/experimentos/{exp_id}")
async def update_experimento(exp_id: int, req: ExperimentoUpdateRequest, uc: ExperimentoUseCase = Depends(get_experimento_uc)):
    data = {k: v for k, v in req.dict().items() if v is not None}
    result = uc.actualizar_experimento(exp_id, data)
    if not result:
        raise HTTPException(status_code=404, detail="Experimento no encontrado")
    return result.to_dict()

@router.delete("/experimentos/{exp_id}")
async def delete_experimento(exp_id: int, uc: ExperimentoUseCase = Depends(get_experimento_uc)):
    if not uc.eliminar_experimento(exp_id):
        raise HTTPException(status_code=404, detail="Experimento no encontrado")
    return {"ok": True}

# ─── Etapas de cultivo ────────────────────────────────────────────────────────

@router.get("/etapas")
async def get_etapas(uc: EtapaUseCase = Depends(get_etapa_uc)):
    return [e.to_dict() for e in uc.obtener_etapas()]

@router.put("/etapas/{etapa_id}")
async def update_etapa(etapa_id: int, req: EtapaUpdateRequest, uc: EtapaUseCase = Depends(get_etapa_uc)):
    data = {k: v for k, v in req.dict().items() if v is not None}
    result = uc.actualizar_etapa(etapa_id, data)
    if not result:
        raise HTTPException(status_code=404, detail="Etapa no encontrada")
    return result.to_dict()

# ─── System Config ────────────────────────────────────────────────────────────

@router.get("/config")
async def get_config():
    db = SessionLocal()
    try:
        cfg = db.query(SystemConfigDB).first()
        if not cfg:
            return {}
        return {
            "humedad_min": cfg.humedad_min, "humedad_max": cfg.humedad_max,
            "temp_min": cfg.temp_min,       "temp_max": cfg.temp_max,
            "luz_min": cfg.luz_min,         "luz_max": cfg.luz_max,
            "intervalo_sensor": cfg.intervalo_sensor,
            "alertas_email": cfg.alertas_email,
            "alertas_dashboard": cfg.alertas_dashboard,
            "cultivo_actual": cfg.cultivo_actual,
            "etapa_actual": cfg.etapa_actual,
        }
    except OperationalError:
        return {}
    finally:
        db.close()

@router.put("/config")
async def save_config(req: ConfigRequest):
    db = SessionLocal()
    try:
        cfg = db.query(SystemConfigDB).first()
        if not cfg:
            cfg = SystemConfigDB()
            db.add(cfg)
        for key, value in req.dict().items():
            if value is not None and hasattr(cfg, key):
                setattr(cfg, key, value)
        db.commit()
        return {"ok": True}
    except OperationalError:
        return {"ok": False, "warning": "Base de datos no disponible"}
    finally:
        db.close()

# ─── Indicadores STEAM ────────────────────────────────────────────────────────

@router.get("/indicadores")
async def get_indicadores(uc: ExperimentoUseCase = Depends(get_experimento_uc)):
    experimentos = uc.obtener_experimentos()
    activos    = sum(1 for e in experimentos if e.estado == 'activo')
    obs_total  = sum(e.observaciones for e in experimentos)
    return {
        "experimentos_activos": activos,
        "observaciones_totales": obs_total,
        "variables_monitoreadas": 4,
        "sesiones_semana": max(len(experimentos), 1),
        "areas": [
            {"area": "Ciencia",     "descripcion": "Método científico y experimentación", "actividades": 29, "progreso": 85},
            {"area": "Tecnología",  "descripcion": "Sensores IoT y monitoreo digital",    "actividades": 22, "progreso": 70},
            {"area": "Ingeniería",  "descripcion": "Sistemas de riego y estructuras",      "actividades": 18, "progreso": 60},
            {"area": "Arte",        "descripcion": "Documentación visual y diseño",        "actividades": 15, "progreso": 50},
            {"area": "Matemáticas", "descripcion": "Análisis de datos y estadísticas",     "actividades": 25, "progreso": 75},
        ],
    }
