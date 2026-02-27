from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from parler.models import TranslatableModel, TranslatedFields
from .mixins import EnsureTranslationsMixin
from django.utils import timezone
from django.db.models import Q
from parler.managers import TranslatableQuerySet, TranslatableManager
from django.conf import settings

class BaseModel(EnsureTranslationsMixin, TranslatableModel):
    class Meta:
        abstract = True

class Category(BaseModel):
    translations = TranslatedFields(
        name=models.CharField(_("Category name"), max_length=120),
    )

    slug = models.SlugField(_("Slug"), max_length=140, unique=True)
    icon = models.ImageField(_("Icon"), upload_to="categories/icons/", blank=True, null=True)
    is_active = models.BooleanField(_("Active"), default=True)
    sort_order = models.PositiveIntegerField(_("Sort order"), default=0)

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")
        ordering = ["sort_order", "slug"]
        indexes = [models.Index(fields=["slug"])]

    def __str__(self):
        return self.safe_translation_getter("name", any_language=True) or f"Category #{self.id}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.ensure_all_translations(["name"])


class ProductType(BaseModel):
    """
    If requires_coat_type=True then coat_type for products becomes required.
    """
    translations = TranslatedFields(
        name=models.CharField(_("Product type name"), max_length=120),
    )

    slug = models.SlugField(_("Slug"), max_length=140, unique=True)
    requires_coat_type = models.BooleanField(_("Requires coat type"), default=False)
    is_active = models.BooleanField(_("Active"), default=True)
    sort_order = models.PositiveIntegerField(_("Sort order"), default=0)

    class Meta:
        verbose_name = _("Product type")
        verbose_name_plural = _("Product types")
        ordering = ["sort_order", "slug"]

    def __str__(self):
        return self.safe_translation_getter("name", any_language=True) or f"ProductType #{self.id}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.ensure_all_translations(["name"])


class CoatType(BaseModel):
    translations = TranslatedFields(
        name=models.CharField(_("Coat type name"), max_length=120),
    )

    is_active = models.BooleanField(_("Active"), default=True)
    sort_order = models.PositiveIntegerField(_("Sort order"), default=0)

    class Meta:
        verbose_name = _("Coat type")
        verbose_name_plural = _("Coat types")
        ordering = ["sort_order", "id"]

    def __str__(self):
        return self.safe_translation_getter("name", any_language=True) or f"CoatType #{self.id}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.ensure_all_translations(["name"])


class Product(BaseModel):
    translations = TranslatedFields(
        name=models.CharField(_("Product name"), max_length=255),
        description=models.TextField(_("Description"), blank=True),
    )

    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name="products", verbose_name=_("Category")
    )
    product_type = models.ForeignKey(
        ProductType, on_delete=models.PROTECT, related_name="products", verbose_name=_("Product type")
    )
    coat_type = models.ForeignKey(
        CoatType,
        on_delete=models.PROTECT,
        related_name="products",
        blank=True,
        null=True,
        verbose_name=_("Coat type"),
    )

    article = models.CharField(_("Article"), max_length=64, unique=True, null=True, blank=True)
    volume_ml = models.PositiveIntegerField(_("Volume (ml)"))

    price = models.DecimalField(_("Price"), max_digits=10, decimal_places=2)
    cost_price = models.DecimalField(_("Cost price"), max_digits=10, decimal_places=2)

    stock_qty = models.PositiveIntegerField(_("Stock quantity"), default=0)

    batch_code = models.CharField(_("Batch code"), max_length=64, blank=True)
    expiry_date = models.DateField(_("Expiry date"), blank=True, null=True)

    is_active = models.BooleanField(_("Active"), default=True)
    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated at"), auto_now=True)

    class Meta:
        verbose_name = _("Product")
        verbose_name_plural = _("Products")
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["article"])]

    def __str__(self):
        name = self.safe_translation_getter("name", any_language=True) or "Product"
        return f"{name} ({self.article})"

    def clean(self):
        if self.product_type and self.product_type.requires_coat_type and not self.coat_type:
            raise ValidationError({"coat_type": _("Coat type is required for this product type.")})

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.ensure_all_translations(["name", "description"])

    def get_active_promotion(self, at=None):
        at = at or timezone.now()
        return (
            self.promotions.active(at=at)
            .order_by("-priority", "-discount_percent", "id")
            .first()
        )

    def get_discount_percent(self):
        promo = self.get_active_promotion()
        return promo.discount_percent if promo else 0

    def get_sale_price(self):
        percent = self.get_discount_percent()
        if percent > 0:
            discount_amount = (self.price * percent) / 100
            return self.price - discount_amount
        return self.price


