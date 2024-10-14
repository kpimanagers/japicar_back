import sys
from fastapi import APIRouter, security, status, Response
from fastapi.exceptions import HTTPException
from fastapi.params import Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.params import Depends
from fastapi.responses import JSONResponse
from sqlalchemy import exc
from sqlalchemy.orm import Session, joinedload
from starlette.requests import Request
from .....config import config
from app.database.main import get_database
from ...services.security import (
    verify_password,
    create_access_token,
    create_refresh_token,
    create_recovery_token,
    get_password_hash,
    decodeRecoverJWT,
)
from ...middlewares.auth import decodeJWT
from ..users.model import User
from .schema import (
    LoginSchema,
    MeResponseSchema,
    RecoverPasswordSchema,
    PasswordChangeSchema,
)
from ...middlewares.verify_token import upadte_token
from ...services.send_mail import send_email

router = APIRouter(prefix="/auth", tags=["Auth"])
security = HTTPBearer()


def is_authenticated(auth_token):
    try:
        if decodeJWT(auth_token):
            return get_database
        else:
            return False

    except Exception as err:
        print("Error message {0}".format(err))


def auth_wrapper(auth: HTTPAuthorizationCredentials = Security(security)):
    return is_authenticated(auth.credentials)


@router.post("/login")
async def login_user(login_obj: LoginSchema, response: Response, db: Session = Depends(get_database)):
    try:
        found_user = db.query(User).options(joinedload(User.role)).filter(User.email == login_obj.email).first()


        if not found_user:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Este usuario no está registrado",
            )
        
        match_password = verify_password(login_obj.password, found_user.password)
        if not match_password:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Credenciales incorrectas"
            )
        
        user_obj = {
            "accessToken": create_access_token(found_user.id),
            "refreshToken": create_refresh_token(found_user.id),
            "user": {
                "id": found_user.id,
                "name": found_user.name,
                "lastName": found_user.last_name,
                "email": found_user.email,
                "phone": found_user.phone,
                "workshopId": found_user.workshop_id,
                "roleId": found_user.role_id,
                "role": {
                    "id": found_user.role.id,
                    "name": found_user.role.name
                },
                "workshop": {
                    "id": found_user.workshop.id if found_user.workshop is not None else None,
                    "name": found_user.workshop.name if found_user.workshop is not None else None,
                }
            }
        }
        
        response = JSONResponse(content=user_obj)
        response.set_cookie(key='accessToken', value=user_obj['accessToken'], httponly=False, secure=False)
        response.set_cookie(key='refreshToken', value=user_obj['refreshToken'], httponly=False, secure=False)
        return response
    except exc.SQLAlchemyError as err:
        print('line error', sys.exc_info()[-1].tb_lineno)

        raise HTTPException(404, format(err))


@router.get("/me", response_model=MeResponseSchema, dependencies=[Depends(upadte_token)])
async def get_logged_user(request: Request, db: Session = Depends(get_database)):
    try:
        new_token_obj = request.new_token_obj
        return JSONResponse(content=new_token_obj)

    except Exception as err:
        print("Error message : {0}".format(err))
        if hasattr(err, "detail"):
            raise HTTPException(err.status_code, format(err.detail))
        else:
            raise HTTPException(404, format(err))



@router.post("/forgot-password")
async def recover_password(
    body: RecoverPasswordSchema, db: Session = Depends(get_database)
):
    try:
        found_user = db.query(User).filter(User.email == body.email).first()
        if not found_user:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Este email no está registrado",
            )
        recovery_token = create_recovery_token(found_user.id)
        print('recovery_token', recovery_token)

        await send_email(
            recipients=[found_user.email],
            subject="Recuperación de contraseña",
            template_file_path="templates/forgotPassword.html",
            context={"name": f'{found_user.name} {found_user.last_name}', "recovery_url": f'{config.CLIENT_DOMAIN}/auth/recover-password?recovery_token={recovery_token}'},
        )

        return JSONResponse(
            status_code=200,
            content={"message": "EMAIL_SENT"},
        )

    except Exception as err:
        print("Error message : {0}".format(err))
        if hasattr(err, "detail"):
            raise HTTPException(404, format(err.detail))
        else:
            raise HTTPException(404, format(err))


@router.post("/recover-password")
async def recovery_password(
    body: PasswordChangeSchema, db: Session = Depends(get_database)
):
    print('body', body)
    try:
        token = decodeRecoverJWT(body.recovery_token)
        print('token', token)
        if not token:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="El tiempo para cambiar la contraseña ha expirado, favor volver a enviar el correo de recuperación"
            )

        user = db.query(User).filter(User.id == token["sub"]).first()

        setattr(user, "password", get_password_hash(body.new_password))

        db.add(user)
        db.commit()
        db.flush(user)

        return JSONResponse(
            status_code=200,
            content={"message": "USER_UPDATED"},
        )

    except Exception as err:
        print("Error message : {0}".format(err))
        if hasattr(err, "detail"):
            raise HTTPException(404, format(err.detail))
        else:
            raise HTTPException(404, format(err))


