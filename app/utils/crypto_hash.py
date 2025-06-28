from abc import ABC, abstractmethod

from argon2 import PasswordHasher, exceptions


class AbstractCrypto(ABC):
    @abstractmethod
    def hash(self, value: str) -> str:
        """return hashed value"""
        ...

    @abstractmethod
    def verify(self, value: str, hash: str) -> bool:
        """Verify hashed value"""
        ...


class Argon2Crypto(AbstractCrypto):
    def __init__(self) -> None:
        self.hasher = PasswordHasher()

    def hash(self, value: str) -> str:
        return self.hasher.hash(value)

    def verify(self, value: str, hash: str) -> bool:
        try:
            return self.hasher.verify(hash, value)
        except exceptions.VerifyMismatchError:
            return False
