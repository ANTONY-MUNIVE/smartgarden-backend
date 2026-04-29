from abc import ABC, abstractmethod
from src.domain.entities.recomendacion import Recomendacion
from typing import List, Optional

class RecomendacionRepositoryPort(ABC):
    @abstractmethod
    def get_all(self) -> List[Recomendacion]:
        pass

    @abstractmethod
    def save(self, rec: Recomendacion) -> Recomendacion:
        pass

    @abstractmethod
    def aplicar(self, rec_id: int) -> Optional[Recomendacion]:
        pass
