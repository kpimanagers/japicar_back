
import sys
from fastapi import Depends
from sqlalchemy.orm.session import Session
from app.database.main import get_database
from ..model import User


def get_user_by_id(id, db: Session = Depends(get_database)):
    try:
        find_user = db.query(User).filter(User.id == id, User.is_deleted == False).first()

        return find_user if find_user else None

    except Exception as err:
        print(f"Error in line: {sys.exc_info()[-1].tb_lineno}")
        print(f"Error message: {err}")
