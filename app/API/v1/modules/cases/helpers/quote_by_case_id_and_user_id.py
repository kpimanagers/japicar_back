
import sys
from fastapi import HTTPException, Depends
from sqlalchemy.orm.session import Session
from app.database.main import get_database
from ..model import QuoteCase, QuoteItemCase


def get_quotes_items_by_quote_id(quote_id, db: Session = Depends(get_database)):
    try:
        found_quotes = db.query(QuoteItemCase).filter(QuoteItemCase.quote_case_id == quote_id, QuoteItemCase.is_deleted == False).all()
        
        return found_quotes
    except Exception as err:
        print(f"Error in line: {sys.exc_info()[-1].tb_lineno}")
        print(f"Error message: {err}")
        raise HTTPException(status_code=400, detail='Error al obtener la cotización')
    
def get_net_price_all_quotes_items_by_quote_id(quote_id, db: Session = Depends(get_database)):
    try:
        labor_price_sum = 0
        spare_parts_price_sum = 0
        found_quotes = db.query(QuoteItemCase).filter(QuoteItemCase.quote_case_id == quote_id, QuoteItemCase.is_deleted == False).all()

        if found_quotes is not None:
            
            for quote_item in found_quotes:
                labor_price_sum += quote_item.labor_price
                spare_parts_price_sum += quote_item.spare_parts_price
            
        net_price = labor_price_sum + spare_parts_price_sum
        formatted_price = format(net_price, ",")
        return formatted_price
    except Exception as err:
        print(f"Error in line: {sys.exc_info()[-1].tb_lineno}")
        print(f"Error message: {err}")
        raise HTTPException(status_code=400, detail='Error al obtener la cotización')
    
def get_gross_price_all_quotes_items_by_quote_id(quote_id, db: Session = Depends(get_database)):
    try:
        labor_price_sum = 0
        spare_parts_price_sum = 0
        found_quotes = db.query(QuoteItemCase).filter(QuoteItemCase.quote_case_id == quote_id, QuoteItemCase.is_deleted == False).all()

        if found_quotes is not None:
            
            for quote_item in found_quotes:
                labor_price_sum += quote_item.labor_price
                spare_parts_price_sum += quote_item.spare_parts_price
            
        net_price = labor_price_sum + spare_parts_price_sum
        gross_price = net_price * (1 + 0.19)
        formatted_price = format(gross_price, ",")
        return formatted_price
    except Exception as err:
        print(f"Error in line: {sys.exc_info()[-1].tb_lineno}")
        print(f"Error message: {err}")
        raise HTTPException(status_code=400, detail='Error al obtener la cotización')

def get_quote_by_case_id_and_user_id(case_id, user_id, db: Session = Depends(get_database)):
    try:
        found_quote = db.query(QuoteCase).filter(QuoteCase.case_id == case_id, QuoteCase.user_id == user_id, QuoteCase.is_deleted == False).first()
        
        if found_quote is not None:
            found_quote.quote_items = get_quotes_items_by_quote_id(found_quote.id, db)
       
        
        return found_quote
    except Exception as err:
        print(f"Error in line: {sys.exc_info()[-1].tb_lineno}")
        print(f"Error message: {err}")
        raise HTTPException(status_code=400, detail='Error al obtener la cotización')
    

def get_quote_approved_by_case( case_id, db: Session = Depends(get_database)):
    try:
        found_quote = db.query(QuoteCase).filter(QuoteCase.case_id == case_id, QuoteCase.status_id == 2, QuoteCase.is_deleted == False).first() #APPROVED

        if found_quote is not None:
            found_quote.quote_items = get_quotes_items_by_quote_id(found_quote.id, db)
       
        return found_quote
    except Exception as err:
        print(f"Error in line: {sys.exc_info()[-1].tb_lineno}")
        print(f"Error message: {err}")
        raise HTTPException(status_code=400, detail='Error al obtener la cotización')

def get_all_quotes_by_case_id(case_id, db: Session = Depends(get_database)):
    try:
        found_quotes = db.query(QuoteCase).filter(QuoteCase.case_id == case_id, QuoteCase.is_deleted == False).all()
        
        for quote in found_quotes:
            quote.quote_items = get_quotes_items_by_quote_id(quote.id, db)
            
        
        return found_quotes
    except Exception as err:
        print(f"Error in line: {sys.exc_info()[-1].tb_lineno}")
        print(f"Error message: {err}")
        raise HTTPException(status_code=400, detail='Error al obtener las cotizaciones')
    

def get_quote_by_id(quote_id, db: Session = Depends(get_database)):
    try:
        found_quote = db.query(QuoteCase).filter(QuoteCase.id == quote_id, QuoteCase.is_deleted == False).first()
        
        if found_quote is not None:
            found_quote.quote_items = get_quotes_items_by_quote_id(quote_id, db)
       
        
        return found_quote
    except Exception as err:
        print(f"Error in line: {sys.exc_info()[-1].tb_lineno}")
        print(f"Error message: {err}")
        raise HTTPException(status_code=400, detail='Error al obtener la cotización')