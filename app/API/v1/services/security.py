from datetime import datetime, timedelta
from typing import Any, Union
from jose import jwt
from passlib.context import CryptContext
from ....config import config

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = "HS256"


def create_access_token(subject: Union[str, Any], valid_try: int = 4) -> str:
    expire = datetime.utcnow() + timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"exp": expire, "sub": str(subject), "valid_try": valid_try}
    encoded_jwt = jwt.encode(to_encode, config.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(subject: Union[str, Any]) -> str:
    expire = datetime.utcnow() + timedelta(minutes=config.REFRESH_TOKEN_EXPIRE_MINUTES)
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, config.REFRESH_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_recovery_token(subject: Union[str, Any]) -> str:
    expire = datetime.utcnow() + timedelta(minutes=config.RECOVERY_TOKEN_EXPIRE_MINUTES)
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, config.RECOVERY_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def decodeJWT(token: str) -> dict:
    try:
        
        decoded_token = jwt.decode(token, config.SECRET_KEY, algorithms=ALGORITHM)
        
        return (
            decoded_token
            if decoded_token["exp"] >= datetime.utcnow().timestamp()
            else None
        )
    except Exception as e:
        print(e)
        return {}


def decodeRefreshJWT(token: str) -> dict:
    try:
        decoded_token = jwt.decode(token, config.REFRESH_KEY, algorithms=ALGORITHM)
        return (
            decoded_token
            if decoded_token["exp"] >= datetime.utcnow().timestamp()
            else None
        )
    except Exception as e:
        print(e)
        return {}



def decodeRecoverJWT(token: str) -> dict:
    try:
        decoded_token = jwt.decode(token, config.RECOVERY_KEY, algorithms=ALGORITHM)
        print('decoded_token', decoded_token)
        return (
            decoded_token
            if decoded_token["exp"] >= datetime.utcnow().timestamp()
            else None
        )
    except Exception as e:
        print(e)
        return {}
