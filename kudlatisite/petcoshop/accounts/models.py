from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.contrib.postgres.fields import ArrayField
from django.core.validators import MinValueValidator, MaxValueValidator


class UserRole(models.TextChoices):
    CUSTOMER = "customer", "B2C клієнт"
    B2B      = "b2b",      "B2B контакт"
    STAFF    = "staff",    "Персонал/адмін"


class User(AbstractUser):
    email = models.EmailField(unique=True)
    role  = models.CharField(max_length=16, choices=UserRole.choices, default=UserRole.CUSTOMER)

    # Якщо хочете логінитися e-mail’ом (а не username), можна пізніше
    # перейти на AbstractBaseUser. Поки що зручніше залишити AbstractUser.

    def __str__(self) -> str:
        return self.username or self.email


# ---- B2C (звичайний клієнт) --------------------------------------------------

class AcquisitionChannel(models.TextChoices):
    SITE        = "site",        "Сайт"
    INSTAGRAM   = "instagram",   "Instagram"
    MARKETPLACE = "marketplace", "Маркетплейс"
    TIKTOK      = "tiktok",      "TikTok"
    OTHER       = "other",       "Інше"


class CustomerStatus(models.TextChoices):
    NEW        = "new",        "Новий"        # перша покупка за останні 30 днів
    REPEATING  = "repeating",  "Повторний"    # 2+ покупки
    OLD        = "old",        "Старий"       # відсутні покупки > 90 днів


class CustomerProfile(models.Model):
    """
    Картка B2C-клієнта (один до одного з User)
    Поля з ТЗ:
    - Ім’я, Прізвище, Email, Телефон
    - Адреса (для доставки)
    - Канал залучення
    - Теги (ArrayField, бо Postgres)
    - Нотатки
    - Статус клієнта (автообчислення пізніше; тимчасово збережемо поле)
    - Остання покупка / Загальна сума (для відображення картки)
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="customer_profile")

    first_name = models.CharField(max_length=120, blank=True)
    last_name  = models.CharField(max_length=120, blank=True)
    email      = models.EmailField(blank=True)     # дублюємо для зручності CRM-вигрузок
    phone      = models.CharField(max_length=32, blank=True)

    delivery_address = models.TextField(blank=True)

    acquisition_channel = models.CharField(
        max_length=16, choices=AcquisitionChannel.choices, default=AcquisitionChannel.SITE
    )

    tags = ArrayField(models.CharField(max_length=32), blank=True, default=list)  # напр.: ["new_client","UGC","B2B"]

    notes = models.TextField(blank=True)  # відгуки, UGC-активність, амбасадорство

    customer_status = models.CharField(
        max_length=16, choices=CustomerStatus.choices, default=CustomerStatus.NEW
    )

    # поля для зручного відображення картки
    last_purchase_at = models.DateTimeField(null=True, blank=True)
    total_spent      = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Клієнт (B2C)"
        verbose_name_plural = "Клієнти (B2C)"

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}".strip() or self.user.email

    # TODO: коли зʼявляться замовлення — оновлювати customer_status автоматично (сигнал/сервісом)
    # NEW: перша покупка за останні 30 днів
    # REPEATING: 2+ покупки
    # OLD: немає покупок > 90 днів


# ---- B2B (компанії/контакти) -------------------------------------------------

class B2BClientType(models.TextChoices):
    VET_CLINIC   = "vet_clinic",   "Ветклініка"
    GROOMING     = "grooming",     "Грумінг-салон"
    SHOP         = "shop",         "Магазин"
    DISTRIBUTOR  = "distributor",  "Дистриб’ютор"


class PaymentTerms(models.TextChoices):
    PREPAID_100     = "prepaid_100",     "Передплата 100%"
    NET_7           = "net_7",           "Відтермінування 7 днів"
    NET_14          = "net_14",          "Відтермінування 14 днів"
    NET_30          = "net_30",          "Відтермінування 30 днів"


class DeliveryTerms(models.TextChoices):
    NOVA_POSHTA = "nova_poshta", "Нова Пошта"
    COURIER     = "courier",     "Кур’єр"
    PICKUP      = "pickup",      "Самовивіз"


class B2BStatus(models.TextChoices):
    ACTIVE   = "active",   "Активний"
    INACTIVE = "inactive", "Неактивний"


class B2BProfile(models.Model):
    """
    Картка B2B-клієнта (контакт = User з role=b2b).
    За потреби пізніше можна винести Company як окрему сутність і зв’язати багато контактів.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="b2b_profile")

    # Компанія
    company_name = models.CharField(max_length=255)
    contact_first_name = models.CharField(max_length=120, blank=True)
    contact_last_name  = models.CharField(max_length=120, blank=True)
    email   = models.EmailField(blank=True)   # може відрізнятись від user.email
    phone   = models.CharField(max_length=32, blank=True)

    legal_address     = models.TextField(blank=True)  # юридична
    actual_address    = models.TextField(blank=True)  # фактична

    edrpou_or_ipn = models.CharField(max_length=32, blank=True)  # опціонально

    client_type = models.CharField(max_length=16, choices=B2BClientType.choices)

    min_order_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)  # підтягнеться з умов B2B

    payment_terms = models.CharField(max_length=16, choices=PaymentTerms.choices, default=PaymentTerms.PREPAID_100)
    delivery_terms = models.CharField(max_length=16, choices=DeliveryTerms.choices, default=DeliveryTerms.NOVA_POSHTA)

    # знижки: або відсоток, або спец-ціна по SKU (мапу збережемо в JSON)
    individual_discount_percent = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    special_prices_by_sku = models.JSONField(null=True, blank=True)  # {"SKU123": "199.00", "SKU456": "149.00"}

    contracts_link = models.URLField(blank=True)    # файл/посилання — поки залишимо посиланням
    notes          = models.TextField(blank=True)

    # Для відображення картки
    last_order_at = models.DateTimeField(null=True, blank=True)
    customer_status = models.CharField(max_length=16, choices=B2BStatus.choices, default=B2BStatus.ACTIVE)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "B2B клієнт"
        verbose_name_plural = "B2B клієнти"

    def __str__(self) -> str:
        return f"{self.company_name} ({self.email or self.user.email})"