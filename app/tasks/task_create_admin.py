from typing import Annotated

from dependencies import get_user_service
from domain.interfaces import IUserService
from infrastructure.deps_injector import Depends, use_services


@use_services()
async def task_create_admin(
    user_service: Annotated[IUserService, Depends(get_user_service)],
):
    await user_service.create_admin_record()
