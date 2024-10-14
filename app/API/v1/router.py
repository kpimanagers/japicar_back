from fastapi import APIRouter
from .modules.users import user_router
from .modules.auth import auth_router
from .modules.brands import brands_router
from .modules.cases import cases_router_client, cases_router_operations, cases_router_workshops
from .modules.notifications import notification_router
from .modules.no_participation_motives import no_participation_motives_router

v1_router = APIRouter()

v1_router.include_router(user_router)
v1_router.include_router(auth_router)
v1_router.include_router(brands_router)
v1_router.include_router(cases_router_client)
v1_router.include_router(cases_router_operations)
v1_router.include_router(cases_router_workshops)
v1_router.include_router(notification_router)
v1_router.include_router(no_participation_motives_router)
