import sys
from typing import List
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.param_functions import Depends
from sqlalchemy.orm.session import Session
from app.database.main import get_database

from ...middlewares.verify_token import verify_token
from ...services.security import get_password_hash
from app.API.v1.modules.users.schema import UserAutoRegister, UserItem
from app.API.v1.modules.users.model import User, AcceptedTerms

from ...services.send_mail import send_email
from .....config import config
from ..users.helpers.get_all_users_by_role_id import get_all_users_by_role_id
from ...helpers.constants.business import TEXTS_MESSAGES_NOTIFICATIONS
from ..notifications.helpers.create_notificacion import create_notification

router = APIRouter(prefix="/users", tags=["Users"])



@router.post("/auto-register")
async def create_user(body: UserAutoRegister, db: Session = Depends(get_database)):
    try:
        if (body.password != body.confirm_password):
            raise HTTPException(
                status_code=400,
                detail="las contraseñas no coinciden",
            )
        
        if not body.accept_terms:
            raise HTTPException(
                status_code=400,
                detail="Tienes que aceptar los términos y condiciones",
            )
        # validate email
        current_user = db.query(User).filter(User.email == body.email).first()
        if current_user:
            raise HTTPException(
                status_code=400,
                detail="El email ya esta registrado",
            )
       
        hashed_password = get_password_hash(body.password)
        user_data = body.dict()
        del user_data['confirm_password']
        del user_data['accept_terms']
        user_data['password'] = hashed_password
        user_data['role_id'] = 1 # Default role is CLIENTS

        new_user = User(**user_data)
        db.add(new_user)
        db.commit()
        db.flush(User)

        user_id = new_user.id
        accepted_terms = AcceptedTerms(user_id=user_id, description='ok')
        db.add(accepted_terms)
        db.commit()
        db.flush(AcceptedTerms)
        
        await send_email(
            recipients=[new_user.email],
            subject="¡Darte la bienvenida nos pone Japi!",
            template_file_path="templates/welcome.html",
            context={"name": f'{new_user.name.capitalize()} {new_user.last_name.capitalize()}', "url_client": config.CLIENT_DOMAIN},
        )

        notiication_data_client = {
            "user_id": user_id,
            "type_id": 15, #NOTIFY_WELCOME
            "message": f'¡Hola {new_user.name} {new_user.last_name}! Gracias por registrarte en Japicar. Ya puedes operar con nosotros. Equipo Japicar.cl',
        }

        await create_notification(notification=notiication_data_client, keyWs="UPDATE_NOTIFICATIONS_CLIENT", request=None, db=db)

        #email to operation
        all_emails = get_all_users_by_role_id(2, db, only_email=True) #OPERATIONS
        data_email_operations = {
            "client_name": f'{new_user.name} {new_user.last_name}',
            "client_phone": new_user.phone,
            "client_email": new_user.email,
            "client_id": new_user.id,
        }
        context_email_operations = {
            "data": data_email_operations,
        }

        await send_email(
            recipients=all_emails,
            subject="¡Nuevo Cliente de Japicar.cl!",
            template_file_path="templates/welcomeOperatiors.html",
            context=context_email_operations,
        )

        notiication_data_operations = {
            "role_id": 2, #OPERATIONS
            "type_id": 19, #NOTIFY_NEW_CLIENT
            "message": f'Tenemos un nuevo cliente en nuestro sistema, registro N° {new_user.id}. Equipo JapiCar.cl',
        }

        await create_notification(notification=notiication_data_operations, keyWs="UPDATE_NOTIFICATIONS_OPERATIONS", request=None, db=db)

        del user_data['password']
        return HTTPException(200, user_data)
    except Exception as err:
        print("Error in line:", sys.exc_info()[-1].tb_lineno)
        print("Error message : {0}".format(err))
        if hasattr( err, "detail"):
            
            raise HTTPException(
                status_code=400,
                detail= err.detail,
            )
        else:
            raise HTTPException(400, format(err))
        


@router.get("/get-all-users", dependencies=[Depends(verify_token)])
def get_all_users(request: Request, db: Session = Depends(get_database)):
    try:
        user_id_auth = request.user_id_auth
        print('user_id_auth =>>>>>>>>>>>>>>>>>>>>>', user_id_auth)
        return db.query(User).all()
    except Exception as err:
        print("Error in line:", sys.exc_info()[-1].tb_lineno)
        print("Error message : {0}".format(err))
        if hasattr( err, "detail"):
            
            raise HTTPException(
                status_code=400,
                detail= err.detail,
            )
        else:
            raise HTTPException(400, format(err))



@router.post("/generate-password")
async def generate_password(pwd: str, db: Session = Depends(get_database)):
    try:
        if pwd is None or pwd == '':
            raise HTTPException(
                status_code=400,
                detail="La contraseña no puede estar vacía",
            )

        hashed_password = get_password_hash(pwd)
        return hashed_password
    except Exception as err:
        print("Error in line:", sys.exc_info()[-1].tb_lineno)
        print("Error message : {0}".format(err))
