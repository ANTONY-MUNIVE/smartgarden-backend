from abc import ABC, abstractmethod
from src.domain.entities.alerta import Alerta
from typing import List

class AlertaRepositoryPort(ABC):
    @abstractmethod
    def get_all(self) -> List[Alerta]:
        pass

    @abstractmethod
    def save(self, alerta: Alerta) -> Alerta:
        pass
