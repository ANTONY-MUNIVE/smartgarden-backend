from src.domain.entities.recomendacion import Recomendacion
from src.domain.ports.recomendacion_port import RecomendacionRepositoryPort
from src.infrastructure.database import SessionLocal, RecomendacionDB
from typing import List, Optional

class PostgresRecomendacionRepository(RecomendacionRepositoryPort):
    def _to_entity(self, r: RecomendacionDB) -> Recomendacion:
        return Recomendacion(
            id=r.id, prioridad=r.prioridad, accion=r.accion,
            descripcion=r.descripcion, variable=r.variable,
            icono=r.icono or '💡', confianza=r.confianza,
            aplicada=r.aplicada, fecha=r.created_at,
        )

    def get_all(self) -> List[Recomendacion]:
        db = SessionLocal()
        try:
            return [self._to_entity(r) for r in db.query(RecomendacionDB).order_by(RecomendacionDB.id).all()]
        finally:
            db.close()

    def save(self, rec: Recomendacion) -> Recomendacion:
        db = SessionLocal()
        try:
            row = RecomendacionDB(
                prioridad=rec.prioridad, accion=rec.accion, descripcion=rec.descripcion,
                variable=rec.variable, icono=rec.icono, confianza=rec.confianza,
            )
            db.add(row)
            db.commit()
            db.refresh(row)
            return self._to_entity(row)
        finally:
            db.close()

    def aplicar(self, rec_id: int) -> Optional[Recomendacion]:
        db = SessionLocal()
        try:
            row = db.query(RecomendacionDB).filter(RecomendacionDB.id == rec_id).first()
            if not row:
                return None
            row.aplicada = True
            db.commit()
            db.refresh(row)
            return self._to_entity(row)
        finally:
            db.close()
