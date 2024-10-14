import sys
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, Request, Query
from fastapi_pagination import paginate, Params, Page
from typing import Optional
from fastapi.param_functions import Depends
from sqlalchemy.orm.session import Session
from sqlalchemy.orm import joinedload
from app.database.main import get_database
from ...middlewares.verify_token import verify_token
from .....config import config
from ...services.send_mail import send_email

from app.API.v1.modules.cases.schema import EvaluationDataClientToTecnical, CaseDataBase, QuoteCaseItem, QuoteDataApproved
from app.API.v1.modules.cases.model import Case, ContactCase, CarCase, ImageCase, QuoteCase, QuoteItemCase, AwardedQuoteCase
from app.API.v1.modules.users.model import User
from app.API.v1.modules.workshops.model import Workshop

from ...helpers.calculate_time_difference import calculate_time_difference

from .helpers.Images_by_id import get_images_by_id
from .helpers.quote_by_case_id_and_user_id import get_all_quotes_by_case_id, get_quote_by_id
from .helpers.quote_by_case_id_and_user_id import get_quotes_items_by_quote_id
from ...helpers.get_current_date_chile import get_current_date

from ..users.helpers.get_all_users_by_role_id import get_all_users_by_role_id
from ..users.helpers.get_user_by_id import get_user_by_id
from ..notifications.helpers.create_notificacion import create_notification
from ...helpers.constants.business import TEXTS_MESSAGES_NOTIFICATIONS
from ...helpers.typeDamageDict import type_damage_dict

router = APIRouter(prefix="/cases", tags=["Cases"])

#OPERATIONS ENDPOINTS
@router.get("/operations/all-cases", dependencies=[Depends(verify_token)])
def get_case_by_id_simple(
                          case_id: Optional[int] = Query(None, alias="caseId"),
                          patent: Optional[str] = Query(None, alias="patent"),
                          state_id: Optional[int] = Query(None, alias="stateId"),
                          start_date: Optional[str] = Query(None, alias="startDate"),
                          end_date: Optional[str] = Query(None, alias="endDate"),
                          pag_params: Params = Depends(),
                          db: Session = Depends(get_database)):
    try:
        query = db.query(Case).options(
            joinedload(Case.state),
            joinedload(Case.damage_state),
            joinedload(Case.car),
            ).filter(Case.is_deleted == False)

        if state_id is not None:
            query = query.filter(Case.state_id == state_id)
        else:
            query = query.filter(Case.state_id.in_([2, 5, 1, 6, 4, 7, 8]))

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

        if patent is not None:
            query = query.join(CarCase).filter(CarCase.patent.startswith(patent))



        query = query.order_by(Case.created_at.desc())

        cases = query.all()
        
        return paginate(cases, params=pag_params)
        
    except Exception as err:
        print("Error in line:", sys.exc_info()[-1].tb_lineno)
        print("Error message : {0}".format(err))
        raise HTTPException(400, 'Error al obtener el caso')
    

@router.get("/operations/get-case-by-id/{case_id}", dependencies=[Depends(verify_token)], response_model=CaseDataBase)
def get_case_by_id(case_id: int, db: Session = Depends(get_database)):
    try:
        found_case = (
            db.query(Case).options(
                joinedload(Case.contact),
                joinedload(Case.car),
                joinedload(Case.damage_state),
                joinedload(Case.state),)
                .filter(Case.id == case_id).filter(Case.is_deleted == False).first()
        )

        if found_case is not None:
            current_awarded_quote = db.query(AwardedQuoteCase).filter(AwardedQuoteCase.case_id == found_case.id, AwardedQuoteCase.is_deleted == False).first()
            
            found_case.images = get_images_by_id(case_id, db)
            found_case.quote = get_quote_by_id(current_awarded_quote.quote_id, db) if current_awarded_quote is not None else None
            found_case.quotes = get_all_quotes_by_case_id(case_id, db)
            return found_case
        else:
            return HTTPException(404, 'No se encontró el caso')
        
    except Exception as err:
        print("Error in line:", sys.exc_info()[-1].tb_lineno)
        print("Error message : {0}".format(err))
        raise HTTPException(400, 'Error al obtener el caso')
    


