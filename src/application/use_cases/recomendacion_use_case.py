from src.domain.ports.recomendacion_port import RecomendacionRepositoryPort
from src.domain.entities.recomendacion import Recomendacion
from sqlalchemy.exc import OperationalError

class RecomendacionUseCase:
    def __init__(self, repository: RecomendacionRepositoryPort):
        self.repository = repository

    def obtener_recomendaciones(self):
        try:
            return self.repository.get_all()
        except OperationalError:
            return []

    def aplicar_recomendacion(self, rec_id: int):
        try:
            return self.repository.aplicar(rec_id)
        except OperationalError:
            return None

    def crear_recomendacion(self, data: dict):
        """Crea y guarda una nueva recomendación en la persistencia."""
        try:
            rec = Recomendacion(
                prioridad=data.get("prioridad", "media"),
                accion=data.get("accion", ""),
                descripcion=data.get("descripcion"),
                variable=data.get("variable"),
                icono=data.get("icono", "💡"),
                confianza=data.get("confianza"),
            )
            return self.repository.save(rec)
        except OperationalError:
            return None
