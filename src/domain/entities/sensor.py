from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class SensorReading:
    humedad_suelo: float
    temperatura: float
    luminosidad: float
    humedad_ambiental: float
    id: Optional[int] = None
    fecha: datetime = datetime.now()

    def to_dict(self):
        return {
            "id": self.id,
            "humedad_suelo": self.humedad_suelo,
            "temperatura": self.temperatura,
            "luminosidad": self.luminosidad,
            "humedad_ambiental": self.humedad_ambiental,
            "fecha": self.fecha.isoformat()
        }
