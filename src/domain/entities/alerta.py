from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Alerta:
    tipo: str
    variable: str
    mensaje: str
    id: Optional[int] = None
    fecha: Optional[datetime] = None

    def to_dict(self):
        return {
            "id": self.id,
            "tipo": self.tipo,
            "variable": self.variable,
            "mensaje": self.mensaje,
            "fecha": self.fecha.isoformat() if self.fecha else None,
        }
