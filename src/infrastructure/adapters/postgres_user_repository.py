import uuid as uuid_module
from src.domain.entities.user import User
from src.domain.ports.user_repository_port import UserRepositoryPort
from src.infrastructure.database import SessionLocal, UserDB
from typing import Optional, List

AVATAR_POR_ROL = {'admin': '🌳', 'docente': '🌿', 'estudiante': '🌱'}

class PostgresUserRepository(UserRepositoryPort):
    def _to_entity(self, u: UserDB) -> User:
        return User(
            id=u.id, username=u.username, nombre=u.nombre,
            email=u.email, password_hash=u.password_hash,
            rol=u.rol, avatar=u.avatar, activo=u.activo,
            created_at=u.created_at,
        )

    def get_by_username(self, username: str) -> Optional[User]:
        db = SessionLocal()
        try:
            row = db.query(UserDB).filter(UserDB.username == username).first()
            return self._to_entity(row) if row else None
        finally:
            db.close()

    def get_by_id(self, user_id: str) -> Optional[User]:
        db = SessionLocal()
        try:
            row = db.query(UserDB).filter(UserDB.id == uuid_module.UUID(user_id)).first()
            return self._to_entity(row) if row else None
        finally:
            db.close()

    def get_all(self) -> List[User]:
        db = SessionLocal()
        try:
            return [self._to_entity(u) for u in db.query(UserDB).all()]
        finally:
            db.close()

    def create(self, user: User) -> User:
        db = SessionLocal()
        try:
            avatar = user.avatar or AVATAR_POR_ROL.get(user.rol, '🌱')
            row = UserDB(
                username=user.username, nombre=user.nombre, email=user.email,
                password_hash=user.password_hash, rol=user.rol, avatar=avatar,
            )
            db.add(row)
            db.commit()
            db.refresh(row)
            return self._to_entity(row)
        finally:
            db.close()

    def update(self, user_id: str, data: dict) -> Optional[User]:
        db = SessionLocal()
        try:
            row = db.query(UserDB).filter(UserDB.id == uuid_module.UUID(user_id)).first()
            if not row:
                return None
            for key, value in data.items():
                if hasattr(row, key) and value is not None:
                    setattr(row, key, value)
            if 'rol' in data:
                row.avatar = AVATAR_POR_ROL.get(data['rol'], row.avatar)
            db.commit()
            db.refresh(row)
            return self._to_entity(row)
        finally:
            db.close()

    def delete(self, user_id: str) -> bool:
        db = SessionLocal()
        try:
            row = db.query(UserDB).filter(UserDB.id == uuid_module.UUID(user_id)).first()
            if not row:
                return False
            db.delete(row)
            db.commit()
            return True
        finally:
            db.close()

    def toggle_active(self, user_id: str) -> Optional[User]:
        db = SessionLocal()
        try:
            row = db.query(UserDB).filter(UserDB.id == uuid_module.UUID(user_id)).first()
            if not row:
                return None
            row.activo = not row.activo
            db.commit()
            db.refresh(row)
            return self._to_entity(row)
        finally:
            db.close()
