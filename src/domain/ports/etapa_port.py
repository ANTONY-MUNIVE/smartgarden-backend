from abc import ABC, abstractmethod
from src.domain.entities.etapa import EtapaCultivo
from typing import List, Optional

class EtapaRepositoryPort(ABC):
    @abstractmethod
    def get_all(self) -> List[EtapaCultivo]:
        pass

    @abstractmethod
    def update(self, etapa_id: int, data: dict) -> Optional[EtapaCultivo]:
        pass
