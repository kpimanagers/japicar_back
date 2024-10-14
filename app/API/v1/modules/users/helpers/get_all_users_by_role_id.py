
import sys
from fastapi import Depends
from sqlalchemy.orm.session import Session
from app.database.main import get_database
from ..model import User


def get_all_users_by_role_id(role_id, db: Session = Depends(get_database), only_email=False):
    try:
        find_users = db.query(User).filter(User.role_id == role_id, User.is_deleted == False).all()

        if only_email and find_users is not None:
            find_users = [user.email for user in find_users]


        return find_users if find_users is not None else None

    except Exception as err:
        print(f"Error in line: {sys.exc_info()[-1].tb_lineno}")
        print(f"Error message: {err}")
