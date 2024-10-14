import sys
from fastapi import APIRouter, HTTPException, Depends
from typing import List
from sqlalchemy.orm.session import Session
from app.database.main import get_database

from ..cases.model import NoParticipationMotive
from .schema import MotiveItem

from ...middlewares.verify_token import verify_token

router = APIRouter(prefix="/no-participation-motives", tags=["No participation motives"])

@router.get("/get-all-motives", response_model=List[MotiveItem], dependencies=[Depends(verify_token)])
def get_all_motives(db: Session = Depends(get_database)):
    try:
        motives = db.query(NoParticipationMotive).filter(NoParticipationMotive.is_deleted == False).order_by(NoParticipationMotive.id).all()
        return motives
    
    except Exception as err:
        print("Error in line:", sys.exc_info()[-1].tb_lineno)
        print("Error message : {0}".format(err))
        raise HTTPException(400, 'Error al obtener las marcas')
