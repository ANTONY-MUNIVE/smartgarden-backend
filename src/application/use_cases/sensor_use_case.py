from src.domain.ports.repository_port import SensorRepositoryPort
from src.domain.entities.sensor import SensorReading
from sqlalchemy.exc import OperationalError

class SensorUseCase:
    def __init__(self, repository: SensorRepositoryPort):
        self.repository = repository

    def registrar_lectura(self, data: dict):
        # Aquí puedes agregar lógica: ej. disparar alerta si la temp > 40
        nueva_lectura = SensorReading(**data)
        try:
            return self.repository.save(nueva_lectura)
        except OperationalError:
            return nueva_lectura

    def obtener_estado_actual(self):
        try:
            return self.repository.get_latest()
        except OperationalError:
            return None

    def obtener_historial(self, limit: int = 24):
        try:
            return self.repository.get_history(limit)
        except OperationalError:
            return []
