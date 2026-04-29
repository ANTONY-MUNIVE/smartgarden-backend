from src.domain.ports.etapa_port import EtapaRepositoryPort
from sqlalchemy.exc import OperationalError

class EtapaUseCase:
    def __init__(self, repository: EtapaRepositoryPort):
        self.repository = repository

    def obtener_etapas(self):
        try:
            return self.repository.get_all()
        except OperationalError:
            return []

    def actualizar_etapa(self, etapa_id: int, data: dict):
        try:
            return self.repository.update(etapa_id, data)
        except OperationalError:
            return None
