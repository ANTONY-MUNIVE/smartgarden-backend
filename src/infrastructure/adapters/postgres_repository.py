from sqlalchemy.orm import Session
from src.domain.entities.sensor import SensorReading
from src.domain.ports.repository_port import SensorRepositoryPort
from src.infrastructure.database import SessionLocal, SensorReadingDB
from typing import List

class PostgresSensorRepository(SensorRepositoryPort):
    def save(self, reading: SensorReading) -> SensorReading:
        db = SessionLocal()
        try:
            db_reading = SensorReadingDB(
                humedad_suelo=reading.humedad_suelo,
                temperatura=reading.temperatura,
                luminosidad=reading.luminosidad,
                humedad_ambiental=reading.humedad_ambiental,
                created_at=reading.fecha
            )
            db.add(db_reading)
            db.commit()
            db.refresh(db_reading)
            reading.id = db_reading.id
            return reading
        finally:
            db.close()

    def get_latest(self) -> SensorReading:
        db = SessionLocal()
        try:
            db_reading = db.query(SensorReadingDB).order_by(SensorReadingDB.created_at.desc()).first()
            if db_reading:
                return SensorReading(
                    id=db_reading.id,
                    humedad_suelo=db_reading.humedad_suelo,
                    temperatura=db_reading.temperatura,
                    luminosidad=db_reading.luminosidad,
                    humedad_ambiental=db_reading.humedad_ambiental,
                    fecha=db_reading.created_at
                )
            return None
        finally:
            db.close()

    def get_history(self, limit: int = 24) -> List[SensorReading]:
        db = SessionLocal()
        try:
            db_readings = db.query(SensorReadingDB).order_by(SensorReadingDB.created_at.desc()).limit(limit).all()
            return [
                SensorReading(
                    id=r.id,
                    humedad_suelo=r.humedad_suelo,
                    temperatura=r.temperatura,
                    luminosidad=r.luminosidad,
                    humedad_ambiental=r.humedad_ambiental,
                    fecha=r.created_at
                ) for r in db_readings
            ]
        finally:
            db.close()
