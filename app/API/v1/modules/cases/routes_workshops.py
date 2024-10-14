import sys
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, Request, Query
from fastapi_pagination import paginate, Params, Page
from typing import Optional
from fastapi.param_functions import Depends
from sqlalchemy.orm.session import Session
from sqlalchemy.orm import joinedload
from sqlalchemy import and_
from app.database.main import get_database
from ...middlewares.verify_token import verify_token


from app.API.v1.modules.cases.schema import DeleteQuoteShopCase, QuoteDataCreate, CaseDataBase, AddQuoteFileCase, QuoteDataSendToReview, CaseBasicData, NoParticipationData
from app.API.v1.modules.cases.model import Case, ImageCase, QuoteCase, QuoteItemCase, PaymentMethodsCase, AcceptedTermsQuoteCase, QuoteShopCase, ShopsWithoutParticipationCase
from .helpers.quote_by_case_id_and_user_id import get_quote_by_case_id_and_user_id, get_gross_price_all_quotes_items_by_quote_id
from .helpers.Images_by_id import get_images_by_id
from .helpers.case_state_by_id import case_state_by_id
from ...helpers.get_current_date_chile import get_current_date
from ..users.helpers.get_user_by_id import get_user_by_id

from .....config import config
from ...services.send_mail import send_email
from ..users.helpers.get_all_users_by_role_id import get_all_users_by_role_id
from ..notifications.helpers.create_notificacion import create_notification
from ...helpers.constants.business import TEXTS_MESSAGES_NOTIFICATIONS



router = APIRouter(prefix="/cases", tags=["Cases"])

#OPERATIONS ENDPOINTS
@router.get("/workshops/get-all-payment-methods-case", dependencies=[Depends(verify_token)])
def get_all_payment_methods_case(db: Session = Depends(get_database)):
    try:
        return db.query(PaymentMethodsCase).filter(PaymentMethodsCase.is_deleted == False).all()
    except Exception as err:
        print("Error in line:", sys.exc_info()[-1].tb_lineno)
        print("Error message : {0}".format(err))
        raise HTTPException(400, 'Error al obtener el caso')




@router.get("/workshops/all-cases", dependencies=[Depends(verify_token)], response_model=Page[CaseBasicData])
def get_case_by_id_simple(
                          request: Request,
                          case_id: Optional[int] = Query(None, alias="caseId"),
                          state_id: Optional[int] = Query(None, alias="stateId"),
                          start_date: Optional[str] = Query(None, alias="startDate"),
                          end_date: Optional[str] = Query(None, alias="endDate"),
                          pag_params: Params = Depends(),
                          db: Session = Depends(get_database)):
    try:
        
        user_id_auth = request.user_id_auth

        query = db.query(Case).options(
            joinedload(Case.state),
            joinedload(Case.damage_state),
            joinedload(Case.car),
            joinedload(Case.awarded_quote_case),
            joinedload(Case.shop_without_participation),
            )

        if state_id is not None:
            query = query.filter(Case.state_id == state_id)
        else:
            query = query.filter(Case.state_id.in_([1, 5, 6, 4, 8])) #INUOTATION, PENDINGAPPROVAL, INREVIEWFORCLIENT, APPROVED, DEADLINE_EXPIRED
        
        if case_id is not None:
            query = query.filter(Case.id == case_id)
        if start_date is not None:
            try:
                start_date_obj = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                start_date_obj = start_date_obj.replace(hour=0, minute=0, second=0, microsecond=0)

                query = query.filter(Case.created_at >= start_date_obj)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid date format")
        if end_date is not None:
            try:
                end_date_obj = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                end_date_obj = end_date_obj.replace(hour=23, minute=59, second=59, microsecond=999999)
                query = query.filter(Case.created_at <= end_date_obj)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid date format")
            
        cases = query.order_by(Case.sent_operations_to_workshop_date.desc()).all()

        state_data = case_state_by_id(5, db) #INREVIEWFORCLIENT

        
        cases_paginated = paginate(cases, params=pag_params)
        
        for case in cases_paginated.items:
            current_quote = get_quote_by_case_id_and_user_id(case.id, user_id_auth, db)
            
            
            if current_quote is not None and current_quote.send_to_review_date and case.state_id == 1: #INOUVATION
                case.state_id = 5 #INREVIEWFORCLIENT
                case.state = state_data


        return cases_paginated
        
    except Exception as err:
        print("Error in line:", sys.exc_info()[-1].tb_lineno)
        print("Error message : {0}".format(err))
        raise HTTPException(400, 'Error al obtener el caso')
    

