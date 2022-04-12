from fastapi import APIRouter
from webapps.auth import route_login
from webapps.sellers import route_sellers
from webapps.users import route_users


api_router = APIRouter()
api_router.include_router(route_sellers.router, prefix="", tags=["sellers-webapp"])
api_router.include_router(route_users.router, prefix="", tags=["users-webapp"])
api_router.include_router(route_login.router, prefix="", tags=["auth-webapp"])
