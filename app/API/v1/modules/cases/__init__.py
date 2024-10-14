from .model import Case, ContactCase, CarCase, DamageStateCase, StateCase, ImageCase, QuoteCase, QuoteItemCase, QuoteShopCase, NoParticipationMotive, ShopsWithoutParticipationCase, PaymentMethodsCase, AcceptedTermsQuoteCase, StatusQuoteCase, AwardedQuoteCase
from .routes_clients import router as cases_router_client
from .routes_operarations import router as cases_router_operations
from .routes_workshops import router as cases_router_workshops