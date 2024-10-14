from fastapi import HTTPException, Request, status
from ..services.security import decodeJWT
import time


def verify_cookie(request: Request):
    cookie_value = request.cookies.get("accessToken")
    
    if not cookie_value:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cookie is missing")

    token_data = decodeJWT(cookie_value)

    if not token_data:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Token is missing")
    
    user_id = token_data["sub"]
    token_expiration_timestamp  = token_data["exp"]

    if token_expiration_timestamp is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Token is expired")
    

    current_timestamp = int(time.time())
    if current_timestamp > token_expiration_timestamp:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Token is expired")
    

    request.user_id_auth = user_id



