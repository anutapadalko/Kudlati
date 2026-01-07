from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from parler.models import TranslatableModel, TranslatedFields

# ====== ДОВІДНИКИ, ЯКИМИ МЕНЕДЖИШ ЧЕРЕЗ АДМІНКУ ======

class Category(TranslatableModel):
    translations = TranslatedFields(
        name = models.CharField(_("Назва категорії"), max_length=120),
    )
    slug = models.SlugField(_("Слаг"), max_length=140, unique=True)
    icon = models.ImageField(_("Іконка"), upload_to="categories/icons/", blank=True, null=True)
    is_active = models.BooleanField(_("Активна"), default=True)
    sort_order = models.PositiveIntegerField(_("Порядок"), default=0)

    class Meta:
        verbose_name = _("Категорія")
        verbose_name_plural = _("Категорії")
        ordering = ["sort_order", "slug"]
        indexes = [models.Index(fields=["slug"])]

    def __str__(self):
        return self.safe_translation_getter("name", any_language=True) or self.slug

    # авто-створення перекладів
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self._ensure_all_translations(["name"])

    def _ensure_all_translations(self, fields):
        langs = [code for code, _ in getattr(settings, "LANGUAGES", [("uk","Ukrainian")])]
        base_lang = getattr(settings, "LANGUAGE_CODE", "uk")
        base_val = {f: self.safe_translation_getter(f, language_code=base_lang) for f in fields}
        for code in langs:
            if not self.has_translation(code):
                self.set_current_language(code)
                for f in fields:
                    setattr(self, f, base_val[f] or "")
                super(Category, self).save(update_fields=[])


class ProductType(TranslatableModel):
    """
    Напр.: шампунь / кондиціонер / пінка для лап / мус.
    Через адмінку можна додавати нові. Якщо requires_coat_type=True,
    то у продуктів цього типу coat_type стане обовʼязковим.
    """
    translations = TranslatedFields(
        name = models.CharField(_("Назва типу продукту"), max_length=120),
    )
    slug = models.SlugField(_("Слаг"), max_length=140, unique=True)
    requires_coat_type = models.BooleanField(_("Потрібен тип шерсті?"), default=False)
    is_active = models.BooleanField(_("Активний"), default=True)
    sort_order = models.PositiveIntegerField(_("Порядок"), default=0)

    class Meta:
        verbose_name = _("Тип продукту")
        verbose_name_plural = _("Типи продуктів")
        ordering = ["sort_order", "slug"]

    def __str__(self):
        return self.safe_translation_getter("name", any_language=True) or self.slug

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self._ensure_all_translations(["name"])

    def _ensure_all_translations(self, fields):
        langs = [code for code, _ in getattr(settings, "LANGUAGES", [("uk","Ukrainian")])]
        base_lang = getattr(settings, "LANGUAGE_CODE", "uk")
        base_val = {f: self.safe_translation_getter(f, language_code=base_lang) for f in fields}
        for code in langs:
            if not self.has_translation(code):
                self.set_current_language(code)
                for f in fields:
                    setattr(self, f, base_val[f] or "")
                super(ProductType, self).save(update_fields=[])


class CoatType(TranslatableModel):
    """
    Напр.: гладкошерсті / кудлаті / чутливі. Адмін може додавати свої.
    """
    translations = TranslatedFields(
        name = models.CharField(_("Тип шерсті"), max_length=120),
    )
    is_active = models.BooleanField(_("Активний"), default=True)
    sort_order = models.PositiveIntegerField(_("Порядок"), default=0)

    class Meta:
        verbose_name = _("Тип шерсті")
        verbose_name_plural = _("Типи шерсті")
        ordering = ["sort_order", "id"]

    def __str__(self):
        return self.safe_translation_getter("name", any_language=True) or self.slug

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self._ensure_all_translations(["name"])

    def _ensure_all_translations(self, fields):
        langs = [code for code, _ in getattr(settings, "LANGUAGES", [("uk","Ukrainian")])]
        base_lang = getattr(settings, "LANGUAGE_CODE", "uk")
        base_val = {f: self.safe_translation_getter(f, language_code=base_lang) for f in fields}
        for code in langs:
            if not self.has_translation(code):
                self.set_current_language(code)
                for f in fields:
                    setattr(self, f, base_val[f] or "")
                super(CoatType, self).save(update_fields=[])