@router.post("/operations/update-evaluation-client-to-technical", dependencies=[Depends(verify_token)])
async def create_evaluation_client_to_technical(body: EvaluationDataClientToTecnical, request: Request, db: Session = Depends(get_database)):
    try:
        current_case_id = body.case_id
        find_current_case = db.query(Case).filter(Case.id == current_case_id).first()
        
        #update contact data
        contact_data = {"name": body.contact.name,  "last_name": body.contact.last_name, "rut": body.contact.rut, "email": body.contact.email, "phone": body.contact.phone, "region_id": body.contact.region_id, "commune_id": body.contact.commune_id}
        db.query(ContactCase).filter(ContactCase.id == find_current_case.contact_id).update(contact_data)
        db.commit()
        db.flush(ContactCase)

        #update car data
        car_data = {"patent": body.car.patent, "brand_id": body.car.brand_id, "model_id": body.car.model_id, "year": body.car.year, "vin": body.car.vin}
        db.query(CarCase).filter(CarCase.id == find_current_case.car_id).update(car_data)
        db.commit()
        db.flush(CarCase)

        #update images data
        #1.-update state current img in bd
        db.query(ImageCase).filter(ImageCase.case_id == current_case_id).update({"is_deleted": True})
        db.commit()
        db.flush(ImageCase)
        #2.-insert new imgs in bd
        for url in body.images:
            img_data = {"url": url, "case_id": current_case_id}
            new_image = ImageCase(**img_data)
            db.add(new_image)
            db.commit()
            db.flush(ImageCase)

        #update case data
        find_case = db.query(Case).options(joinedload(Case.contact)).filter(Case.id == current_case_id).first()
        case_data = {"description_damage": body.description_Damage, "start_term": body.start_term, "end_term": body.end_term, "damage_state_id": body.damage_state_id, "state_id": 1}# 1 -> INUOTATION
        
        is_rejected_by_damage = False
        if (body.damage_state_id == 3 and find_case.damage_state_id != 3 and find_case.state_id == 2): #HIGH
            case_data['state_id'] = 7 #REJECTED_BY_DAMAGE

            #enviar email/note a cliente por dechazo.
            client_id = find_case.user_id
            user_data = get_user_by_id(client_id, db)
            if user_data is not None:

                user_data_email = {
                    "name": f'{user_data.name} {user_data.last_name}',
                }


                await send_email(
                    recipients=[user_data.email, find_case.contact.email],
                    subject="Tenemos información importante sobre tu caso.",
                    template_file_path="templates/rejectedCaseByDamage.html",
                    context={"url_client": f'{config.CLIENT_DOMAIN}/clientes/casos?caseId={current_case_id}', "current_case_id": current_case_id, "user_data": user_data_email, "contact_url": f'wa.me/{config.CLIENT_CONTACT}'},
                )

                notification_data = {
                    "user_id": user_data.id,
                    "type_id": 12, #NOTIFY_REJECTED_BY_DAMAGE
                    "case_id": current_case_id,
                    "message": f'¡Hola {user_data.name} {user_data.last_name}! Gracias por confiar en JapiCar. Revisa tu correo. Equipo Japicar.cl',
                }
                await create_notification(notification=notification_data, keyWs="UPDATE_NOTIFICATIONS_CLIENT", request=request, db=db)
            is_rejected_by_damage = True

        if find_case.sent_operations_to_workshop_date is None:
            case_data["sent_operations_to_workshop_date"] = get_current_date()
        else:
            case_data["update_at"] = get_current_date()
        
        db.query(Case).filter(Case.id == current_case_id).update(case_data)
        db.commit()
        db.flush(Case)

        if is_rejected_by_damage:
            return HTTPException(200, 'Case updated successfully')
        
        all_emails = get_all_users_by_role_id(3, db, only_email=True) #WORKSHOPS
        if case_data.get('sent_operations_to_workshop_date') is not None:
            
            #send email and notification to workshop
            if all_emails is not None:
                current_date_chile = get_current_date()
                data_email_workshop = {
                    "type_damage": type_damage_dict[find_case.damage_state_id],
                    "time_difference": calculate_time_difference(current_date_chile, find_case.end_term),
                }

                context = {
                    "url_client": f'{config.CLIENT_DOMAIN}/talleres/casos/detalles/{current_case_id}',
                    "contact_url": config.CONTACT_URL,
                    "current_case_id": current_case_id,
                    "data": data_email_workshop
                }
                await send_email(
                    recipients=all_emails,
                    subject="¡Nuevo caso disponible para cotización en JapiCar.cl!",
                    template_file_path="templates/caseToinuotation.html",
                    context=context
                )

            notification_data = {
                "role_id": 3, #WORKSHOPS
                "type_id": 4, #NOTIFY_OPERATOR_RELEASED_CASE_FOR_QUOTATION
                "case_id": current_case_id,
                "message": f'Un nuevo caso Japi N° {current_case_id} está disponible para cotización. Revisa y envía tu cotización. Equipo Japicar.cl',
            }
            await create_notification(notification=notification_data, keyWs="UPDATE_NOTIFICATIONS_WORKSHOPS", request=request, db=db)

            #send email and notification to client
            client_data = get_user_by_id(find_case.user_id, db)
            if client_data is not None:
                client_data_email = {
                    "name": f'{client_data.name} {client_data.last_name}',
                }
                current_date_chile = get_current_date()
                case_data = {
                    "time_difference": calculate_time_difference(current_date_chile, find_case.end_term),
                }

                await send_email(
                    recipients=[client_data.email],
                    subject=f'¡Tu caso ya está en cotización!',
                    template_file_path="templates/caseToinuotationClient.html",
                    context={"current_case_id":current_case_id, "url_client": f'{config.CLIENT_DOMAIN}/clientes/casos?caseId={current_case_id}', "client_data": client_data_email, "contact_url": f'wa.me/{config.CLIENT_CONTACT}', "case_data": case_data},
                )

                notification_data_for_client = {
                    "user_id": client_data.id,
                    "type_id": 18, #NOTIFY_OPERATOR_RELEASED_CASE_FOR_QUOTATION_TO_CLIENT
                    "case_id": current_case_id,
                    "message": f'¡Hola {client_data.name} {client_data.last_name}! Tu caso está siendo cotizado por nuestros talleres. Equipo Japicar.cl ',
                }
                await create_notification(notification=notification_data_for_client, keyWs="UPDATE_NOTIFICATIONS_CLIENT", request=request, db=db)

        else:
            #send email and notification to workshop
            if all_emails is not None:
                await send_email(
                    recipients=all_emails,
                    subject=f'Se ha actualizado la información del caso {current_case_id}',
                    template_file_path="templates/caseUpdated.html",
                    context={"current_case_id":current_case_id, "url_client": f'{config.CLIENT_DOMAIN}/talleres/casos/detalles/{current_case_id}'},
                ) 

            notification_data = {
                "role_id": 3, #WORKSHOPS
                "type_id": 7, #NOTIFY_CHANGE_INFO_CASE
                "case_id": current_case_id,
                "message": TEXTS_MESSAGES_NOTIFICATIONS[7],
            }
            await create_notification(notification=notification_data, keyWs="UPDATE_NOTIFICATIONS_WORKSHOPS", request=request, db=db)

        return HTTPException(200, 'Case updated successfully')


    except Exception as err:
        print("Error in line:", sys.exc_info()[-1].tb_lineno)
        print("Error message : {0}".format(err))
        raise HTTPException(400, 'Error al crear la evaluación')
    

