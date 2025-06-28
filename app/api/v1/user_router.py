from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse

from api.auth import check_token, jwt_token
from domain.exceptions import DoubleFoundError, NotFoundError, PermissionException, RepositoryException
from domain.models.user import User
from domain.services.user_service import IUserService

from ..dependencies import get_user_service
from .schemas.user_schema import (
    UserCreateSchema,
    UserLoginSchema,
    UserReadSchema,
    UserTokenSchema,
    UserUpdatePasswordSchema,
)

router = APIRouter(
    prefix="/users",
    tags=["/v1/users"],
    responses={404: {"description": "User not found"}},
    redirect_slashes=False,
)


@router.post("/login", response_model=UserTokenSchema)
@router.post("/login/", include_in_schema=False)
async def login(
    user_data: UserLoginSchema,
    service: Annotated[IUserService, Depends(get_user_service)]
):
    try:
        user = await service.verify_password(**user_data.model_dump())
        token = jwt_token.create(user.username, user.hashed_password)

        response = JSONResponse(
            content={
                "id": user.id,
                "username": user.username,
                "level": user.level,
                "token": token,
            }
        )

        response.set_cookie(
            key="TOKEN",
            value=token,
            httponly=True,
            secure=False,
            samesite="lax",
            path="/"
        )

        return response

    except NotFoundError:
        raise HTTPException(401, "Wrong username or password")


@router.post("/update_password", response_model=UserReadSchema)
@router.post("/update_password/", include_in_schema=False)
async def update_user_password(
    data: UserUpdatePasswordSchema,
    service: Annotated[IUserService, Depends(get_user_service)],
    user: Annotated[User, Depends(check_token)],
) -> UserReadSchema | None:
    try:
        updated_user = await service.update_password(
            username=user.username,
            old_password=data.old_password,
            new_password=data.new_password,
        )
        return UserReadSchema(**updated_user.model_dump())
    except RepositoryException as ex:
        raise HTTPException(401, str(ex))


@router.get("/{id}", response_model=UserReadSchema)
@router.get("/{id}/", include_in_schema=False)
async def read_user(
    id: int,
    user: Annotated[User, Depends(check_token)],
) -> UserReadSchema:
    try:
        return UserReadSchema(**user.model_dump())
    except ValueError as ex:
        raise HTTPException(422, str(ex))
    except NotFoundError:
        raise HTTPException(404, f"User with id {id} not found.")


@router.post("", response_model=UserReadSchema)
@router.post("/", include_in_schema=False)
async def create_user(
    data: UserCreateSchema,
    service: Annotated[IUserService, Depends(get_user_service)],
    user: Annotated[User, Depends(check_token)],
) -> UserReadSchema:
    try:
        user = await service.create(user=user, **data.model_dump())
        return UserReadSchema.model_validate(user)
    except DoubleFoundError as ex:
        raise HTTPException(422, str(ex))
    except PermissionException as ex:
        raise HTTPException(403, str(ex))
