import sys
from pytz import timezone
from datetime import datetime, timedelta
from sqlalchemy.orm.session import Session
from sqlalchemy.orm import joinedload
from .config import config


from app.database.main import SessionLocal
from app.API.v1.modules.cases.helpers.quote_by_case_id_and_user_id import get_all_quotes_by_case_id
from app.API.v1.modules.cases.model import Case
from app.API.v1.modules.users.helpers.get_all_users_by_role_id import get_all_users_by_role_id
from app.API.v1.modules.users.helpers.get_user_by_id import get_user_by_id
from app.API.v1.services.send_mail import send_email
from app.API.v1.modules.notifications.helpers.create_notificacion import create_notification
from app.API.v1.helpers.constants.business import TEXTS_MESSAGES_NOTIFICATIONS

CHILE_TZ = timezone('America/Santiago')

MAX_NUMBER = config.MAX_NUMBER_QUOTE_BY_CASE


""" 
1,- select a todos los casos con un estado de "INUOTATION" con un rango de fecha desde HOY a las 12:00AM hasta MANANA a las 12:00AM. [DONE]
2,- recorrer los casos y verificar el campo "end_term" con la fecha actual.
3,- si es igual o menor a la fecha actual, se actualizara el estado de "INUOTATION" a "DEADLINE_EXPIRED".
4,- enviar notificacion y correo a todos los talleres, pero excluyendo a los que marcaron el caso como "sin participacion".
"""
async def task_12_am():
    try:
        print(f"=====TASK_12_AM STARTED {datetime.now(CHILE_TZ)}=====")
        db: Session = SessionLocal()

        current_time = datetime.now(CHILE_TZ)
        yesterday = (datetime.now(CHILE_TZ) - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        
        cases_in_range = db.query(Case).options(
            joinedload(Case.shop_without_participation),
            joinedload(Case.contact),
            joinedload(Case.car),
            ).filter(Case.state_id == 1, # Estado "INUOTATION"
                     Case.end_term <= current_time, # Casos cuyo end_term ya venció
                     Case.created_at >= yesterday, # Casos enviados desde ayer
                     Case.is_deleted == False).all()

        if cases_in_range is not None:
            all_shop_users = get_all_users_by_role_id(3, db, only_email=False)
            all_operations_users = get_all_users_by_role_id(2, db, only_email=False)
            
            for case in cases_in_range:
                client_data = get_user_by_id(case.user_id, db)
                quotes = get_all_quotes_by_case_id(case.id, db)
                shop_without_participation = case.shop_without_participation
                shop_for_send_notification = cases_in_range

                #update case state
                db.query(Case).filter(Case.id == case.id).update({"state_id": 8}) #DEADLINE_EXPIRED
                db.commit()
                db.flush(Case)

                if shop_without_participation is not None:
                    shop_for_send_notification = [
                        u for u in all_shop_users if not any(shop.user_id == u.id for shop in shop_without_participation)
                    ]

                if quotes is not None:
                    shop_for_send_notification = [
                        u for u in all_shop_users if not any(quote.user_id == u.id for quote in quotes)
                    ]
                
                #send email/notification all shops.
                emails = [u.email for u in shop_for_send_notification]
                await send_email(
                    recipients=emails,
                    subject=f'El tiempo para agregar la cotización para el caso N° {case.id} ha expirado',
                    template_file_path="templates/deadlineExpired.html",
                    context={"url_client": f'{config.CLIENT_DOMAIN}/talleres/casos/{case.id}', "current_case_id": case.id},
                )

                for user in shop_for_send_notification:
                    notification_data = {
                        "user_id": user.id,
                        "type_id": 13, #NOTIFY_DEADLINE_EXPIRED
                        "case_id": case.id,
                        "message": TEXTS_MESSAGES_NOTIFICATIONS[13],
                    }
                    await create_notification(notification=notification_data, keyWs="UPDATE_NOTIFICATIONS_WORKSHOPS", db=db, request=None)

                #send email/notification all operations.
                emails = [u.email for u in all_operations_users]
                await send_email(
                    recipients=emails,
                    subject=f'El tiempo para agregar la cotización para el caso N° {case.id} ha expirado',
                    template_file_path="templates/deadlineExpired.html",
                    context={"url_client": f'{config.CLIENT_DOMAIN}/operaciones/casos/{case.id}', "current_case_id": case.id},
                )

                notification_data = {
                    "role_id": 2, #OPERATIONS
                    "type_id": 13, #NOTIFY_DEADLINE_EXPIRED
                    "case_id": case.id,
                    "message": TEXTS_MESSAGES_NOTIFICATIONS[13],
                }
                await create_notification(notification=notification_data, keyWs="UPDATE_NOTIFICATIONS_OPERATIONS", db=db, request=None)

                #send email/notification to clients.
                emails = [client_data.email]

                data_email_client = {
                    "client_name": f'{client_data.name} {client_data.last_name}',
                    "client_rut": client_data.rut,
                    "patent": case.car.patent,
                    "case_id": case.id,
                }

                context_email ={
                    "url_client": f'{config.CLIENT_DOMAIN}/clientes/casos?caseId={case.id}',
                    "current_case_id": case.id,
                    "contact_url": config.CONTACT_URL,
                    "data": data_email_client,
                }

                await send_email(
                    recipients=emails,
                    subject=f'¡Tu caso está listo para que puedas decidir!',
                    template_file_path="templates/deadlineExpiredClient.html",
                    context=context_email,
                )

                notification_data = {
                    "user_id": client_data.id,
                    "type_id": 13, #NOTIFY_DEADLINE_EXPIRED
                    "case_id": case.id,
                    "message": TEXTS_MESSAGES_NOTIFICATIONS[13],
                }
                await create_notification(notification=notification_data, keyWs="UPDATE_NOTIFICATIONS_CLIENT", db=db, request=None)

                print(f'===case n {case.id} expired, send notification to client, workshops and operations and change state to DEADLINE_EXPIRED===')

            print(f"=====TASK_12_AM FINISHED {datetime.now(CHILE_TZ)}=====")
            
    except Exception as err:
        print('=====ERROR IN TASK_12_AM=====')
        print(f"Error in line: {sys.exc_info()[-1].tb_lineno}")
        print(f"Error message: {err}")