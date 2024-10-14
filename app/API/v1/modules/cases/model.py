from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.functions import func
from app.database.base_class import Base, TimestampMixin, SoftDeleteMixin
from app.API.v1.modules.regions.model import Region, Commune
from ...helpers.get_current_date_chile import get_current_date

def default_end_service_date():
    return get_current_date() + timedelta(days=30)

class ContactCase(Base, SoftDeleteMixin, TimestampMixin):
    __tablename__ = "contacts_cases"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=True, default='')
    last_name = Column(String(100), nullable=True, default='')
    rut = Column(String(20), nullable=True, default='')
    email = Column(String(100), nullable=True, default='')
    phone = Column(String(20), nullable=True, default='')
    region_id = Column(Integer, ForeignKey("regions.id"), nullable=True, default=None)
    commune_id = Column(Integer, ForeignKey("communes.id"), nullable=True, default=None)

    case = relationship("Case", back_populates="contact", uselist=False)

class CarCase(Base, SoftDeleteMixin, TimestampMixin):
    __tablename__ = "cars_cases"
    id = Column(Integer, primary_key=True)
    patent = Column(String(50), nullable=True, default='')
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=True, default=None)
    model_id = Column(Integer, ForeignKey("models.id"), nullable=True, default=None)
    year = Column(Integer, nullable=True, default=None)
    vin = Column(String(50), nullable=True, default='')

    case = relationship("Case", back_populates="car", uselist=False)
    
    brand = relationship("Brand", back_populates="car", uselist=False, lazy="joined")
    model = relationship("Model", back_populates="car", uselist=False, lazy="joined")

class DamageStateCase(Base, SoftDeleteMixin, TimestampMixin):
    __tablename__ = "damages_state_cases"
    id = Column(Integer, primary_key=True)
    name = Column(String(500), nullable=False) #MILD | MEDIUM | HIGH

    case = relationship("Case", back_populates="damage_state", uselist=False)

class StateCase(Base, SoftDeleteMixin, TimestampMixin):
    __tablename__ = "states_cases"
    id = Column(Integer, primary_key=True)
    name = Column(String(500), nullable=False) #INUOTATION | INREVIEWFORWORKER | INREVIEWFORCLIENT | INCOMPLETE | APPROVED

    case = relationship("Case", back_populates="state", uselist=False)

class ImageCase(Base, SoftDeleteMixin, TimestampMixin):
    __tablename__ = "images_cases"
    id = Column(Integer, primary_key=True)
    url = Column(String(500), nullable=False)
    case_id = Column(Integer, ForeignKey("cases.id"), nullable=False)

    case = relationship("Case", back_populates="images")


class PaymentMethodsCase(Base, SoftDeleteMixin, TimestampMixin):
    __tablename__ = "payment_methods_cases"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)

    quote_case = relationship("QuoteCase", back_populates="payment_method", uselist=False)

class AcceptedTermsQuoteCase(Base, SoftDeleteMixin, TimestampMixin):
    __tablename__ = "accepted_terms_quote_cases"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    quote_case_id = Column(Integer, ForeignKey("quotes_cases.id"), nullable=False)
    description = Column(String(500), nullable=False, default='ok')


class StatusQuoteCase(Base, SoftDeleteMixin, TimestampMixin):
    __tablename__ = "status_quote_cases"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)

    quote_case = relationship("QuoteCase", back_populates="status", uselist=False)


 
