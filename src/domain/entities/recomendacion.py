from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

@dataclass
class Recomendacion:
    prioridad: str
    accion: str
    descripcion: Optional[str] = None
    variable: Optional[str] = None
    icono: str = '💡'
    confianza: Optional[float] = None
    aplicada: bool = False
    id: Optional[int] = None
    fecha: Optional[datetime] = None

    def to_dict(self):
        return {
            "id": self.id,
            "prioridad": self.prioridad,
            "accion": self.accion,
            "descripcion": self.descripcion,
            "variable": self.variable,
            "icono": self.icono,
            "confianza": self.confianza,
            "aplicada": self.aplicada,
            "fecha": self.fecha.isoformat() if self.fecha else None,
        }