@router.get("/workshops/get-case-by-id/{case_id}", dependencies=[Depends(verify_token)], response_model=CaseDataBase)
def get_case_by_id(case_id: int, request: Request, db: Session = Depends(get_database)):
    try:
        user_id_auth = request.user_id_auth
        found_case = (
            db.query(Case)
            .outerjoin(Case.images)
            .filter(and_(Case.id == case_id, ImageCase.is_deleted == False, Case.state_id.in_([1, 2, 5, 6, 4, 8]))) #INREVIEWFORWORKER, INUOTATION, INREVIEWFORCLIENT, PENDINGAPPROVAL, APPROVED, DEADLINE_EXPIRED
            .options(
                joinedload(Case.contact),
                joinedload(Case.car),
                joinedload(Case.damage_state),
                joinedload(Case.state),
                joinedload(Case.shop_without_participation),
            )
            .first()
        )

        if found_case is not None:
            current_quote = get_quote_by_case_id_and_user_id(case_id, user_id_auth, db)
            found_case.images = get_images_by_id(case_id, db)
            found_case.quote = current_quote


            if current_quote is not None and current_quote.send_to_review_date and found_case.state_id == 1: #INOUVATION
                 found_case.state_id = 5
                 found_case.state = case_state_by_id(5, db)

            

            return found_case
        else:
            return HTTPException(404, 'No se encontró el caso')
        
    except Exception as err:
        print("Error in line:", sys.exc_info()[-1].tb_lineno)
        print("Error message : {0}".format(err))
        raise HTTPException(400, 'Error al obtener el caso')
    


@router.post("/workshops/add-quote-case", dependencies=[Depends(verify_token)])
def add_quote_case(body: QuoteDataCreate, request: Request, db: Session = Depends(get_database)):
    try:
        user_id_auth = request.user_id_auth
        current_case_id = body.case_id
        final_quote_id = None

        print(body)
        

        quote_data_base = {"description": body.description, "use_crane": body.use_crane, "use_drive": body.use_drive, "init_service_date": body.init_service_date, "end_service_date": body.end_service_date, "payment_method_id": body.payment_method_id}

        find = db.query(QuoteCase).filter(QuoteCase.case_id == current_case_id, QuoteCase.user_id == user_id_auth, QuoteCase.is_deleted == False).first()

        if find is not None:
            db.query(QuoteCase).filter(QuoteCase.case_id == current_case_id, QuoteCase.user_id == user_id_auth, QuoteCase.is_deleted == False).update(quote_data_base)
            db.commit()
            db.flush(QuoteCase)
            final_quote_id = find.id
            
            
        else:
            quote_data = {**quote_data_base, "case_id": current_case_id, "user_id": user_id_auth}
            new_quote = QuoteCase(**quote_data)
            db.add(new_quote)
            db.commit()
            db.flush(QuoteCase)
            final_quote_id = new_quote.id
            
            #add accepted terms
            accepted_terms_data = {"user_id": user_id_auth, "quote_case_id": final_quote_id}
            new_accepted_terms = AcceptedTermsQuoteCase(**accepted_terms_data)
            db.add(new_accepted_terms)
            db.commit()
            db.flush(AcceptedTermsQuoteCase)

        if final_quote_id is not None:
            #update to is_deleted to false all items
            db.query(QuoteItemCase).filter(QuoteItemCase.quote_case_id == final_quote_id).update({"is_deleted": True})
                
            #add items
            for item in body.items:
                quote_item_data = {"name": item.name, "labor_price": item.labor_price, "spare_parts_price": item.spare_parts_price, "quote_case_id": final_quote_id}
                new_item = QuoteItemCase(**quote_item_data)
                db.add(new_item)
                db.commit()
                db.flush(QuoteItemCase)


        return HTTPException(200, 'Corización creada/actualizada exitosamente')
    except Exception as err:
        print("Error in line:", sys.exc_info()[-1].tb_lineno)
        print("Error message : {0}".format(err))
        raise HTTPException(400, 'Error al obtener el caso')
    


