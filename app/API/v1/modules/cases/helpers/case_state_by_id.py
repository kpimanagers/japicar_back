
import sys
from fastapi import HTTPException, Depends
from sqlalchemy.orm.session import Session
from app.database.main import get_database
from ..model import StateCase


def case_state_by_id(state_id, db: Session = Depends(get_database), is_dict=False):
    try:
        found_state = db.query(StateCase).filter(StateCase.id == state_id, StateCase.is_deleted == False).first()

        if found_state is not None and is_dict:
            found_state = {
                "id": found_state.id,
                "name": found_state.name,
                "is_deleted": found_state.is_deleted,
                "created_at": found_state.created_at,
                "update_at": found_state.update_at
            }
            return found_state


        return found_state
    except Exception as err:
        print(f"Error in line: {sys.exc_info()[-1].tb_lineno}")
        print(f"Error message: {err}")
        raise HTTPException(status_code=400, detail='Error al obtener la cotización')


    try:
        found_quotes = db.query(QuoteCase).filter(QuoteCase.case_id == case_id, QuoteCase.is_deleted == False).all()
        
        for quote in found_quotes:
            quote.quote_items = get_quotes_items_by_quote_id(quote.id, db)
            
        
        return found_quotes
    except Exception as err:
        print(f"Error in line: {sys.exc_info()[-1].tb_lineno}")
        print(f"Error message: {err}")
        raise HTTPException(status_code=400, detail='Error al obtener las cotizaciones')