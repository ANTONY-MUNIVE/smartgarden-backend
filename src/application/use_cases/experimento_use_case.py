from src.domain.ports.experimento_port import ExperimentoRepositoryPort
from src.domain.entities.experimento import Experimento
from sqlalchemy.exc import OperationalError

class ExperimentoUseCase:
    def __init__(self, repository: ExperimentoRepositoryPort):
        self.repository = repository

    def obtener_experimentos(self):
        try:
            return self.repository.get_all()
        except OperationalError:
            return []

    def crear_experimento(self, data: dict):
        exp = Experimento(**data)
        try:
            return self.repository.save(exp)
        except OperationalError:
            return exp

    def actualizar_experimento(self, exp_id: int, data: dict):
        try:
            return self.repository.update(exp_id, data)
        except OperationalError:
            return None

    def eliminar_experimento(self, exp_id: int):
        try:
            return self.repository.delete(exp_id)
        except OperationalError:
            return False
