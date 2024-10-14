import sys
from fastapi import HTTPException, Depends
from fastapi.param_functions import Depends
from sqlalchemy.orm.session import Session
from app.database.main import get_database

from ..model import ImageCase

def get_images_by_id(case_id: int, db: Session = Depends(get_database)):
    try:
        # Realizar la consulta para obtener todas las imágenes asociadas al caso
        found_images = db.query(ImageCase).filter(ImageCase.case_id == case_id,ImageCase.is_deleted == False).all()

        # Retornar la lista de imágenes, puede ser vacía si no hay resultados
        return found_images
        
    except Exception as err:
        # Imprimir información de error para depuración
        print(f"Error in line: {sys.exc_info()[-1].tb_lineno}")
        print(f"Error message: {err}")
        # Lanzar una excepción HTTP con un mensaje de error
        raise HTTPException(status_code=400, detail='Error al obtener las imágenes')