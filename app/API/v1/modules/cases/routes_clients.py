import sys
from fastapi import APIRouter, HTTPException, Depends, Request, Query
from typing import Optional, List
from fastapi_pagination import paginate, Params, Page
from fastapi.param_functions import Depends
from sqlalchemy.orm.session import Session
from sqlalchemy.orm import joinedload
from app.database.main import get_database
from ...middlewares.verify_token import verify_token


from .helpers.Images_by_id import get_images_by_id
from app.API.v1.modules.cases.schema import CaseBasicData, ContactDataBase, ContactDataPartial, CarDataBase, CarDataPartial, CaseDataBase, DamageDataBase, ImageDataBase, SendToReviewForWorker, QuoteCaseItem, ApproveQuoteClient
from app.API.v1.modules.cases.model import Case, ContactCase, CarCase, ImageCase, QuoteCase, AwardedQuoteCase
from app.API.v1.modules.users.model import User

from .....config import config
from ...services.send_mail import send_email
from .helpers.quote_by_case_id_and_user_id import get_quotes_items_by_quote_id, get_quote_by_id, get_net_price_all_quotes_items_by_quote_id, get_gross_price_all_quotes_items_by_quote_id
from ...helpers.get_current_date_chile import get_current_date

from ..regions.helpers.get_region_by_id import get_region_by_id
from ..regions.helpers.get_commune_by_id import get_commune_by_id
from ..users.helpers.get_all_users_by_role_id import get_all_users_by_role_id
from ..users.helpers.get_user_by_id import get_user_by_id
from ..notifications.helpers.create_notificacion import create_notification
from ...helpers.constants.business import TEXTS_MESSAGES_NOTIFICATIONS


router = APIRouter(prefix="/cases", tags=["Cases"])


#CLIENT ENDPOINTS
@router.get("/get-case-by-id-simple", dependencies=[Depends(verify_token)], response_model=Page[CaseBasicData])
def get_case_by_id_simple(
                          request: Request,
                          case_id: Optional[str] = Query(None, alias="caseId"),
                          state_id: Optional[int] = Query(None, alias="stateId"),
                          pag_params: Params = Depends(),
                          db: Session = Depends(get_database)):
    try:
        
        user_id_auth = request.user_id_auth
        query = db.query(Case).options(joinedload(Case.state), joinedload(Case.awarded_quote_case)).filter(Case.user_id == user_id_auth, Case.is_deleted == False)

        if state_id is not None:
            query = query.filter(Case.state_id == state_id)

        if case_id is not None:
            if case_id.isdigit():
                
                query = query.filter(Case.id == int(case_id))
            else:
                
                query = query.join(CarCase).filter(CarCase.patent.startswith(case_id))

        
        query = query.order_by(Case.created_at.desc())
        
        cases = query.all()
        
        return paginate(cases, params=pag_params)
        
    except Exception as err:
        print("Error in line:", sys.exc_info()[-1].tb_lineno)
        print("Error message : {0}".format(err))
        raise HTTPException(400, 'Error al obtener el caso')



@router.get("/get-case-by-id/{case_id}", dependencies=[Depends(verify_token)], response_model=CaseDataBase)
def get_case_by_id(case_id: int, db: Session = Depends(get_database)):
    try:
        found_case = db.query(Case).options(
        joinedload(Case.contact),
        joinedload(Case.car),
        joinedload(Case.damage_state),
        joinedload(Case.state),
        ).filter(Case.id == case_id).filter(Case.is_deleted == False).first()

        if found_case is not None:
            current_awarded_quote = db.query(AwardedQuoteCase).filter(AwardedQuoteCase.case_id == found_case.id, AwardedQuoteCase.is_deleted == False).first()
            found_case.quote = get_quote_by_id(current_awarded_quote.quote_id, db) if current_awarded_quote is not None else None
            found_case.images = get_images_by_id(case_id, db)
            return found_case
        else:
            return HTTPException(404, 'No se encontró el caso')
        
    except Exception as err:
        print("Error in line:", sys.exc_info()[-1].tb_lineno)
        print("Error message : {0}".format(err))
        raise HTTPException(400, 'Error al obtener el caso')

