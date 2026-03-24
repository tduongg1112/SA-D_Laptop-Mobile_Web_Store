from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.db.utils import OperationalError, ProgrammingError


def seed_mobile_catalog(sender, **kwargs):
    try:
        from .models import Mobile

        mobile_seed = [
            {'name': 'iPhone 15', 'brand': 'Apple', 'price': 899, 'specs': '128GB, A16 Bionic', 'stock': 16},
            {'name': 'iPhone 15 Pro', 'brand': 'Apple', 'price': 1099, 'specs': '256GB, A17 Pro', 'stock': 10},
            {'name': 'Samsung Galaxy S24', 'brand': 'Samsung', 'price': 849, 'specs': '256GB, Snapdragon 8 Gen 3', 'stock': 14},
            {'name': 'Samsung Galaxy Z Flip5', 'brand': 'Samsung', 'price': 999, 'specs': '256GB, Foldable Display', 'stock': 9},
            {'name': 'Google Pixel 8', 'brand': 'Google', 'price': 699, 'specs': '128GB, Tensor G3', 'stock': 13},
            {'name': 'Google Pixel 8 Pro', 'brand': 'Google', 'price': 999, 'specs': '256GB, Tensor G3', 'stock': 8},
            {'name': 'Xiaomi 14', 'brand': 'Xiaomi', 'price': 679, 'specs': '256GB, Snapdragon 8 Gen 3', 'stock': 20},
            {'name': 'Xiaomi 14 Ultra', 'brand': 'Xiaomi', 'price': 1099, 'specs': '512GB, Leica Camera System', 'stock': 6},
            {'name': 'OnePlus 12', 'brand': 'OnePlus', 'price': 799, 'specs': '256GB, 100W Fast Charge', 'stock': 11},
            {'name': 'Nothing Phone 2', 'brand': 'Nothing', 'price': 599, 'specs': '256GB, Glyph Interface', 'stock': 18},
        ]

        for item in mobile_seed:
            Mobile.objects.update_or_create(
                name=item['name'],
                defaults=item,
            )
    except (OperationalError, ProgrammingError):
        return


class MobileCoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mobile_core'

    def ready(self):
        post_migrate.connect(seed_mobile_catalog, sender=self, dispatch_uid='mobile_core_seed_catalog')
