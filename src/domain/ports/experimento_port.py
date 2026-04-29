from abc import ABC, abstractmethod
from src.domain.entities.experimento import Experimento
from typing import List, Optional

class ExperimentoRepositoryPort(ABC):
    @abstractmethod
    def get_all(self) -> List[Experimento]:
        pass

    @abstractmethod
    def save(self, exp: Experimento) -> Experimento:
        pass

    @abstractmethod
    def update(self, exp_id: int, data: dict) -> Optional[Experimento]:
        pass

    @abstractmethod
    def delete(self, exp_id: int) -> bool:
        pass
