
import sys
from fastapi import HTTPException, Depends
from sqlalchemy.orm.session import Session
from app.database.main import get_database
from ..model import Commune


def get_commune_by_id(commune_id, db: Session = Depends(get_database)):
    try:
        find = db.query(Commune).filter(Commune.id == commune_id, Commune.is_deleted == False).first()
        return find

    except Exception as err:
        print(f"Error in line: {sys.exc_info()[-1].tb_lineno}")
        print(f"Error message: {err}")
        raise HTTPException(status_code=400, detail='Error al obtener la cotización')
