from src.domain.ports.alerta_port import AlertaRepositoryPort
from src.domain.entities.alerta import Alerta
from sqlalchemy.exc import OperationalError

class AlertaUseCase:
    def __init__(self, repository: AlertaRepositoryPort):
        self.repository = repository

    def obtener_alertas(self):
        try:
            return self.repository.get_all()
        except OperationalError:
            return []

    def crear_alerta(self, data: dict):
        alerta = Alerta(**data)
        try:
            return self.repository.save(alerta)
        except OperationalError:
            return alerta