@router.get("/operations/get-all-quotes-by-case-id", dependencies=[Depends(verify_token)], response_model=Page[QuoteCaseItem])
def get_quotes_by_case_id(case_id: Optional[int] = Query(None, alias="caseId"),
                          workshop_name: Optional[str] = Query(None, alias="workshopName"),
                          state_id: Optional[int] = Query(None, alias="stateId"),
                          pag_params: Params = Depends(),
                          db: Session = Depends(get_database)):
    try:
        if case_id is None or case_id == 0:
            raise HTTPException(400, 'case_id es requerido')

        query = db.query(QuoteCase).filter(QuoteCase.case_id == case_id, QuoteCase.is_deleted == False)

        if state_id is not None:
            query = query.filter(QuoteCase.status_id == state_id)

        if workshop_name is not None:
            query = query.join(User).join(Workshop).filter(Workshop.name.startswith(workshop_name))


        query = query.order_by(QuoteCase.approve_client_date.desc())

        quotes = query.all()

       
       
        for quote in quotes:
            quote.quote_items = get_quotes_items_by_quote_id(quote.id, db)
            
        return paginate(quotes, params=pag_params)
    
    except Exception as err:
        print("Error in line:", sys.exc_info()[-1].tb_lineno)
        print("Error message : {0}".format(err))
        raise HTTPException(400, 'Error al obtener las cotizaciones')
    

@router.post("/operations/approved-quote", dependencies=[Depends(verify_token)])
async def get_quotes_by_case_id(body: QuoteDataApproved, request: Request, db: Session = Depends(get_database)):
    try:
      find_quote = db.query(QuoteCase).filter(QuoteCase.id == body.quote_id).first()
      

      if find_quote is not None:
        #update is_deleted in items quotes          
        db.query(QuoteItemCase).filter(QuoteItemCase.quote_case_id == body.quote_id, QuoteItemCase.is_deleted == False).update({"is_deleted": True})
        db.commit()
        db.flush(QuoteItemCase)

        #add new items quotes
        for item in body.items:
            quote_item_data = {"name": item.name, "labor_price": item.labor_price, "spare_parts_price": item.spare_parts_price, "quote_case_id": body.quote_id}
            new_item = QuoteItemCase(**quote_item_data)
            db.add(new_item)
            db.commit()
            db.flush(QuoteItemCase)


        #update quote data
        quote_data = {"description": body.description, "status_id": 2}#APPROVED

        if find_quote.send_to_approve_date is None:
            quote_data["send_to_approve_date"] = get_current_date()
        else:
            quote_data["update_at"] = get_current_date()

        db.query(QuoteCase).filter(QuoteCase.id == find_quote.id).update(quote_data)
        db.commit()
        db.flush(QuoteCase)
        
        find_case = db.query(Case).filter(Case.id == find_quote.case_id, Case.is_deleted == False).first()
        
        if find_case.state_id == 1: #INOUVATION
            db.query(Case).filter(Case.id == find_quote.case_id, Case.is_deleted == False).update({"state_id": 6}) #PENDINGAPPROVAL
            db.commit()
            db.flush(Case)

        #send email and notification to client and workshop
        find_case = db.query(Case).options(joinedload(Case.contact), joinedload(Case.car)).filter(Case.id == find_quote.case_id, Case.is_deleted == False).first()
        user_data = get_user_by_id(find_case.user_id, db)
        workshop_user_data = get_user_by_id(find_quote.user_id, db)
        client_emails = [user_data.email, find_case.contact.email] if user_data is not None else None

        if client_emails is not None:
            current_date_chile = get_current_date()
            user_data_email = {
                "name": f'{user_data.name} {user_data.last_name}',
            }
            case_data = {
                "name": f'{find_case.contact.name} {find_case.contact.last_name}',
                "rut": find_case.contact.rut,
                "patent": find_case.car.patent,
                "case_id": find_case.id,
                'time_difference': calculate_time_difference(current_date_chile, find_case.end_term),
            }
            
            await send_email(
                recipients=client_emails,
                subject=f'¡Tienes una nueva cotización disponible para tu caso!',
                template_file_path="templates/newQuoteForCase.html",
                context={"url_client": f'{config.CLIENT_DOMAIN}/cliente/casos?caseId={find_case.id}&quoteId={find_quote.id}', "current_case_id": find_case.id, "user_data": user_data_email, "case_data": case_data, "url_contact": f'wa.me/{config.CLIENT_CONTACT}'},
            )
            
            notification_data_for_client = {
                "type_id": 9, #NOTIFY_ADDED_QUOTE_TO_CASE
                "case_id": find_case.id,
                "quote_id": find_quote.id,
                "user_id": user_data.id,
                "message": f'¡Hola {user_data.name} {user_data.last_name}! Un taller ha subido una cotización para tu caso. Compara las opciones y elige. Equipo Japicar.cl',
            }

            await create_notification(notification=notification_data_for_client, keyWs="UPDATE_NOTIFICATIONS_CLIENT", request=request, db=db)

        if workshop_user_data is not None:
            await send_email(
                recipients=[workshop_user_data.email],
                subject=f'Se ha aprobado tu cotización ingresada para el caso N° {find_case.id}',
                template_file_path="templates/approvedQuoteForCase.html",
                context={"url_client": f'{config.CLIENT_DOMAIN}/talleres/casos/detalles/{find_case.id}', "current_case_id": find_case.id},
            )

            notification_data_for_workshop = {
                "type_id": 8, #NOTIFY_QUOTATION_APPROVED
                "case_id": find_case.id,
                "quote_id": find_quote.id,
                "user_id": find_quote.user_id,
                "message": TEXTS_MESSAGES_NOTIFICATIONS[8],
            }

            await create_notification(notification=notification_data_for_workshop, keyWs="UPDATE_NOTIFICATIONS_WORKSHOPS", request=request, db=db)

        



        return HTTPException(200, 'Cotización aprobada exitosamente')
          
    except Exception as err:
        print("Error in line:", sys.exc_info()[-1].tb_lineno)
        print("Error message : {0}".format(err))
        raise HTTPException(400, 'Error al aprobar la cotización')