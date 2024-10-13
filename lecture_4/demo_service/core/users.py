from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Callable

from pydantic import BaseModel, SecretStr


class UserRole(str, Enum):
    USER: str = "user"
    ADMIN: str = "admin"


class UserInfo(BaseModel):
    username: str
    name: str
    birthdate: datetime
    role: UserRole = UserRole.USER
    password: SecretStr


class UserEntity(BaseModel):
    uid: int
    info: UserInfo


@dataclass(slots=True)
class UserService:
    password_validators: list[Callable[[str], bool]] = field(default_factory=list)

    _data: dict[int, UserEntity] = field(init=False, default_factory=dict)
    _username_index: dict[str, int] = field(init=False, default_factory=dict)
    _last_id: int = field(init=False, default=0)

    def register(self, user_info: UserInfo) -> UserEntity:
        if user_info.username in self._username_index:
            raise ValueError("username is already taken")

        for password_validator in self.password_validators:
            if not password_validator(user_info.password.get_secret_value()):
                raise ValueError("invalid password")

        self._last_id += 1

        entity = UserEntity(uid=self._last_id, info=user_info)

        self._data[entity.uid] = entity
        self._username_index[entity.info.username] = entity.uid

        return entity

    def get_by_username(self, username: str) -> UserEntity | None:
        if username not in self._username_index:
            return None

        return self._data[self._username_index[username]]

    def get_by_id(self, uid: int) -> UserEntity | None:
        return self._data.get(uid)

    def grant_admin(self, user_id: int) -> None:
        user = self.get_by_id(user_id)

        if user is None:
            raise ValueError("user not found")

        user.info.role = UserRole.ADMIN
        self._data[user.uid] = user


def password_is_longer_than_8(password: str) -> bool:
    return len(password) > 8
