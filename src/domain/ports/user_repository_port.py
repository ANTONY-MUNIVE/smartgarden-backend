from abc import ABC, abstractmethod
from src.domain.entities.user import User
from typing import Optional, List

class UserRepositoryPort(ABC):
    @abstractmethod
    def get_by_username(self, username: str) -> Optional[User]:
        pass

    @abstractmethod
    def get_by_id(self, user_id: str) -> Optional[User]:
        pass

    @abstractmethod
    def get_all(self) -> List[User]:
        pass

    @abstractmethod
    def create(self, user: User) -> User:
        pass

    @abstractmethod
    def update(self, user_id: str, data: dict) -> Optional[User]:
        pass

    @abstractmethod
    def delete(self, user_id: str) -> bool:
        pass

    @abstractmethod
    def toggle_active(self, user_id: str) -> Optional[User]:
        pass
