from django.db import models
from django.db.models.signals import pre_save, post_save, post_delete
from .models import Category, ProductImage, HomeBanner, ProductLike
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver


SESSION_KEY = "liked_product_ids"

def file_fields(model):
    return [
        f for f in model._meta.get_fields()
        if isinstance(f, models.FileField)
    ]


def track_old_files(sender, instance, **kwargs):
    if not instance.pk:
        return

    try:
        old = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return

    instance._old_files_to_delete = {}

    for f in file_fields(sender):
        old_file = getattr(old, f.name, None)
        new_file = getattr(instance, f.name, None)

        old_name = getattr(old_file, "name", "") or ""
        new_name = getattr(new_file, "name", "") or ""

        if old_name and old_name != new_name:
            instance._old_files_to_delete[f.name] = old_name


def delete_tracked_files(sender, instance, created=False, **kwargs):
    old_files = getattr(instance, "_old_files_to_delete", None) or {}
    if not old_files:
        return

    for field_name, old_name in old_files.items():
        field = instance._meta.get_field(field_name)
        storage = field.storage

        still_used = sender.objects.filter(**{field_name: old_name}).exclude(pk=instance.pk).exists()
        if not still_used:
            storage.delete(old_name)

    instance._old_files_to_delete = {}


def delete_current_files(sender, instance, **kwargs):
    for f in file_fields(sender):
        file_obj = getattr(instance, f.name, None)
        name = getattr(file_obj, "name", "") or ""
        if name:
            still_used = sender.objects.filter(**{f.name: name}).exclude(pk=instance.pk).exists()
            if not still_used:
                f.storage.delete(name)


for model_cls in (Category, ProductImage, HomeBanner):
    pre_save.connect(track_old_files, sender=model_cls, weak=False)
    post_save.connect(delete_tracked_files, sender=model_cls, weak=False)
    post_delete.connect(delete_current_files, sender=model_cls, weak=False)


@receiver(user_logged_in)
def merge_session_likes_to_db(sender, request, user, **kwargs):
    ids = request.session.get(SESSION_KEY, [])
    if not ids:
        return

    ids = [int(x) for x in ids if str(x).isdigit()]
    ProductLike.objects.bulk_create(
        [ProductLike(user=user, product_id=pid) for pid in set(ids)],
        ignore_conflicts=True,
    )

    # очистимо session (тепер все в БД)
    request.session.pop(SESSION_KEY, None)
    request.session.modified = True