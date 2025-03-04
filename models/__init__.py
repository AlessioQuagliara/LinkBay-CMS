
# 📌 Prima importiamo le tabelle fondamentali (User e ShopList) per evitare errori di riferimento
from .user import User
from .shoplist import ShopList

# 📌 Tabelle collegate agli utenti e ai negozi
from .userstoreaccess import UserStoreAccess
from .websettings import WebSettings
from .cookiepolicy import CookiePolicy
from .subscription import Subscription

# 📌 Tabelle delle agenzie e dipendenti
from .agency import Agency
from .userstoreaccess import UserStoreAccess
from .agency import AgencyStoreAccess
from .agency import AgencyEmployee

# 📌 Tabelle delle opportunità di lavoro
from .opportunities import Opportunity
from .opportunities import AgencyOpportunity
from .opportunities import OpportunityMessage

# 📌 Tabelle relative ai negozi e ai servizi
from .stores_info import StoreInfo
from .domain import Domain
from .site_visits import SiteVisit
from .site_visit_intern import SiteVisitIntern
from .storepayment import StorePayment

# 📌 Tabelle relative alla gestione delle categorie e prodotti
from .categories import Category
from .products import Brand
from .products import ProductImage
from .products import ProductAttribute
from .products import Product
from .collections import Collection
from .collections import CollectionImage
from .collections import CollectionProduct

# 📌 Tabelle per gli ordini e pagamenti
from .orders import Order
from .orders import OrderItem
from .payments import Payment
from .payment_methods import PaymentMethod

# 📌 Tabelle relative alla gestione della spedizione
from .shipping import Shipping
from .shippingmethods import ShippingMethod

# 📌 Tabelle per le pagine e il contenuto del CMS
from .page import Page
from .navbar import NavbarLink
from .cmsaddon import CMSAddon
from .cmsaddon import ShopAddon

# 📌 Tabelle per suggerimenti di miglioramento e contatti
from .improvement_suggestion import ImprovementSuggestion
from .contacts import Contact

# 📌 Tabelle per la gestione delle email, ticket di supporto e messaggi
from .support_tickets import SupportTicket
from .ticket_messages import TicketMessage

# 📌 Tabelle per i superadmin
from .superadmin_models import SuperAdmin
from .superadmin_models import SuperPages
from .superadmin_models import SuperMedia
from .superadmin_models import SuperInvoice
from .superadmin_models import SuperMessages
from .superadmin_models import SuperSupport