class ProductImage(BaseModel):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="images", verbose_name=_("Product")
    )
    image = models.ImageField(_("Image"), upload_to="products/%Y/%m/")
    translations = TranslatedFields(
        alt=models.CharField(_("Alt text"), max_length=255, blank=True),
    )

    sort_order = models.PositiveIntegerField(_("Sort order"), default=0)
    is_main = models.BooleanField(_("Is main"), default=False)

    class Meta:
        verbose_name = _("Product image")
        verbose_name_plural = _("Product images")
        ordering = ["sort_order", "id"]

    def __str__(self):
        return f"{self.product} [{self.id}]"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.ensure_all_translations(["alt"])


class HomeBanner(BaseModel):
    translations = TranslatedFields(
        title=models.CharField(_("Title"), max_length=200, blank=True),
    )
    image = models.ImageField(_("Image"), upload_to="home_slides/")
    link = models.URLField(_("Link"), blank=True)
    order = models.PositiveIntegerField(_("Order"), default=0)
    is_active = models.BooleanField(_("Active"), default=True)

    class Meta:
        verbose_name = _("Home banner")
        verbose_name_plural = _("Home banners")
        ordering = ["order", "id"]

    def __str__(self):
        return self.safe_translation_getter("title", any_language=True) or f"Banner #{self.id}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.ensure_all_translations(["title"])


class ShopAddress(BaseModel):
    translations = TranslatedFields(
        title=models.CharField(_("Title"), max_length=120, blank=True),
        address=models.CharField(_("Address"), max_length=255),
        work_hours=models.CharField(_("Working hours"), max_length=120, blank=True),
    )

    phone = models.CharField(_("Phone"), max_length=64, blank=True)
    email = models.EmailField(_("Email"), blank=True)
    map_link = models.URLField(_("Map link"), blank=True)

    order = models.PositiveIntegerField(_("Order"), default=0)
    is_active = models.BooleanField(_("Active"), default=True)

    class Meta:
        verbose_name = _("Shop address")
        verbose_name_plural = _("Shop addresses")
        ordering = ["order", "id"]

    def __str__(self):
        return (
            self.safe_translation_getter("title", any_language=True)
            or self.safe_translation_getter("address", any_language=True)
            or f"ShopAddress #{self.id}"
        )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.ensure_all_translations(["title", "address", "work_hours"])


class PromotionQuerySet(TranslatableQuerySet):
    def active(self, at=None):
        at = at or timezone.now()
        return self.filter(is_active=True).filter(
            Q(starts_at__isnull=True) | Q(starts_at__lte=at),
            Q(ends_at__isnull=True) | Q(ends_at__gte=at),
        )

class Promotion(BaseModel):
    translations = TranslatedFields(
        title=models.CharField(_("Title"), max_length=200),
        badge=models.CharField(_("Badge text"), max_length=50, blank=True),
    )

    slug = models.SlugField(_("Slug"), max_length=140, unique=True)
    discount_percent = models.PositiveIntegerField(_("Discount percent"), default=0)

    starts_at = models.DateTimeField(_("Starts at"), blank=True, null=True)
    ends_at = models.DateTimeField(_("Ends at"), blank=True, null=True)

    priority = models.PositiveIntegerField(_("Priority"), default=0)
    is_active = models.BooleanField(_("Active"), default=True)

    products = models.ManyToManyField(
        "catalog.Product",
        related_name="promotions",
        blank=True,
        verbose_name=_("Products"),
    )

    objects = TranslatableManager.from_queryset(PromotionQuerySet)()

    class Meta:
        verbose_name = _("Promotion")
        verbose_name_plural = _("Promotions")

class ProductLike(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="product_likes",
    )
    product = models.ForeignKey(
        "catalog.Product",
        on_delete=models.CASCADE,
        related_name="likes",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (("user", "product"),)
        indexes = [
            models.Index(fields=["user", "product"]),
            models.Index(fields=["product"]),
        ]

    def __str__(self):
        return f"{self.user} ❤ {self.product}"