@router.post("/create-from-contact", dependencies=[Depends(verify_token)])
def add_contact_data(body: ContactDataBase, request: Request, db: Session = Depends(get_database)):
    try:
        print("body============>", body)
        user_id_auth = request.user_id_auth
        current_case_id = body.case_id
        contact_data = {"name": body.name, "last_name": body.last_name, "rut": body.rut, "email": body.email, "phone": body.phone, "region_id": body.region_id, "commune_id": body.commune_id}

        if current_case_id is not None:
            found_case = db.query(Case).filter(Case.id == current_case_id).first()

            if found_case is not None:
                found_contact_case = db.query(ContactCase).filter(ContactCase.id == found_case.contact_id).first()
                final_car_id = None

                if found_contact_case is not None:
                    # update car data
                    db.query(ContactCase).filter(ContactCase.id == found_case.contact_id).update(contact_data)
                    db.commit()
                    db.flush(CarCase)
                    final_car_id = found_contact_case.id
                else:
                    # add car data
                    new_contact = ContactCase(**contact_data)
                    db.add(new_contact)
                    db.commit()
                    db.flush(ContactCase)
                    final_car_id = new_contact.id

                db.query(Case).filter(Case.id == found_case.id).update({"contact_id": final_car_id})
                db.commit()
                db.flush(Case)
                
                contact_data['caseId'] = found_case.id
                return HTTPException(200, contact_data)
            
        else:
            # add contact data
            new_contact = ContactCase(**contact_data)
            db.add(new_contact)
            db.commit()
            db.flush(ContactCase)

            # create case with car 
            case_data = {"user_id": user_id_auth, "contact_id": new_contact.id}
            new_case_empty = Case(**case_data)
            db.add(new_case_empty)
            db.commit()
            db.flush(Case)

            contact_data['caseId'] = new_case_empty.id
            return HTTPException(200, contact_data)
        
        

    except Exception as err:
        print("Error in line:", sys.exc_info()[-1].tb_lineno)
        print("Error message : {0}".format(err))
        raise HTTPException(400, 'Error al agregar el contacto')
    

@router.post("/create-from-contact-partial", dependencies=[Depends(verify_token)])
def add_contact_data(body: ContactDataPartial, request: Request, db: Session = Depends(get_database)):
    try:
        print("body============>", body)
        user_id_auth = request.user_id_auth
        current_case_id = body.case_id
        print("current_case_id============>", current_case_id)
        valid_region_id = None if body.region_id == '' else body.region_id
        valid_commune_id = None if body.commune_id == '' else body.commune_id
        contact_data = {"name": body.name, "last_name": body.last_name, "rut": body.rut, "email": body.email, "phone": body.phone, "region_id": valid_region_id, "commune_id": valid_commune_id}

        if current_case_id is not None:
            found_case = db.query(Case).filter(Case.id == current_case_id).first()

            if found_case is not None:
                found_contact_case = db.query(ContactCase).filter(ContactCase.id == found_case.contact_id).first()
                final_contact_id = None

                if found_contact_case is not None:
                    # update car data
                    db.query(ContactCase).filter(ContactCase.id == found_case.contact_id).update(contact_data)
                    db.commit()
                    db.flush(CarCase)
                    final_contact_id = found_contact_case.id
                else:
                    # add car data
                    new_contact = ContactCase(**contact_data)
                    db.add(new_contact)
                    db.commit()
                    db.flush(ContactCase)
                    final_contact_id = new_contact.id

                db.query(Case).filter(Case.id == found_case.id).update({"contact_id": final_contact_id})
                db.commit()
                db.flush(Case)
                
                contact_data['caseId'] = found_case.id
                return HTTPException(200, contact_data)
            
        else:
            # add contact data
            new_contact = ContactCase(**contact_data)
            db.add(new_contact)
            db.commit()
            db.flush(ContactCase)

            # create case with car 
            case_data = {"user_id": user_id_auth, "contact_id": new_contact.id}
            new_case_empty = Case(**case_data)
            db.add(new_case_empty)
            db.commit()
            db.flush(Case)

            contact_data['caseId'] = new_case_empty.id
            return HTTPException(200, contact_data)
        
        

    except Exception as err:
        print("Error in line:", sys.exc_info()[-1].tb_lineno)
        print("Error message : {0}".format(err))
        raise HTTPException(400, 'Error al agregar el contacto')
    


