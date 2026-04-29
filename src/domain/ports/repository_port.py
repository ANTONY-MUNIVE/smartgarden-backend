from abc import ABC, abstractmethod
from src.domain.entities.sensor import SensorReading
from typing import List

class SensorRepositoryPort(ABC):
    @abstractmethod
    def save(self, reading: SensorReading) -> SensorReading:
        pass

    @abstractmethod
    def get_latest(self) -> SensorReading:
        pass

    @abstractmethod
    def get_history(self, limit: int = 24) -> List[SensorReading]:
        pass
