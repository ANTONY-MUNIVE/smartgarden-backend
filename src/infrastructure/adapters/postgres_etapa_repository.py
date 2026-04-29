from src.domain.entities.etapa import EtapaCultivo
from src.domain.ports.etapa_port import EtapaRepositoryPort
from src.infrastructure.database import SessionLocal, EtapaCultivoDB
from typing import List, Optional

class PostgresEtapaRepository(EtapaRepositoryPort):
    def _to_entity(self, r: EtapaCultivoDB) -> EtapaCultivo:
        return EtapaCultivo(
            id=r.id, nombre=r.nombre, estado=r.estado,
            fecha=r.fecha, icono=r.icono or '🌱',
            descripcion=r.descripcion, datos=r.datos or {},
        )

    def get_all(self) -> List[EtapaCultivo]:
        db = SessionLocal()
        try:
            return [self._to_entity(r) for r in db.query(EtapaCultivoDB).order_by(EtapaCultivoDB.id).all()]
        finally:
            db.close()

    def update(self, etapa_id: int, data: dict) -> Optional[EtapaCultivo]:
        db = SessionLocal()
        try:
            row = db.query(EtapaCultivoDB).filter(EtapaCultivoDB.id == etapa_id).first()
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
