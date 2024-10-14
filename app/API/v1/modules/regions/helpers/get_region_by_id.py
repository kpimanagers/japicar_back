
import sys
from fastapi import HTTPException, Depends
from sqlalchemy.orm.session import Session
from app.database.main import get_database
from ..model import Region


def get_region_by_id(region_id, db: Session = Depends(get_database)):
    try:
        find_region = db.query(Region).filter(Region.id == region_id, Region.is_deleted == False).first()
        return find_region

    except Exception as err:
        print(f"Error in line: {sys.exc_info()[-1].tb_lineno}")
        print(f"Error message: {err}")
        raise HTTPException(status_code=400, detail='Error al obtener la cotización')
