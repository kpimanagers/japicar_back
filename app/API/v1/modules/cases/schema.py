from pydantic import Field
from typing import Optional, List
from datetime import datetime

from ...helpers.schema import Base

from ..brands.schema import BrandItem, ModelItem
from ..users.schema import UserItem


class ContactDataBase(Base):
    case_id: Optional[int] = Field(None,alias="caseId")
    name: str
    last_name: str = Field(..., alias="lastName")
    rut: str
    email: str
    phone: str
    region_id: Optional[int] = Field(alias="regionId")
    commune_id: Optional[int] = Field(alias="communeId")

    class Config:
        schema_extra = {
            "example": {
                "full_name": "javier baez",
                "rut": "123456789",
                "email": "javier@foreach.cl",
                "phone": "123456789",
                "region_id": 1,
                "commune_id": 1,
            }
        }

class ContactDataPartial(Base):
    case_id: Optional[int] = Field('',alias="caseId")
    name: Optional[str] = Field('', alias="name")
    last_name: Optional[str] = Field('', alias="lastName")
    rut: Optional[str] = Field('', alias="rut")
    email: Optional[str] = Field('', alias="email")
    phone: Optional[str] = Field('', alias="phone")
    region_id: Optional[str] = Field(None, alias="regionId")
    commune_id: Optional[str] = Field(None, alias="communeId")

    class Config:
        schema_extra = {
            "example": {
                "full_name": "javier baez",
                "rut": "123456789",
                "email": "javier@foreach.cl",
                "phone": "123456789",
                "region_id": 1,
                "commune_id": 1,
            }
        }

class ContactData(ContactDataBase):
    id: int

    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "full_name": "javier baez",
                "rut": "123456789",
                "email": "javier@foreach.cl",
                "phone": "123456789",
                "region_id": 1,
                "commune_id": 1,
            }
        }

class CarDataBase(Base):
    case_id: Optional[int] = Field(None,alias="caseId")
    patent: str
    brand_id: str = Field(alias="brandId")
    model_id: str = Field(alias="modelId")
    year: int
    vin: Optional[str] = Field('', alias="vin")

    class Config:
        schema_extra = {
            "example": {
                "patent": "123456789",
                "brand_id": "1",
                "model_id": "1",
                "year": 2020,
                "vin": "123456789",
            }
        }

class CarDataPartial(Base):
    case_id: Optional[int] = Field(None,alias="caseId")
    patent: Optional[str] = Field('', alias="patent")
    brand_id: str = Field('', alias="brandId")
    model_id: str = Field('', alias="modelId")
    year: Optional[str] = Field('', alias="year")
    vin: Optional[str] = Field('', alias="vin")

    class Config:
        schema_extra = {
            "example": {
                "patent": "123456789",
                "brand_id": "1",
                "model_id": "1",
                "year": 2020,
                "vin": "123456789",
            }
        }

class DamageDataBase(Base):
    case_id: Optional[int] = Field(None,alias="caseId")
    description_damage: str = Field(alias="descriptionDamage")

class ImageDataBase(Base):
    case_id: Optional[int] = Field(None,alias="caseId")
    urls: List[str] = Field(alias="urls")

class SendToReviewForWorker(Base):
    case_id: int = Field(alias="caseId")

class CarData(CarDataBase):
    id: int

    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "patent": "123456789",
                "brand": "ford",
                "model": "f150",
                "year": 2020,
                "vin": "123456789",
            }
        }

# Esquemas relacionados a un caso



class ContactCase(Base):
    id: int 
    name: Optional[str] = Field('', alias="name")
    last_name: Optional[str] = Field('', alias="lastName")
    rut: Optional[str] = Field('', alias="rut")
    email: Optional[str] = Field('', alias="email")
    phone: Optional[str] = Field('', alias="phone")
    region_id: Optional[int] = Field(None, alias="regionId")
    commune_id: Optional[int] = Field(None, alias="communeId")

    


 

