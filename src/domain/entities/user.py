from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class User:
    username: str
    nombre: str
    password_hash: str
    rol: str
    email: Optional[str] = None
    avatar: Optional[str] = None
    activo: bool = True
    id: Optional[str] = None
    created_at: Optional[datetime] = None

    def to_dict(self):
        return {
            "id": str(self.id) if self.id else None,
            "username": self.username,
            "nombre": self.nombre,
            "email": self.email,
            "rol": self.rol,
            "avatar": self.avatar,
            "activo": self.activo,
        }
