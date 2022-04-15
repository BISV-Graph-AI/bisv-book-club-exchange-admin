from datetime import datetime
from datetime import timedelta
from typing import Optional

from core.config import settings
from jose import jwt

from fastapi import Security, HTTPException
from fastapi.security.api_key import APIKeyQuery, APIKeyCookie, APIKeyHeader, APIKey

from starlette.status import HTTP_403_FORBIDDEN, HTTP_401_UNAUTHORIZED
from starlette.responses import RedirectResponse, JSONResponse


API_KEY_NAME = "access_token"
api_key_query = APIKeyQuery(name=API_KEY_NAME, auto_error=False)
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)
api_key_cookie = APIKeyCookie(name=API_KEY_NAME, auto_error=False)


async def get_api_key_default(
    api_key_query: str = Security(api_key_query),
    api_key_header: str = Security(api_key_header),
    api_key_cookie: str = Security(api_key_cookie)
):
    api_key = None
    if (api_key_query is not None):
        api_key = api_key_query
    elif (api_key_header is not None):
        api_key = api_key_header
    elif (api_key_cookie is not None):
        api_key = api_key_cookie

    return api_key


async def get_api_key(
    api_key_query: str = Security(api_key_query),
    api_key_header: str = Security(api_key_header),
    api_key_cookie: str = Security(api_key_cookie),
):
    credentials_401_exception = HTTPException(
        status_code=HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    credentials_403_exception = HTTPException(
        status_code=HTTP_403_FORBIDDEN,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    api_key = None
    if (api_key_query is not None):
        api_key = api_key_query
    elif (api_key_header is not None):
        api_key = api_key_header
    elif (api_key_cookie is not None):
        api_key = api_key_cookie
    if (api_key is None):
        raise credentials_401_exception
    return api_key


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt
