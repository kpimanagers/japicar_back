import sys

from fastapi import HTTPException, Depends, Request
from sqlalchemy.orm.session import Session
from app.database.main import get_database
from ..model import Notification

from ......config.socket_config import ws_manager, WebSocketData, Data

async def create_notification(notification, keyWs: str, request: Request, db: Session = Depends(get_database)):
    try:
        current_user_id = request.user_id_auth if request is not None else None
        if current_user_id is None:
            notification['triggered_by_user_id'] = current_user_id
        db.add(Notification(**notification))
        db.commit()
        db.flush(Notification)
        

        web_socket_data = WebSocketData(key=keyWs, data=Data(userId=current_user_id))

        await ws_manager.broadcast_message(web_socket_data)

    except Exception as err:
        print(f"Error in line: {sys.exc_info()[-1].tb_lineno}")
        print(f"Error message: {err}")
        