class CarCase(Base):
    id: int
    patent: Optional[str] = Field('', alias="patent")
    brand_id: Optional[int] = Field('' ,alias="brandId")
    model_id: Optional[int] = Field('' ,alias="modelId")
    year: Optional[int] = Field('', alias="year")
    vin: Optional[str] = Field('', alias="vin")
    brand: Optional[BrandItem] = Field(None, alias="brand")
    model: Optional[ModelItem] = Field(None, alias="model")




class ImagesCase(Base):
    id: int
    url: str
    case_id: int

class StateCase(Base):
    id: int
    name: str

class DamageStateCase(Base):
    id: int
    name: str


class QuoteItemCase(Base):
    id: int
    name: str
    labor_price: int = Field(alias="laborPrice")
    spare_parts_price: int = Field(alias="sparePartsPrice")

class QuoteShopCase(Base):
    id: int
    url: str
    
class PaymentMethodsCase(Base):
    id: int
    name: str

class StatusQuoteCase(Base):
    id: int
    name: str

class QuoteCaseItem(Base):
    id: int
    description: str
    use_crane: bool = Field(alias="useCrane")
    use_drive: bool = Field(alias="useDrive")
    init_service_date: Optional[datetime] = Field(None, alias="initServiceDate")
    end_service_date: Optional[datetime] = Field(None, alias="endServiceDate")
    payment_method_id: Optional[int] = Field(None, alias="paymentMethodId")
    validity_init_quote_date: datetime = Field(alias="validityInitQuoteDate")
    validity_end_quote_date: datetime = Field(alias="validityEndQuoteDate")
    quote_items: List[QuoteItemCase] = Field(alias="quoteItems")
    quote_shop: Optional[QuoteShopCase] = Field(None, alias="quoteShop")
    user: Optional[UserItem] = Field(None, alias="user")
    send_to_review_date: Optional[datetime] = Field(None, alias="sendToReviewDate")
    send_to_approve_date: Optional[datetime] = Field(None, alias="sendToApproveDate")
    approve_client_date: Optional[datetime] = Field(None, alias="approveClientDate")
    payment_method: Optional[PaymentMethodsCase] = Field(None, alias="paymentMethod")
    status: Optional[StatusQuoteCase] = Field(None, alias="status")
    update_at: datetime = Field(alias="updateAt")

class AwardedQuoteCase(Base):
    id: int
    case_id: int = Field(alias="caseId")
    user_id: int = Field(alias="userId")
    quote_id: int = Field(alias="quoteId")
    workshop_user_id: int = Field(alias="workshopUserId")

class NoParticipationMotive(Base):
    name: str
    description: str

class ShopsWithoutParticipationCase(Base):
    user_id: int = Field(alias="userId")
    motive: Optional[NoParticipationMotive] = Field(None, alias="motive")

class CaseDataBase(Base):
    id: int 
    contact_id: Optional[int] = Field(None, alias="contactId")
    contact: Optional[ContactCase] = Field(None, alias="contact")
    car_id: Optional[int] = Field(None, alias="carId")
    car: Optional[CarCase] = Field(None, alias="car")
    description_damage: Optional[str] = Field(None, alias="descriptionDamage")
    damage_state_id: Optional[int] = Field(None, alias="damageStateId")
    state_id: Optional[int] = Field(None, alias="stateId")
    start_term: Optional[datetime] = Field(None, alias="startTerm")
    end_term: Optional[datetime] = Field(None, alias="endTerm")
    images: Optional[List[ImagesCase]] = Field(None, alias="images")
    state: Optional[StateCase] = Field(None, alias="state")
    damage_state: Optional[DamageStateCase] = Field(None, alias="damageState")
    created_at: Optional[datetime] = Field(None, alias="createdAt")

    sent_client_to_operations_date: Optional[datetime] = Field(None, alias="sentClientToOperationsDate")
    sent_operations_to_workshop_date: Optional[datetime] = Field(None, alias="sentOperationsToWorkshopDate")
    approved_date: Optional[datetime] = Field(None, alias="approvedDate")
    
    quote: Optional[QuoteCaseItem] = Field(None, alias="quote")
    quotes: Optional[List[QuoteCaseItem]] = Field(None, alias="quotes")
    awarded_quote_case: Optional[AwardedQuoteCase] = Field(None, alias="awardedQuoteCase")
    shop_without_participation: Optional[List[ShopsWithoutParticipationCase]] = Field(None, alias="shopWithoutParticipation")

    class Config:
        orm_mode = True

