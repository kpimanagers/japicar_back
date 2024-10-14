import sys
from fastapi import APIRouter, HTTPException, Depends, Query, Request
from sqlalchemy import or_
from fastapi_pagination import paginate, Params, Page
from sqlalchemy.orm.session import Session
from app.database.main import get_database


from .model import Notification, SeenBy
from .schema import NotificationItem, ToReadNotification
from ...middlewares.verify_token import verify_token

router = APIRouter(prefix="/notifications", tags=["Notifications"])

@router.get("/get-all-notifications-by-role", response_model=Page[NotificationItem], dependencies=[Depends(verify_token)])
def get_all_notifications_by_role(request: Request,
                                  role_id: int = Query(None, alias="roleId"),
                                  pag_params: Params = Depends(),
                                  db: Session = Depends(get_database)):
    try:
        user_id_auth = int(request.user_id_auth)
        query = db.query(Notification).filter(
            or_(
                Notification.role_id == role_id,
                Notification.user_id == user_id_auth
            ),
            Notification.is_deleted == False
        )
        query = query.order_by(Notification.created_at.desc())
        notifications = query.all()

        notifications_paginated = paginate(notifications, params=pag_params)
        
        for notification in notifications_paginated.items:
            seen_by_list = notification.seen_by

            if any(seen_by.user_id == user_id_auth for seen_by in seen_by_list):
                notification.is_read = True
            else:
                notification.is_read = False

        return notifications_paginated

    
    except Exception as err:
        print("Error in line:", sys.exc_info()[-1].tb_lineno)
        print("Error message : {0}".format(err))
        raise HTTPException(400, 'Error al obtener las marcas')
    
@router.post("/to-read-notification", dependencies=[Depends(verify_token)])
def to_read_notification(body: ToReadNotification, request: Request, db: Session = Depends(get_database)):
    try:
        user_id_auth = request.user_id_auth
        find_notification = db.query(Notification).filter(Notification.id == body.id, Notification.is_deleted == False).first()
        if find_notification is not None:
            
            if not any(seen_by.user_id == user_id_auth for seen_by in find_notification.seen_by):
                seen_by_data = {'user_id': user_id_auth, 'notification_id': find_notification.id}
                new_seen_by = SeenBy(**seen_by_data)
                db.add(new_seen_by)
                db.commit()
                db.flush(Notification)

            return HTTPException(200, 'Notificación leída exitosamente')
        else:
            return HTTPException(404, 'No se encontró la notificación')
    except Exception as err:
        print("Error in line:", sys.exc_info()[-1].tb_lineno)
        print("Error message : {0}".format(err))
        raise HTTPException(400, 'Error al leer la notificación')
    