class QuoteCase(Base, SoftDeleteMixin, TimestampMixin):
    __tablename__ = "quotes_cases"
    id = Column(Integer, primary_key=True)
    description = Column(String(500), nullable=False)
    use_crane = Column(Boolean, nullable=False)
    use_drive = Column(Boolean, nullable=False)
    
    init_service_date = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), default=func.now())
    end_service_date = Column(DateTime(timezone=True), nullable=False, default=func.now())

    validity_init_quote_date = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), default=func.now())
    validity_end_quote_date = Column(DateTime(timezone=True), nullable=False, default=default_end_service_date)

    quote_shop_id = Column(Integer, ForeignKey("quote_shops_cases.id"), nullable=True)
    payment_method_id = Column(Integer, ForeignKey("payment_methods_cases.id"), nullable=True)
    status_id = Column(Integer, ForeignKey("status_quote_cases.id"), nullable=True, default=4) #NOT_SEND

    case_id = Column(Integer, ForeignKey("cases.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    payment_method = relationship("PaymentMethodsCase", back_populates="quote_case", uselist=False, lazy="joined")
    quote_items = relationship("QuoteItemCase", back_populates="quote_case")
    quote_shop = relationship("QuoteShopCase", back_populates="quote_case", uselist=False, lazy="joined")
    user = relationship("User", back_populates="quote", uselist=False, lazy="joined")
    status = relationship("StatusQuoteCase", back_populates="quote_case", uselist=False, lazy="joined")

    case = relationship("Case", back_populates="quote")

    #fechas de registros:
    send_to_review_date = Column(DateTime(timezone=True), nullable=True, default=None)
    send_to_approve_date = Column(DateTime(timezone=True), nullable=True, default=None)
    approve_client_date = Column(DateTime(timezone=True), nullable=True, default=get_current_date)

    
    


class QuoteItemCase(Base, SoftDeleteMixin, TimestampMixin):
    __tablename__ = "quote_items_cases"
    id = Column(Integer, primary_key=True)
    name = Column(String(500), nullable=False)
    labor_price = Column(Float, nullable=False)
    spare_parts_price = Column(Float, nullable=False)

    quote_case_id = Column(Integer, ForeignKey("quotes_cases.id"), nullable=False)
    quote_case = relationship("QuoteCase", back_populates="quote_items")

class QuoteShopCase(Base, SoftDeleteMixin, TimestampMixin):
    __tablename__ = "quote_shops_cases"
    id = Column(Integer, primary_key=True)
    url = Column(String(500), nullable=False)

    quote_case = relationship("QuoteCase", back_populates="quote_shop", uselist=False)

class NoParticipationMotive(Base, SoftDeleteMixin, TimestampMixin):
    __tablename__ = "no_participation_motives"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500), nullable=False)

    shop_without_participation = relationship("ShopsWithoutParticipationCase", back_populates="motive", uselist=False)

class ShopsWithoutParticipationCase(Base, SoftDeleteMixin, TimestampMixin):
    __tablename__ = "shops_without_participation_cases"
    id = Column(Integer, primary_key=True)
    case_id = Column(Integer, ForeignKey("cases.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    motive_id = Column(Integer, ForeignKey("no_participation_motives.id"), nullable=False)

    case = relationship("Case", back_populates="shop_without_participation")
    motive = relationship("NoParticipationMotive", back_populates="shop_without_participation", lazy="joined")


class AwardedQuoteCase(Base, SoftDeleteMixin, TimestampMixin):
    __tablename__ = "awarded_quote_cases"
    id = Column(Integer, primary_key=True)
    case_id = Column(Integer, ForeignKey("cases.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    quote_id = Column(Integer, ForeignKey("quotes_cases.id"), nullable=False)
    workshop_user_id = Column(Integer, ForeignKey("users.id"), nullable=False, default=None)

    case = relationship("Case", back_populates="awarded_quote_case", uselist=False)

    # Define the relationship for `workshop_user` using `workshop_user_id`
    """ workshop_user = relationship("User", foreign_keys=[workshop_user_id], back_populates="workshop_awarded_quote_case", uselist=False) """


class Case(Base, SoftDeleteMixin, TimestampMixin):
    __tablename__ = "cases"
    id = Column(Integer, primary_key=True)
    description_damage = Column(String(700), nullable=True, default='')
    start_term = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), default=func.now())
    end_term = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), default=func.now())

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="case", uselist=False)

    contact_id = Column(Integer, ForeignKey("contacts_cases.id"), nullable=True)
    contact = relationship("ContactCase", back_populates="case", uselist=False)

    car_id = Column(Integer, ForeignKey("cars_cases.id"), nullable=True)
    car = relationship("CarCase", back_populates="case", uselist=False)

    damage_state_id = Column(Integer, ForeignKey("damages_state_cases.id"), nullable=True)
    damage_state = relationship("DamageStateCase", back_populates="case", uselist=False)

    state_id = Column(Integer, ForeignKey("states_cases.id"), nullable=True, default=3)#INCOMPLETE default state
    state = relationship("StateCase", back_populates="case", uselist=False)

    #
    """ is_out_time_for_quoting = Column(Boolean, nullable=False, default=False)
    is_excceds_quoting_limit = Column(Boolean, nullable=False, default=False) """

    # Relación uno a muchos con las imágenes
    images = relationship("ImageCase", back_populates="case", cascade="all, delete-orphan")

    # Relación uno a muchos con la cotización
    quote = relationship("QuoteCase", back_populates="case", cascade="all, delete-orphan", uselist=False)

    # Relación uno a muchos con la no participación
    shop_without_participation = relationship("ShopsWithoutParticipationCase", back_populates="case", cascade="all, delete-orphan")

    #fechas de registros:
    sent_client_to_operations_date = Column(DateTime(timezone=True), nullable=True, default=None)
    sent_operations_to_workshop_date = Column(DateTime(timezone=True), nullable=True, default=None)
    approved_date = Column(DateTime(timezone=True), nullable=True, default=None)

    awarded_quote_case = relationship("AwardedQuoteCase", back_populates="case", uselist=False)
    
