from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict

@dataclass
class EtapaCultivo:
    nombre: str
    estado: str = 'pendiente'
    fecha: Optional[str] = None
    icono: str = '🌱'
    descripcion: Optional[str] = None
    datos: Dict = field(default_factory=dict)
    id: Optional[int] = None
    created_at: Optional[datetime] = None

    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "estado": self.estado,
            "fecha": self.fecha,
            "icono": self.icono,
            "descripcion": self.descripcion,
            "datos": self.datos or {},
        }