@router.post("/workshops/add-quote-file-case", dependencies=[Depends(verify_token)])
def add_quote_file_case(body: AddQuoteFileCase, request: Request, db: Session = Depends(get_database)):
    try:
        user_id_auth = request.user_id_auth
        current_case_id = body.case_id
        

        findCase = db.query(Case).filter(Case.id == current_case_id, Case.is_deleted == False).first()

        if findCase is None:
            raise HTTPException(404, 'No se encontró el caso')

        find = db.query(QuoteCase).filter(QuoteCase.case_id == current_case_id, QuoteCase.user_id == user_id_auth, QuoteCase.is_deleted == False).first()

        #add file to QuoteShopCase
        quote_shop_data = {"url": body.url}
        new_quote_shop = QuoteShopCase(**quote_shop_data)
        db.add(new_quote_shop)
        db.commit()
        db.flush(QuoteShopCase)

        if find is not None:
            #update QuoteCase
            db.query(QuoteCase).filter(QuoteCase.case_id == current_case_id, QuoteCase.user_id == user_id_auth, QuoteCase.is_deleted == False).update({"quote_shop_id": new_quote_shop.id})
            db.commit()
            db.flush(QuoteCase)
        
        else:
            #create new QuoteCase in blank
            quote_data = {"case_id": current_case_id, "user_id": user_id_auth, "description": '', "use_crane": False, "use_drive": False, "quote_shop_id": new_quote_shop.id}
            new_quote = QuoteCase(**quote_data)
            db.add(new_quote)
            db.commit()
            db.flush(QuoteCase)

        
        return HTTPException(200, 'Corización creada/actualizada exitosamente')

    except Exception as err:
        print("Error in line:", sys.exc_info()[-1].tb_lineno)
        print("Error message : {0}".format(err))
        raise HTTPException(400, 'Error al obtener el caso')
    