@router.post("/create-from-car", dependencies=[Depends(verify_token)])
def add_car_data(body: CarDataBase, request: Request, db: Session = Depends(get_database)):
    try:
        
        user_id_auth = request.user_id_auth
        current_case_id = body.case_id
        car_data = {"patent": body.patent, "brand_id": body.brand_id, "model_id": body.model_id, "year": body.year, "vin": body.vin}
        
        
        if current_case_id is not None:
            
            found_case = db.query(Case).filter(Case.id == current_case_id).first()

            if found_case is not None:
                found_car_case = db.query(CarCase).filter(CarCase.id == found_case.car_id).first()
                final_car_id = None

                if found_car_case is not None:
                    # update car data
                    db.query(CarCase).filter(CarCase.id == found_case.car_id).update(car_data)
                    db.commit()
                    db.flush(CarCase)
                    final_car_id = found_car_case.id
                else:
                    # add car data
                    new_car = CarCase(**car_data)
                    db.add(new_car)
                    db.commit()
                    db.flush(CarCase)
                    final_car_id = new_car.id
                
                db.query(Case).filter(Case.id == found_case.id).update({"car_id": final_car_id})
                db.commit()
                db.flush(Case)

                car_data['caseId'] = found_case.id
                return HTTPException(200, car_data)
            
        else:
            # add car data
            new_car = CarCase(**car_data)
            db.add(new_car)
            db.commit()
            db.flush(CarCase)

            # create case with car 
            case_data = {"user_id": user_id_auth, "car_id": new_car.id}
            new_case_empty = Case(**case_data)
            db.add(new_case_empty)
            db.commit()
            db.flush(Case)

            

            car_data['caseId'] = new_case_empty.id
            return HTTPException(200, car_data)
        
        

    except Exception as err:
        print("Error in line:", sys.exc_info()[-1].tb_lineno)
        print("Error message : {0}".format(err))
        raise HTTPException(400, 'Error al agregar el automóvil')


@router.post("/create-from-car-partial", dependencies=[Depends(verify_token)])
def add_car_data(body: CarDataPartial, request: Request, db: Session = Depends(get_database)):
    try:
        print("body============>", body)
        user_id_auth = request.user_id_auth
        current_case_id = body.case_id
        valid_brand_id = None if body.brand_id == '' else body.brand_id
        valid_model_id = None if body.model_id == '' else body.model_id
        valid_year = None if body.year == '' else int(body.year)
        car_data = {"patent": body.patent, "brand_id": valid_brand_id, "model_id": valid_model_id, "year": valid_year, "vin": body.vin}
        
        
        if current_case_id is not None:
            
            found_case = db.query(Case).filter(Case.id == current_case_id).first()

            if found_case is not None:
                found_car_case = db.query(CarCase).filter(CarCase.id == found_case.car_id).first()
                final_car_id = None

                if found_car_case is not None:
                    # update car data
                    db.query(CarCase).filter(CarCase.id == found_case.car_id).update(car_data)
                    db.commit()
                    db.flush(CarCase)
                    final_car_id = found_car_case.id
                else:
                    # add car data
                    new_car = CarCase(**car_data)
                    db.add(new_car)
                    db.commit()
                    db.flush(CarCase)
                    final_car_id = new_car.id
                
                db.query(Case).filter(Case.id == found_case.id).update({"car_id": final_car_id})
                db.commit()
                db.flush(Case)

                car_data['caseId'] = found_case.id
                return HTTPException(200, car_data)
            
        else:
            # add car data
            new_car = CarCase(**car_data)
            db.add(new_car)
            db.commit()
            db.flush(CarCase)

            # create case with car 
            case_data = {"user_id": user_id_auth, "car_id": new_car.id}
            new_case_empty = Case(**case_data)
            db.add(new_case_empty)
            db.commit()
            db.flush(Case)

            

            car_data['caseId'] = new_case_empty.id
            return HTTPException(200, car_data)
        
        

    except Exception as err:
        print("Error in line:", sys.exc_info()[-1].tb_lineno)
        print("Error message : {0}".format(err))
        raise HTTPException(400, 'Error al agregar el automóvil')
    

