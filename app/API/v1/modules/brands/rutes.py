import sys
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from sqlalchemy.orm.session import Session
from app.database.main import get_database

from .model import Brand, Model
from .schema import BrandItem, ModelItem

from ...middlewares.verify_token import verify_token

router = APIRouter(prefix="/brands", tags=["Brands"])

@router.get("/get-all-brands", response_model=List[BrandItem], dependencies=[Depends(verify_token)])
def get_all_brands(db: Session = Depends(get_database)):
    try:
        brands = db.query(Brand).filter(Brand.is_deleted == False).order_by(Brand.name).all()
        return brands
    
    except Exception as err:
        print("Error in line:", sys.exc_info()[-1].tb_lineno)
        print("Error message : {0}".format(err))
        raise HTTPException(400, 'Error al obtener las marcas')
    

@router.get("/get-one-brand-by-id/{brand_id}", response_model=BrandItem, dependencies=[Depends(verify_token)])
def get_one_brand_by_id(brand_id: int, db: Session = Depends(get_database)):
    try:
        brand = db.query(Brand).filter(Brand.id == brand_id, Brand.is_deleted == False).first()
        return brand
    except Exception as err:
        print("Error in line:", sys.exc_info()[-1].tb_lineno)
        print("Error message : {0}".format(err))
        raise HTTPException(400, 'Error al obtener la marca')
    

@router.get("/get-all-models-by-brand", response_model=List[ModelItem], dependencies=[Depends(verify_token)])
def get_all_models_by_brand(brand_id: Optional[int] = Query(None, alias="brandId"), db: Session = Depends(get_database)):
    try:
        if brand_id is None:
            return []
        
        models = db.query(Model).filter(Model.brand_id == brand_id, Model.is_deleted == False).order_by(Model.name).all()
        return models
    
    except Exception as err:
        print("Error in line:", sys.exc_info()[-1].tb_lineno)
        print("Error message : {0}".format(err))
        raise HTTPException(400, 'Error al obtener los modelos de la marca')
    
@router.get("/get-one-model-by-id/{model_id}", response_model=ModelItem, dependencies=[Depends(verify_token)])
def get_one_model_by_id(model_id: int, db: Session = Depends(get_database)):
    try:
        model = db.query(Model).filter(Model.id == model_id, Model.is_deleted == False).first()
        return model
    except Exception as err:
        print("Error in line:", sys.exc_info()[-1].tb_lineno)
        print("Error message : {0}".format(err))
        raise HTTPException(400, 'Error al obtener el modelo')