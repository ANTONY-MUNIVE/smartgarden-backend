from sqlalchemy import create_engine, Column, Integer, String, Float, Text, Boolean, DateTime
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import uuid
from sqlalchemy.dialects.postgresql import UUID, JSONB
from datetime import datetime
import os
import socket

from sqlalchemy.engine import make_url

from dotenv import load_dotenv

try:
    import dns.resolver
except ImportError:
    dns = None

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:12345@localhost:5432/hadepeja")
DATABASE_URL_POOLER = os.getenv("DATABASE_URL_POOLER", "").strip()
ACTIVE_DATABASE_URL = DATABASE_URL_POOLER or DATABASE_URL

# Support for SSL connections (required by Supabase). You can force SSL by
# setting DB_SSL=true in the environment, or it will auto-enable when the
# URL contains 'supabase.co'.
DB_SSL = os.getenv("DB_SSL", "").lower() in ("1", "true", "yes")
USE_SSL = DB_SSL or ("supabase.co" in ACTIVE_DATABASE_URL)
AUTO_CREATE_TABLES = os.getenv("AUTO_CREATE_TABLES", "").lower() in ("1", "true", "yes")


def resolve_host_ip(host: str) -> str | None:
    if dns is not None:
        for record_type in ("AAAA", "A"):
            try:
                answers = dns.resolver.resolve(host, record_type)
                if answers:
                    return answers[0].to_text()
            except Exception:
                continue

    try:
        resolved = socket.getaddrinfo(host, 5432, type=socket.SOCK_STREAM)
        if resolved:
            return resolved[0][4][0]
    except OSError:
        return None

    return None

if USE_SSL:
    connect_args = {"sslmode": "require"}

    url = make_url(ACTIVE_DATABASE_URL)
    resolved_host = resolve_host_ip(url.host) if url.host else None
    if resolved_host:
        url = url.set(host=resolved_host)

    engine = create_engine(url.render_as_string(hide_password=False), connect_args=connect_args)
else:
    engine = create_engine(ACTIVE_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class UserDB(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False)
    nombre = Column(String(100), nullable=False)
    email = Column(String(100), unique=True)
    password_hash = Column(Text, nullable=False)
    rol = Column(String(20), default='estudiante')
    avatar = Column(Text)
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class SensorReadingDB(Base):
    __tablename__ = "sensor_readings"
    id = Column(Integer, primary_key=True, index=True)
    humedad_suelo = Column(Float, nullable=False)
    temperatura = Column(Float, nullable=False)
    luminosidad = Column(Float, nullable=False)
    humedad_ambiental = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class AlertaDB(Base):
    __tablename__ = "alertas"
    id = Column(Integer, primary_key=True, index=True)
    tipo = Column(String(20), nullable=False)
    variable = Column(String(100), nullable=False)
    mensaje = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class RecomendacionDB(Base):
    __tablename__ = "recomendaciones"
    id = Column(Integer, primary_key=True, index=True)
    prioridad = Column(String(20), nullable=False)
    accion = Column(String(255), nullable=False)
    descripcion = Column(Text)
    variable = Column(String(100))
    icono = Column(String(10), default='💡')
    confianza = Column(Float)
    aplicada = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class ExperimentoDB(Base):
    __tablename__ = "experimentos"
    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(255), nullable=False)
    hipotesis = Column(Text, nullable=False)
    cultivo = Column(String(100))
    duracion = Column(Integer)
    progreso = Column(Integer, default=0)
    estado = Column(String(20), default='pendiente')
    observaciones = Column(Integer, default=0)
    variables = Column(JSONB, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)

class EtapaCultivoDB(Base):
    __tablename__ = "etapas_cultivo"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(150), nullable=False)
    estado = Column(String(20), default='pendiente')
    fecha = Column(String(50))
    icono = Column(String(10), default='🌱')
    descripcion = Column(Text)
    datos = Column(JSONB)
    created_at = Column(DateTime, default=datetime.utcnow)

class SystemConfigDB(Base):
    __tablename__ = "system_config"
    id = Column(Integer, primary_key=True, index=True)
    humedad_min = Column(Float, default=25)
    humedad_max = Column(Float, default=80)
    temp_min = Column(Float, default=15)
    temp_max = Column(Float, default=35)
    luz_min = Column(Float, default=200)
    luz_max = Column(Float, default=1000)
    intervalo_sensor = Column(Integer, default=10)
    alertas_email = Column(Boolean, default=True)
    alertas_dashboard = Column(Boolean, default=True)
    cultivo_actual = Column(String(100), default='Tomate Cherry')
    etapa_actual = Column(String(100), default='Crecimiento Vegetativo')
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

if AUTO_CREATE_TABLES:
    try:
        Base.metadata.create_all(bind=engine)
    except SQLAlchemyError as exc:
        print(f"Warning: could not create database tables automatically: {exc}")
