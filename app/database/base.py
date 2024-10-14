from .base_class import Base

from app.API.v1.modules.notifications import Notification, NotificationType, SeenBy
from app.API.v1.modules.regions import Region, Commune
from app.API.v1.modules.brands import Brand, Model
from app.API.v1.modules.users import User, Role, AcceptedTerms
from app.API.v1.modules.workshops import Workshop
from app.API.v1.modules.cases import Case, ContactCase, CarCase, DamageStateCase, StateCase, ImageCase, QuoteCase, QuoteItemCase, QuoteShopCase, NoParticipationMotive, ShopsWithoutParticipationCase, PaymentMethodsCase, AcceptedTermsQuoteCase, StatusQuoteCase, AwardedQuoteCase