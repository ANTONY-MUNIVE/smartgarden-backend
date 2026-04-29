from src.domain.entities.alerta import Alerta
from src.domain.ports.alerta_port import AlertaRepositoryPort
from src.infrastructure.database import SessionLocal, AlertaDB
from typing import List

class PostgresAlertaRepository(AlertaRepositoryPort):
    def get_all(self) -> List[Alerta]:
        db = SessionLocal()
        try:
            rows = db.query(AlertaDB).order_by(AlertaDB.created_at.desc()).all()
            return [Alerta(id=r.id, tipo=r.tipo, variable=r.variable, mensaje=r.mensaje, fecha=r.created_at) for r in rows]
        finally:
            db.close()

    def save(self, alerta: Alerta) -> Alerta:
        db = SessionLocal()
        try:
            row = AlertaDB(tipo=alerta.tipo, variable=alerta.variable, mensaje=alerta.mensaje)
            db.add(row)
            db.commit()
            db.refresh(row)
            alerta.id = row.id
            alerta.fecha = row.created_at
            return alerta
        finally:
            db.close()
