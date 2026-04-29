from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List

@dataclass
class Experimento:
    titulo: str
    hipotesis: str
    cultivo: Optional[str] = None
    duracion: Optional[int] = None
    progreso: int = 0
    estado: str = 'pendiente'
    observaciones: int = 0
    variables: List[str] = field(default_factory=list)
    id: Optional[int] = None
    fecha: Optional[datetime] = None

    def to_dict(self):
        return {
            "id": self.id,
            "titulo": self.titulo,
            "hipotesis": self.hipotesis,
            "cultivo": self.cultivo,
            "duracion": self.duracion,
            "progreso": self.progreso,
            "estado": self.estado,
            "observaciones": self.observaciones,
            "variables": self.variables or [],
            "fecha": self.fecha.isoformat() if self.fecha else None,
        }