@router.post("/create-from-damage", dependencies=[Depends(verify_token)])
def add_car_data(body: DamageDataBase, request: Request, db: Session = Depends(get_database)):
    try:
        print("body============>", body)
        user_id_auth = request.user_id_auth
        current_case_id = body.case_id
        damage_data = {"description_damage": body.description_damage, "user_id": user_id_auth}
        
        if current_case_id is not None:
            db.query(Case).filter(Case.id == current_case_id).update(damage_data)
            db.commit()
            db.flush(Case)

            response = body.__dict__
            response['caseId'] = current_case_id
            return HTTPException(200, response)
            
        else:
            # add damage data
            new_case = Case(**damage_data)
            db.add(new_case)
            db.commit()
            db.flush(Case)

            response = body.__dict__
            response['caseId'] = new_case.id
            return HTTPException(200, response)
        
        

    except Exception as err:
        print("Error in line:", sys.exc_info()[-1].tb_lineno)
        print("Error message : {0}".format(err))
        raise HTTPException(400, 'Error al agregar el daño visible')
    

@router.post("/create-from-images", dependencies=[Depends(verify_token)])
async def add_list_images(body: ImageDataBase, request: Request, db: Session = Depends(get_database)):

    try:
        user_id_auth = request.user_id_auth
        current_case_id = body.case_id
        results = []
        print('user_id_auth===', user_id_auth)
        if current_case_id is not None:

            #update all current images in db
            db.query(ImageCase).filter(ImageCase.case_id == current_case_id).update({"is_deleted": True})

            for url in body.urls:
                img_data = {"case_id": current_case_id, "url": url}
                new_image = ImageCase(**img_data)
                db.add(new_image)
                db.commit()
                db.flush(ImageCase)
                results.append(new_image)
            
            response = {'caseId': current_case_id, 'images': results}
            return HTTPException(200, response)
        
        else:
            # create case empty
            case_data = {"user_id": user_id_auth}
            new_case = Case(**case_data)
            db.add(new_case)
            db.commit()
            db.flush(Case)

            # add images data
            for url in body.urls:
                img_data = {"url": url, "case_id": new_case.id}
                new_image = ImageCase(**img_data)
                db.add(new_image)
                db.commit()
                db.flush(ImageCase)
                results.append(new_image)

            response = {'caseId': new_case.id, 'images': results}
            return HTTPException(200, response)

           
    except Exception as err:
        print("Error in line:", sys.exc_info()[-1].tb_lineno)
        print("Error message : {0}".format(err))
        raise HTTPException(400, 'Error al agregar las imágenes')
    