# ====== ПРОДУКТ ТА ЗОБРАЖЕННЯ ======

class Product(TranslatableModel):
    translations = TranslatedFields(
        name = models.CharField(_("Назва"), max_length=255),
        description = models.TextField(_("Опис"), blank=True),
    )

    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name="products", verbose_name=_("Категорія")
    )
    product_type = models.ForeignKey(
        ProductType, on_delete=models.PROTECT, related_name="products", verbose_name=_("Тип продукту")
    )
    coat_type = models.ForeignKey(
        CoatType, on_delete=models.PROTECT, related_name="products",
        verbose_name=_("Тип шампуню / шерсті"), blank=True, null=True
    )

    sku = models.CharField(_("SKU"), max_length=64, unique=True)
    volume_ml = models.PositiveIntegerField(_("Об’єм, мл"))

    price = models.DecimalField(_("Ціна"), max_digits=10, decimal_places=2)
    cost_price = models.DecimalField(_("Собівартість"), max_digits=10, decimal_places=2)

    stock_qty = models.PositiveIntegerField(_("Залишки на складі"), default=0)

    batch_code = models.CharField(_("Партія"), max_length=64, blank=True)
    expiry_date = models.DateField(_("Термін придатності"), blank=True, null=True)

    is_active = models.BooleanField(_("Активний"), default=True)
    created_at = models.DateTimeField(_("Створено"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Оновлено"), auto_now=True)

    class Meta:
        verbose_name = _("Продукт")
        verbose_name_plural = _("Продукти")
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["sku"])]

    def __str__(self):
        return f"{self.safe_translation_getter('name', any_language=True)} ({self.sku})"

    def clean(self):
        # coat_type обовʼязковий, якщо product_type.requires_coat_type=True
        if self.product_type and self.product_type.requires_coat_type and not self.coat_type:
            raise ValidationError({"coat_type": _("Для цього типу продукту потрібно обрати тип шерсті.")})

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self._ensure_all_translations(["name", "description"])

    def _ensure_all_translations(self, fields):
        langs = [code for code, _ in getattr(settings, "LANGUAGES", [("uk","Ukrainian")])]
        base_lang = getattr(settings, "LANGUAGE_CODE", "uk")
        base_val = {f: self.safe_translation_getter(f, language_code=base_lang) for f in fields}
        for code in langs:
            if not self.has_translation(code):
                self.set_current_language(code)
                for f in fields:
                    setattr(self, f, base_val[f] or "")
                super(Product, self).save(update_fields=[])


class ProductImage(TranslatableModel):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="images", verbose_name=_("Продукт")
    )
    image = models.ImageField(_("Зображення"), upload_to="products/%Y/%m/")
    translations = TranslatedFields(
        alt = models.CharField(_("ALT текст"), max_length=255, blank=True),
    )
    sort_order = models.PositiveIntegerField(_("Порядок"), default=0)
    is_main = models.BooleanField(_("Головне"), default=False, help_text=_("Головне зображення"))

    class Meta:
        verbose_name = _("Зображення продукту")
        verbose_name_plural = _("Зображення продукту")
        ordering = ["sort_order", "id"]

    def __str__(self):
        return f"{self.product} [{self.id}]"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self._ensure_all_translations(["alt"])

    def _ensure_all_translations(self, fields):
        langs = [code for code, _ in getattr(settings, "LANGUAGES", [("uk","Ukrainian")])]
        base_lang = getattr(settings, "LANGUAGE_CODE", "uk")
        base_val = {f: self.safe_translation_getter(f, language_code=base_lang) for f in fields}
        for code in langs:
            if not self.has_translation(code):
                self.set_current_language(code)
                for f in fields:
                    setattr(self, f, base_val[f] or "")
                super(ProductImage, self).save(update_fields=[])
