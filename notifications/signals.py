import logging

from django.db.models.signals import post_save, pre_save

from .services import send_later

logger = logging.getLogger(__name__)

PRODUCT_LABELS = (
    'accessories.AccessoriesProduct',
    'birthday.BirthdayProduct',
    'foods.FoodsProduct',
    'fruitsandvegetables.FavProduct',
    'gifts.GiftsProduct',
    'pharmacy.PharmacyProduct',
    'phones.PhonesProduct',
    'products.LibraryProduct',
    'shein.SheinProduct',
    'socks.SocksProduct',
    'spices.SpicesProduct',
    'supermarket.SupermarketProduct',
    'toys.ToysProduct',
    'veils.VeilsProduct',
)


def _number(value):
    if value is None:
        return 0.0
    return float(value)


def remember_discount(sender, instance, update_fields=None, **kwargs):
    if update_fields is not None and 'discount_percentage' not in update_fields:
        instance._previous_discount = _number(instance.discount_percentage)
        return
    instance._previous_discount = None
    if not instance.pk:
        return
    try:
        previous = sender.objects.filter(pk=instance.pk).values_list(
            'discount_percentage', flat=True
        ).first()
        instance._previous_discount = _number(previous)
    except Exception:
        logger.exception('Could not read the previous discount for %s', instance.pk)


def notify_product(sender, instance, created, update_fields=None, **kwargs):
    if (
        not created
        and update_fields is not None
        and 'discount_percentage' not in update_fields
    ):
        return
    try:
        name = instance.name
        discount = _number(instance.discount_percentage)
        previous = getattr(instance, '_previous_discount', None)
        percent = f'{discount:g}'
        if created and discount > 0:
            send_later(
                ['customers', 'staff'],
                'خصم جديد',
                f'{name} عليه خصم {percent}%',
                {'type': 'discount', 'product_id': instance.pk, 'model_name': instance.model_name},
            )
            return
        if created:
            send_later(
                ['customers'],
                'منتج جديد',
                name,
                {'type': 'product', 'product_id': instance.pk, 'model_name': instance.model_name},
            )
            return
        if previous is not None and discount > previous and discount > 0:
            send_later(
                ['customers', 'staff'],
                'خصم جديد',
                f'{name} عليه خصم {percent}%',
                {'type': 'discount', 'product_id': instance.pk, 'model_name': instance.model_name},
            )
    except Exception:
        logger.exception('Could not prepare a product notification')


def notify_offer(sender, instance, created, **kwargs):
    if not created:
        return
    try:
        send_later(
            ['customers'],
            'عرض جديد',
            instance.title or 'عرض جديد',
            {'type': 'offer', 'offer_id': instance.pk},
        )
    except Exception:
        logger.exception('Could not prepare an offer notification')


def connect_signals():
    from django.apps import apps
    from offerspaner.models import Image, TopBannerImage

    for label in PRODUCT_LABELS:
        model = apps.get_model(label)
        pre_save.connect(remember_discount, sender=model, dispatch_uid=f'discount-{label}')
        post_save.connect(notify_product, sender=model, dispatch_uid=f'product-{label}')

    post_save.connect(notify_offer, sender=Image, dispatch_uid='offer-image')
    post_save.connect(notify_offer, sender=TopBannerImage, dispatch_uid='offer-banner')