@router.post("/send-to-review-for-worker", dependencies=[Depends(verify_token)])
async def send_to_review_for_worker(body: SendToReviewForWorker, request: Request, db: Session = Depends(get_database)):
    try:
        current_user_id = request.user_id_auth
        current_case_id = body.case_id

        case_data = {"state_id": 2, "start_term": get_current_date(), "sent_client_to_operations_date": get_current_date()} #INREVIEWFORWORKER new state, start term: when the case is sent to review
        db.query(Case).filter(Case.id == current_case_id).update(case_data)
        db.commit()
        db.flush(Case)
        
        #search user email
        currentUser = db.query(User).filter(User.id == current_user_id).first()
        find_case = db.query(Case).options(
                    joinedload(Case.contact),
                    joinedload(Case.car),
                    joinedload(Case.damage_state),
                    joinedload(Case.state),
                    joinedload(Case.user)
                    ).filter(Case.id == current_case_id).first()
        summary_data = {}
        if find_case is not None:
            summary_data = {
                "name": find_case.contact.name,
                "last_name": find_case.contact.last_name,
                "email": find_case.contact.email,
                "phone": find_case.contact.phone,
                "region": get_region_by_id(find_case.contact.region_id, db).name if find_case.contact.region_id is not None else 'No definido',
                "commune": get_commune_by_id(find_case.contact.commune_id, db).name if find_case.contact.commune_id is not None else 'No definido',
                "patent": find_case.car.patent,
                "brand": find_case.car.brand.name,
                "model": find_case.car.model.name,
                "year": find_case.car.year,
                "vin": find_case.car.vin if find_case.car.vin != '' else 'No definido',
                "description_damage": find_case.description_damage,
                "images_count": len(get_images_by_id(current_case_id, db))
            }
        await send_email(
            recipients=[currentUser.email],
            subject="¡Tu caso ha sido registrado en Japicar.cl!",
            template_file_path="templates/insertCaso.html",
            context={"name": f'{currentUser.name} {currentUser.last_name}', "current_case_id": current_case_id, "url_client": f'{config.CLIENT_DOMAIN}/clientes/casos?caseId={current_case_id}', "url_contact": f'wa.me/{config.CLIENT_CONTACT}', "summary": summary_data if find_case is not None else None},
        )

        notification_data_client = {
            "user_id": current_user_id,
            "type_id": 16, #NOTIFY_NEW_CASE_CREATED_CLIENT
            "case_id": current_case_id,
            "message": f'¡Hola {find_case.contact.name} {find_case.contact.last_name}! Gracias por subir tu caso a Japicar.cl. Recibirás cotizaciones pronto para elegir la mejor alternativa. Equipo Japicar.cl',
        }

        await create_notification(notification=notification_data_client, keyWs="UPDATE_NOTIFICATIONS_CLIENT", request=request, db=db)

        notification_data = {
            "role_id": 2, #OPERATIONS
            "type_id": 6, #NOTIFY_NEW_CASE_CREATED
            "case_id": current_case_id,
            "message": f'Se ha registrado un nuevo caso Japi N° {find_case.id}. Equipo JapiCar.cl',
        }
        await create_notification(notification=notification_data, keyWs="UPDATE_NOTIFICATIONS_OPERATIONS", request=request, db=db)

        #send email to operation
        all_emails = get_all_users_by_role_id(2, db, only_email=True)
        if all_emails is not None:

            data_email_to_operations = {
                'client_name': f'{find_case.user.name} {find_case.user.last_name}',
                'patent': find_case.car.patent,
                'case_id': current_case_id,
                'current_date': get_current_date("%d/%m/%Y"),
                "current_time": get_current_date().strftime("%H:%M:%S"),
            }

            context_email = {
                "url_client": f'{config.CLIENT_DOMAIN}/operaciones/casos/detalles/{current_case_id}',
                "current_case_id": current_case_id,
                "contact_url": config.CONTACT_URL,
                "data": data_email_to_operations,
            }
            
            await send_email(
                recipients=all_emails,
                subject="¡Nuevo Caso ha sido registrado en Japicar.cl!",
                template_file_path="templates/newCaseInserted.html",
                context=context_email,
            )

        response = {'caseId': current_case_id}
        return HTTPException(200, response)
    except Exception as err:
        print("Error in line:", sys.exc_info()[-1].tb_lineno)
        print("Error message : {0}".format(err))
        raise HTTPException(400, 'Error al enviar el caso a revisión por el trabajador')
       
@router.get("/get-all-quotes-by-case-id", dependencies=[Depends(verify_token)], response_model=List[QuoteCaseItem])
def get_all_quotes_by_case_id(case_id: Optional[int] = Query(None, alias="caseId"),
                              db: Session = Depends(get_database)):
    try:
        if case_id is None:
            raise HTTPException(400, 'case_id es requerido')

        query = db.query(QuoteCase).filter(QuoteCase.case_id == case_id,
                                           QuoteCase.status_id == 2, #APPROVED
                                           QuoteCase.is_deleted == False)

        query = query.order_by(QuoteCase.created_at.desc())

        quotes = query.all()
       
        for quote in quotes:
            quote.quote_items = get_quotes_items_by_quote_id(quote.id, db)

        return quotes
    except Exception as err:
        print("Error in line:", sys.exc_info()[-1].tb_lineno)
        print("Error message : {0}".format(err))
        raise HTTPException(400, 'Error al obtener las cotizaciones')
    

