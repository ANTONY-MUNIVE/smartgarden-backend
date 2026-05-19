from typing import List, Optional

from sqlalchemy import func

from src.domain.entities.recomendacion import Recomendacion
from src.domain.ports.recomendacion_port import RecomendacionRepositoryPort
from src.infrastructure.database import SessionLocal, RecomendacionDB

class PostgresRecomendacionRepository(RecomendacionRepositoryPort):
    _ICONOS_VALIDOS = {
        '💡', '🤖', '🌊', '🛡️', '☀️', '📋', '⚠️', '✅', '🔧', '🌱',
        '🍃', '💧', '🌡️', '🧪', '🌿', '📝', '👀', '🚨'
    }

    def _normalizar_texto(self, value: Optional[str]) -> str:
        return (value or '').strip()

    def _normalizar_icono(self, value: Optional[str]) -> str:
        icono = self._normalizar_texto(value)
        if not icono:
            return '💡'

        # Si llega un valor corrupto o no reconocible, caemos a un icono seguro.
        if icono in self._ICONOS_VALIDOS:
            return icono

        if any(token in icono for token in ('�', 'Ã', 'ð', '?')):
            return '💡'

        return icono[:10]

    def _to_entity(self, r: RecomendacionDB) -> Recomendacion:
        return Recomendacion(
            id=r.id, prioridad=r.prioridad, accion=r.accion,
            descripcion=r.descripcion, variable=r.variable,
            icono=r.icono or '💡', confianza=r.confianza,
            aplicada=r.aplicada, fecha=r.created_at,
        )

    def _buscar_duplicado(self, db, rec: Recomendacion) -> Optional[RecomendacionDB]:
        accion = self._normalizar_texto(rec.accion)
        descripcion = self._normalizar_texto(rec.descripcion)
        variable = self._normalizar_texto(rec.variable)
        icono = self._normalizar_icono(rec.icono)

        return (
            db.query(RecomendacionDB)
            .filter(func.lower(func.trim(RecomendacionDB.prioridad)) == rec.prioridad.strip().lower())
            .filter(func.lower(func.trim(RecomendacionDB.accion)) == accion.lower())
            .filter(func.lower(func.coalesce(func.trim(RecomendacionDB.descripcion), '')) == descripcion.lower())
            .filter(func.lower(func.coalesce(func.trim(RecomendacionDB.variable), '')) == variable.lower())
            .filter(func.lower(func.trim(RecomendacionDB.icono)) == icono.lower())
            .first()
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
            existente = self._buscar_duplicado(db, rec)
            if existente:
                return self._to_entity(existente)

            row = RecomendacionDB(
                prioridad=self._normalizar_texto(rec.prioridad) or 'media',
                accion=self._normalizar_texto(rec.accion),
                descripcion=self._normalizar_texto(rec.descripcion) or None,
                variable=self._normalizar_texto(rec.variable) or None,
                icono=self._normalizar_icono(rec.icono),
                confianza=rec.confianza,
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
