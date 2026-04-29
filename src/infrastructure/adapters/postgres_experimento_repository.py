from src.domain.entities.experimento import Experimento
from src.domain.ports.experimento_port import ExperimentoRepositoryPort
from src.infrastructure.database import SessionLocal, ExperimentoDB
from typing import List, Optional

class PostgresExperimentoRepository(ExperimentoRepositoryPort):
    def _to_entity(self, r: ExperimentoDB) -> Experimento:
        return Experimento(
            id=r.id, titulo=r.titulo, hipotesis=r.hipotesis,
            cultivo=r.cultivo, duracion=r.duracion, progreso=r.progreso,
            estado=r.estado, observaciones=r.observaciones,
            variables=r.variables or [], fecha=r.created_at,
        )

    def get_all(self) -> List[Experimento]:
        db = SessionLocal()
        try:
            return [self._to_entity(r) for r in db.query(ExperimentoDB).order_by(ExperimentoDB.id).all()]
        finally:
            db.close()

    def save(self, exp: Experimento) -> Experimento:
        db = SessionLocal()
        try:
            row = ExperimentoDB(
                titulo=exp.titulo, hipotesis=exp.hipotesis, cultivo=exp.cultivo,
                duracion=exp.duracion, progreso=exp.progreso or 0,
                estado=exp.estado or 'pendiente', observaciones=exp.observaciones or 0,
                variables=exp.variables or [],
            )
            db.add(row)
            db.commit()
            db.refresh(row)
            return self._to_entity(row)
        finally:
            db.close()

    def update(self, exp_id: int, data: dict) -> Optional[Experimento]:
        db = SessionLocal()
        try:
            row = db.query(ExperimentoDB).filter(ExperimentoDB.id == exp_id).first()
            if not row:
                return None
            for key, value in data.items():
                if hasattr(row, key):
                    setattr(row, key, value)
            db.commit()
            db.refresh(row)
            return self._to_entity(row)
        finally:
            db.close()

    def delete(self, exp_id: int) -> bool:
        db = SessionLocal()
        try:
            row = db.query(ExperimentoDB).filter(ExperimentoDB.id == exp_id).first()
            if not row:
                return False
            db.delete(row)
            db.commit()
            return True
        finally:
            db.close()
