from typing import Annotated

from fastapi import Depends, HTTPException, Security, status
from fastapi.security.api_key import APIKeyHeader

from api.dependencies import get_user_service
from config.config import settings
from domain.exceptions import NotFoundError, ValueException
from domain.models.user import User
from domain.services.user_service import IUserService
from utils.jwt_token import JWTToken

api_key_header = APIKeyHeader(name="TOKEN", auto_error=True)
jwt_token = JWTToken(
    expires_minutes=settings.JWT_TOKEN_EXPIRE_MINUTES,
    secret=settings.SECRET,
    algorithm=settings.JWT_ALGORITHM,
)


# authentication
async def check_token(
    service: Annotated[IUserService, Depends(get_user_service)],
    token: str = Security(api_key_header),
) -> User:
    """Check token in the Headers and return a user or raise 401 exception"""
    try:
        username, hashed_password = jwt_token.verify(token)

        return await service.read(filters={"username": username, "hashed_password": hashed_password})
    except (NotFoundError, ValueException):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
