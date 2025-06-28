from abc import ABC, abstractmethod
from datetime import datetime, timedelta, timezone

import jwt
from jwt import ExpiredSignatureError, InvalidTokenError

from domain.exceptions import ValueException


class AbstractJWTToken(ABC):
    expires_minutes: int
    secret: str
    algorithm: str = "HS256"

    @abstractmethod
    def create(self, username: str, hashed_password: str | None) -> str:
        """Return new JWT token"""
        ...

    @abstractmethod
    def verify(self, token: str) -> tuple[str, str]:
        """Returns tuple[username, hashed_password]"""
        ...


class JWTToken(AbstractJWTToken):
    def __init__(
        self,
        expires_minutes: int,
        secret: str,
        algorithm: str = "HS256",
    ) -> None:
        self.expires_minutes = expires_minutes
        self.secret = secret
        self.algorithm = algorithm

    def create(self, username: str, hashed_password: str | None) -> str:
        expire = datetime.now(timezone.utc) + timedelta(minutes=self.expires_minutes)
        # PyJWT корректно преобразует datetime в timestamp для claim "exp"
        payload = {
            "username": username,
            "hashed_password": hashed_password,
            "exp": expire,
        }
        encoded_jwt = jwt.encode(payload, self.secret, algorithm=self.algorithm)
        return encoded_jwt

    def verify(self, token: str) -> tuple[str, str]:
        try:
            payload = jwt.decode(token, self.secret, algorithms=[self.algorithm])
            username = payload.get("username")
            hashed_password = payload.get("hashed_password")
            if username is None or hashed_password is None:
                raise ValueException("User or password is missing in token payload")
            return username, hashed_password
        except ExpiredSignatureError:
            raise ValueException("Token is expired")
        except (InvalidTokenError, Exception) as ex:
            raise ValueException(str(ex))