@router.post("/workshops/send-quote-to-review", dependencies=[Depends(verify_token)])
async def send_quote_to_review(body: QuoteDataSendToReview, request: Request, db: Session = Depends(get_database)):
    try:
        user_id_auth = request.user_id_auth
        current_case_id = body.case_id
        
        find = db.query(Case).options(
            joinedload(Case.contact),
            joinedload(Case.car)
        ).filter(Case.id == current_case_id, Case.is_deleted == False).first()

        if find is None:
            raise HTTPException(404, 'No se encontró el caso')
        
        findQuote = db.query(QuoteCase).filter(QuoteCase.case_id == current_case_id, QuoteCase.user_id == user_id_auth, QuoteCase.is_deleted == False).first()

        if findQuote is None:
            raise HTTPException(404, 'No se encontró la corización')
        
        #update QuoteCase
        db.query(QuoteCase).filter(QuoteCase.case_id == current_case_id, QuoteCase.user_id == user_id_auth, QuoteCase.is_deleted == False).update({"send_to_review_date": get_current_date(), "status_id": 1}) #PENDING
        db.commit()
        db.flush(QuoteCase)
        
        all_emails = get_all_users_by_role_id(2, db, only_email=True) #OPERATIONS
        workshop_user_data = get_user_by_id(user_id_auth, db)
        data_email_operations = {
            "workshop_name": workshop_user_data.workshop.name,
            "client_name": f'{find.contact.name} {find.contact.last_name}',
            "patent": find.car.patent,
            "current_date": get_current_date("%d/%m/%Y"),
            "gross_price": get_gross_price_all_quotes_items_by_quote_id(findQuote.id, db),
            "case_id": current_case_id,
        }

        context = {
            "current_case_id":current_case_id,
            "url_client": f'{config.CLIENT_DOMAIN}/operaciones/casos/cotizaciones/{current_case_id}?quoteId=${findQuote.id}',
            "data": data_email_operations,
        }
        

        await send_email(
            recipients=all_emails,
            subject=f'Proceso de cotización completado para el caso Japi N° {current_case_id}',
            template_file_path="templates/addNewQuoteToCase.html",
            context=context,
            )

        notification_data = {
            "role_id": 2, #OPERATIONS
            "type_id": 5, #NOTIFY_SHOP_SUBMITTED_QUOTE
            "case_id": current_case_id,
            "quote_id": findQuote.id,
            "message": f'Se ha completado cotización para el caso Japi N° {current_case_id}. Equipo Japicar.cl',
        }
        await create_notification(notification=notification_data, keyWs="UPDATE_NOTIFICATIONS_OPERATIONS", request=request, db=db)


        #send email to workshop
        current_workshop_data = get_user_by_id(user_id_auth, db)

        data_email_workshop = {
            "workshop_name": current_workshop_data.workshop.name,
        }

        context_workshop = {
            "current_case_id":current_case_id,
            "url_client": f'{config.CLIENT_DOMAIN}/talleres/casos/detalles/{current_case_id}',
            "contact_url": config.CONTACT_URL,
            "data": data_email_workshop
        }

        await send_email(
            recipients=[current_workshop_data.email],
            subject=f'Cotización recibida para el caso {current_case_id} en Japicar.cl',
            template_file_path="templates/addNewQuoteToCaseWorkshop.html",
            context=context_workshop,
            )
        
        notification_data = {
            "type_id": 14, #NOTIFY_SHOP_SUBMITTED_QUOTE_RESPONSE
            "case_id": current_case_id,
            "quote_id": findQuote.id,
            "user_id": current_workshop_data.id,
            "message": f'Gracias por tu cotización al caso Japi N° {current_case_id}.  Te mantendremos informados. Equipo JapiCar.cl'
        }
        await create_notification(notification=notification_data, keyWs="UPDATE_NOTIFICATIONS_WORKSHOPS", request=request, db=db)
            
        return HTTPException(200, 'Corización enviada a revisión exitosamente')
    except Exception as err:
        print("Error in line:", sys.exc_info()[-1].tb_lineno)
        print("Error message : {0}".format(err))
        return HTTPException(400, 'Error al enviar el caso a revisión por el trabajador')
    

@router.post("/workshops/add-not-participation-in-case", dependencies=[Depends(verify_token)])
async def add_not_participation_in_case(body: NoParticipationData, request: Request, db: Session = Depends(get_database)):

    try:
        user_id_auth = request.user_id_auth
        case_id = body.case_id
        motive_id = body.motive_id

        find = db.query(ShopsWithoutParticipationCase).filter(ShopsWithoutParticipationCase.user_id == user_id_auth, ShopsWithoutParticipationCase.case_id == case_id, ShopsWithoutParticipationCase.is_deleted == False).first()

        if find is not None:
            return HTTPException(400, 'Ya se ha agregado la no participación')

        format_data = {"user_id": user_id_auth, "case_id": case_id, "motive_id": motive_id}
        new_no_participation = ShopsWithoutParticipationCase(**format_data)
        db.add(new_no_participation)
        db.commit()
        db.flush(ShopsWithoutParticipationCase)

        return HTTPException(200, 'No participación agregada exitosamente')
    except Exception as err:
        print("Error in line:", sys.exc_info()[-1].tb_lineno)
        print("Error message : {0}".format(err))
        raise HTTPException(400, 'Error al obtener el caso')
    

@router.post("/workshops/delete-quote-shop-case", dependencies=[Depends(verify_token)])
async def delete_quote_shop_case(body: DeleteQuoteShopCase, request: Request, db: Session = Depends(get_database)):
    try:
        find = db.query(QuoteCase).filter(QuoteCase.id == body.quote_id, QuoteCase.is_deleted == False).first()

        if find is None:
            raise HTTPException(404, 'No se encontró la corización')
        
        find.quote_shop_id = None
        db.commit()
        db.flush(QuoteCase)

        return HTTPException(200, 'Corización borrada exitosamente')

    except Exception as err:
        print("Error in line:", sys.exc_info()[-1].tb_lineno)
        print("Error message : {0}".format(err))
        raise HTTPException(400, 'Error al borrar la corización')