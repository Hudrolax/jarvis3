from domain.services.messages.domain_router import DomainMessageRouter
from domain.services.messages.middlewares import middleware
from domain.services.messages.routers import router as test_router

main_router = DomainMessageRouter()
main_router.include_middleware(middleware)
main_router.include_router(test_router)