class CaseDataSimple(Base):
    id: int 
    state_id: int
    class Config:
        orm_mode = True


class EvaluationDataClientToTecnical(Base):
    contact: ContactDataBase
    car: CarDataBase
    description_Damage: str = Field(alias="descriptionDamage")
    images: List[str]
    case_id: int = Field(alias="id")
    damage_state_id: int = Field(alias="damageStateId")
    start_term: datetime = Field(alias="startTermDate")
    end_term: datetime = Field(alias="endTermDate")

    class Config:
        schema_extra = {
            "example": {
                "contact": {"full_name": "javier baez", "rut": "123456789", "email": "javier@foreach.cl", "phone": "123456789", "region_id": 1, "commune_id": 1},
                "car": {"patent": "123456789", "brand": "ford", "model": "f150", "year": 2020, "vin": "123456789"},
                "description_Damage": "damage description",
                "images": ["https://www.google.com", "https://www.google.com"],
                "case_id": 1,
                "damage_state_id": 1,
                "start_term": "2020-01-01T00:00:00",
                "end_term": "2020-01-01T00:00:00",
            }
        }


#workShop
class QuoteItemBase(Base):
    name: str
    labor_price: int = Field(alias="laborPrice")
    spare_parts_price: int = Field(alias="sparePartsPrice")

class QuoteItem(QuoteItemBase):
    id: int

class QuoteDataBase(Base):
    description: str
    use_crane: bool = Field(alias="useCrane")
    use_drive: bool = Field(alias="useDrive")
    payment_method_id: int = Field(alias="paymentMethodId")
    init_service_date: datetime = Field(alias="initServiceDate")
    end_service_date: datetime = Field(alias="endServiceDate")
    accept_terms: bool = Field(alias="acceptTerms")

class QuoteDataCreate(QuoteDataBase):
    case_id: int = Field(alias="caseId")
    items: List[QuoteItemBase]

class AddQuoteFileCase(Base):
    case_id: int = Field(alias="caseId")
    url: str

class QuoteDataSendToReview(Base):
    case_id: int = Field(alias="caseId")


class QuoteDataApproved(Base):
    quote_id: int = Field(alias="quoteId")
    description: str
    items: List[QuoteItemBase]


class ApproveQuoteClient(Base):
    quote_id: int = Field(alias="quoteId")
    case_id: int = Field(alias="caseId")
    
    



class CaseBasicData(Base):
    id: int
    created_at: Optional[datetime] = Field(None, alias="createdAt")
    description_damage: Optional[str] = Field(None, alias="descriptionDamage")
    car: Optional[CarCase] = Field(None, alias="car")
    state_id: Optional[int] = Field(None, alias="stateId")
    state: Optional[StateCase] = Field(None, alias="state")
    end_term: Optional[datetime] = Field(None, alias="endTerm")
    damage_state: Optional[DamageStateCase] = Field(None, alias="damageState")
    sent_client_to_operations_date: Optional[datetime] = Field(None, alias="sentClientToOperationsDate")
    sent_operations_to_workshop_date: Optional[datetime] = Field(None, alias="sentOperationsToWorkshopDate")
    awarded_quote_case: Optional[AwardedQuoteCase] = Field(None, alias="awardedQuoteCase")
    shop_without_participation: Optional[List[ShopsWithoutParticipationCase]] = Field(None, alias="shopWithoutParticipation")

class NoParticipationData(Base):
    case_id: int = Field(alias="caseId")
    motive_id: int = Field(alias="motiveId")

class DeleteQuoteShopCase(Base):
    quote_id: int = Field(alias="quoteId")
    






        