@router.post("/approve-quote", dependencies=[Depends(verify_token)])
async def approve_quote(body: ApproveQuoteClient, request: Request, db: Session = Depends(get_database)):
    try:
        user_id_auth = request.user_id_auth
        current_quote_id = body.quote_id
        current_case_id = body.case_id

        quote_data = {"status_id": 2, "approve_client_date": get_current_date()} #APPROVED
        case_data = {"approved_date": get_current_date(), "state_id": 4} #APPROVE
        db.query(QuoteCase).filter(QuoteCase.id == current_quote_id, QuoteCase.case_id == current_case_id).update(quote_data)
        db.commit()
        db.flush(QuoteCase)

        db.query(Case).filter(Case.id == current_case_id).update(case_data)
        db.commit()
        db.flush(Case)

        #add awarded quote
        current_case = db.query(Case).options(joinedload(Case.car), joinedload(Case.contact)).filter(Case.id == current_case_id, Case.is_deleted == False).first()
        current_quote = db.query(QuoteCase).filter(QuoteCase.id == current_quote_id, QuoteCase.case_id == current_case_id).first()
        awarded_quote_data = {"case_id": current_case_id, "user_id": user_id_auth, "quote_id": current_quote_id, "workshop_user_id": current_quote.user_id}
        new_awarded_quote = AwardedQuoteCase(**awarded_quote_data)
        db.add(new_awarded_quote)
        db.commit()
        db.flush(AwardedQuoteCase)

        #add notification to operators, especific workshop and client
        all_mails_operators = get_all_users_by_role_id(2, db, only_email=True)
        find_quote = db.query(QuoteCase).filter(QuoteCase.id == current_quote_id, QuoteCase.case_id == current_case_id).first()
        find_case = db.query(Case).filter(Case.id == current_case_id, Case.is_deleted == False).first()
        workshop_user_data = get_user_by_id(find_quote.user_id, db)
        client_data = get_user_by_id(find_case.user_id, db)
        if all_mails_operators is not None:

            data_email_operations = {
                "workshop_name": f'{workshop_user_data.workshop.name}',
                "workshop_address": f'{workshop_user_data.workshop.region.name}, {workshop_user_data.workshop.commune.name}',
                "tec_name": f'{workshop_user_data.name} {workshop_user_data.last_name}',
                "workshop_phone": workshop_user_data.workshop.phone if workshop_user_data.workshop.phone is not '' else 'No definido',
                "workshop_email": workshop_user_data.workshop.email if workshop_user_data.workshop.email is not '' else 'No definido',
                "case_id": current_case_id,
                "init_service_date": find_quote.init_service_date.strftime("%d/%m/%Y"),
                "end_service_date": find_quote.end_service_date.strftime("%d/%m/%Y"),
                "car_brand": current_case.car.brand.name,
                "car_model": current_case.car.model.name,
                "car_year": current_case.car.year,
                "gross_price": get_gross_price_all_quotes_items_by_quote_id(find_quote.id, db),
            }

            context = {
                "url_client": f'{config.CLIENT_DOMAIN}/operaciones/casos/detalles/{current_case_id}',
                "current_case_id": current_case_id,
                "data": data_email_operations,
            }

            await send_email(
                recipients=all_mails_operators,
                subject=f'¡Nueva adjudicación en Japicar.cl!',
                template_file_path="templates/quoteApprovedOperators.html",
                context=context
            )

            notification_data_for_operators = {
                "type_id": 10, #NOTIFY_AWARDED_QUOTE_CASE_TO_OPERATIONS
                "role_id": 2, #OPERATIONS
                "case_id": current_case_id,
                "quote_id": current_quote_id,
                "message": f'Un cliente ha adjudicado el caso Japi N° {current_case_id}. Equipo JapiCar.cl',

            }
            await create_notification(notification=notification_data_for_operators, keyWs="UPDATE_NOTIFICATIONS_OPERATIONS", request=request, db=db)

        if workshop_user_data is not None:
            data_email_workshop = {
                "client_name": f'{current_case.contact.name} {current_case.contact.last_name}',
                "client_rut": current_case.contact.rut,
                "client_patent": current_case.car.patent,
                "client_phone": current_case.contact.phone,
                "client_email": current_case.contact.email,
                "case_id": current_case_id,
            }
            context = {
                "url_client": f'{config.CLIENT_DOMAIN}/talleres/casos/detalles/{current_case_id}',
                "contact_url": config.CONTACT_URL,
                "current_case_id": current_case_id,
                "data": data_email_workshop
            }

            await send_email(
                recipients=[workshop_user_data.email],
                subject=f'¡Ya tienes una nueva reparación para tu taller con Japicar.cl!',
                template_file_path="templates/quoteApprovedWorkshop.html",
                context=context,
            )

            notification_data_for_workshop = {
                "type_id": 11, #NOTIFY_AWARDED_QUOTE_CASE_TO_WORKSHOP
                "user_id": workshop_user_data.id,
                "case_id": current_case_id,
                "quote_id": current_quote_id,
                "message": f'Un cliente ha adjudicado tu cotización para el caso Japi N° {current_case_id}. Prepárate para coordinar la reparación. Equipo JapiCar.cl'

            }
            await create_notification(notification=notification_data_for_workshop, keyWs="UPDATE_NOTIFICATIONS_WORKSHOPS", request=request, db=db)

        if client_data is not None:
            data_email = {
                "workshop_name": workshop_user_data.workshop.name,
                "workshop_phone": workshop_user_data.workshop.phone if workshop_user_data.workshop.phone is not '' else 'No definido',
                "workshop_email": workshop_user_data.workshop.email if workshop_user_data.workshop.email is not '' else 'No definido',
                "workshop_region": workshop_user_data.workshop.region.name if workshop_user_data.workshop.region is not None else 'No definido',
                "workshop_commune": workshop_user_data.workshop.commune.name if workshop_user_data.workshop.commune is not None else 'No definido',
                "tec_user_full_name": f'{workshop_user_data.name} {workshop_user_data.last_name}',
                "tec_user_email": workshop_user_data.email,
                "tec_user_phone": workshop_user_data.phone,
                "case_id": current_case_id,
                "init_date": find_quote.init_service_date.strftime("%d/%m/%Y"),
                "end_date": find_quote.end_service_date.strftime("%d/%m/%Y"),
                "net_price": get_net_price_all_quotes_items_by_quote_id(current_quote_id, db),
            }

            await send_email(
                recipients=[client_data.email, current_case.contact.email],
                subject=f'¡La reparación de tu auto ya tiene taller con Japicar.cl!',
                template_file_path="templates/quoteApprovedClient.html",
                context={"url_client": f'{config.CLIENT_DOMAIN}/clientes/casos?caseId={current_case_id}&quoteId={current_quote_id}', "data_email":data_email,"current_case_id": current_case_id, "name": f'{client_data.name} {client_data.last_name}', "url_contact": f'wa.me/{config.CLIENT_CONTACT}'},
            )

            notification_data_for_client = {
                "user_id": client_data.id,
                "type_id": 17, #NOTIFY_AWARDED_QUOTE_CASE_TO_CLIENT
                "case_id": current_case_id,
                "quote_id": current_quote_id,
                "message": f'¡Hola {client_data.name} {client_data.last_name}! Has adjudicado la reparación de tu auto en JapiCar. Revisa los detalles de tu caso. Equipo Japicar.cl'

            }
            await create_notification(notification=notification_data_for_client, keyWs="UPDATE_NOTIFICATIONS_CLIENT", request=request, db=db)
            

        response = {'quoteId': current_quote_id}
        return HTTPException(200, response)
    except Exception as err:
        print("Error in line:", sys.exc_info()[-1].tb_lineno)
        print("Error message : {0}".format(err))
        raise HTTPException(400, 'Error al aprobar la cotización')
    

@router.get("/get-all-cases-approved", dependencies=[Depends(verify_token)], response_model=Page[CaseDataBase])
def get_all_cases_approved(request: Request,
                           pag_params: Params = Depends(),
                           db: Session = Depends(get_database)):
    try:
        user_id_auth = request.user_id_auth
        query = db.query(Case).filter(Case.user_id == user_id_auth, Case.is_deleted == False, Case.state_id == 4) #APPROVED
        query = query.order_by(Case.created_at.desc())
        cases = query.all()

        if cases is not None:
            for case in cases:
                current_awarded_quote = db.query(AwardedQuoteCase).filter(AwardedQuoteCase.case_id == case.id, AwardedQuoteCase.is_deleted == False).first()
                case.images = get_images_by_id(case.id, db)
                case.quote = get_quote_by_id(current_awarded_quote.quote_id, db)
                case.quotes = None

        return paginate(cases, params=pag_params)
    
    except Exception as err:
        print("Error in line:", sys.exc_info()[-1].tb_lineno)
        print("Error message : {0}".format(err))
        raise HTTPException(400, 'Error al obtener las cotizaciones')