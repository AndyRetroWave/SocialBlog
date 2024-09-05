from datetime import datetime, timedelta
from pathlib import Path

import aiofiles
import jwt
from pydantic import BaseModel

from apps.config import settings
from apps.user.shemas import UserShemas

TOKEN_TYPE_FIELD = "type"
ACCESS_TOKEN_TYPE = "access_token"
REFRESH_TOKEN_TYPE = "refresh_token"


class TokenInfo(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str = "Bearer"


async def read_key(path: Path) -> str:
    async with aiofiles.open(path, mode="r") as f:
        return await f.read()


async def encode_jwt(
    payload: dict,
    algorithm: str = settings.AUTH_JWT.algorithm,
    expire_minutes: int = settings.AUTH_JWT.access_token_expire_minutes,
    expire_timedelta: timedelta | None = None,
) -> str:
    to_encode: dict = payload.copy()
    now: datetime = datetime.utcnow()
    if expire_timedelta:
        expire: str = now + expire_timedelta
    else:
        expire: str = now + timedelta(minutes=expire_minutes)
    to_encode.update({"exp": expire, "iat": now})
    private_key = await read_key(settings.AUTH_JWT.private_key_path)
    encoded = jwt.encode(to_encode, private_key, algorithm=algorithm)
    return encoded


async def decode_jwt(token: str | bytes, algorithm: str = settings.AUTH_JWT.algorithm):
    public_key: str = await read_key(settings.AUTH_JWT.public_key_path)
    decoded = jwt.decode(token, public_key, algorithms=[algorithm])
    return decoded


async def create_jwt(
    token_type: str,
    token_data: dict,
    expires_minutes: int,
    expires_timedelta: timedelta | None = None,
) -> str:
    jwt_payload = {TOKEN_TYPE_FIELD: token_type}
    jwt_payload.update(token_data)
    return await encode_jwt(
        payload=jwt_payload,
        expire_minutes=expires_minutes,
        expire_timedelta=expires_timedelta,
    )


async def create_access_token(user: UserShemas) -> str:
    payload = {
        "sub": user.email,
        "given_name": user.given_name,
        "family_name": user.family_name,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(minutes=15),
    }
    return await create_jwt(
        token_type=ACCESS_TOKEN_TYPE,
        token_data=payload,
        expires_minutes=settings.AUTH_JWT.access_token_expire_minutes,
    )


async def create_refresh_token(user: UserShemas) -> str:
    fwt_payload = {
        "sub": user.email,
    }
    return await create_jwt(
        token_type=REFRESH_TOKEN_TYPE,
        token_data=fwt_payload,
        expires_minutes=settings.AUTH_JWT.refresh_token_expire_minutes,
    )
