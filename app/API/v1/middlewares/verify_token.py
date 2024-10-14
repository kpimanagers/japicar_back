from fastapi import HTTPException, Request, status
from ..services.security import decodeJWT
import time
from ..services.security import create_access_token


def verify_token(request: Request):
    # Obtener el encabezado Authorization
    auth_header = request.headers.get("Authorization")

    
    if not auth_header:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Authorization header is missing")

    # Eliminar el prefijo 'Bearer ' del valor del encabezado
    token = auth_header.split(" ")[1] if " " in auth_header else None
    
    if not token:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Token is missing")

    token_data = decodeJWT(token)

    if not token_data:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid token")
    
    user_id = token_data["sub"]
    token_expiration_timestamp = token_data["exp"]

    if token_expiration_timestamp is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Token is expired")

    current_timestamp = int(time.time())
    if current_timestamp > token_expiration_timestamp:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Token is expired")

    request.user_id_auth = user_id


def upadte_token(request: Request):
    # Obtener el encabezado Authorization
    auth_header = request.headers.get("Authorization")

    if not auth_header:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Authorization header is missing")

    # Eliminar el prefijo 'Bearer ' del valor del encabezado
    token = auth_header.split(" ")[1] if " " in auth_header else None
    
    if not token:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Token is missing")
    
    token_data = decodeJWT(token)
    
    print('token_data===>', token_data)
    if not token_data:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid token")
    
    user_id = token_data["sub"]
    token_expiration_timestamp = token_data["exp"]
    valid_try = int(token_data["valid_try"])

    print("token_expiration_timestamp===>", token_expiration_timestamp)
    print('valid_try===>', valid_try)

    if token_expiration_timestamp is None:

        if (valid_try > 0):
            new_valid_try = valid_try - 1
            new_token = create_access_token(user_id, new_valid_try)


            new_token_obj ={
                "accessToken": new_token,
            }

            request.new_token_obj = new_token_obj
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Token is expired")
    
    new_token_obj ={
        "accessToken": token,
    }

    request.new_token_obj = new_token_obj

        

