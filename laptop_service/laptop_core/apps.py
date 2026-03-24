from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.db.utils import OperationalError, ProgrammingError


def seed_laptop_catalog(sender, **kwargs):
    try:
        from .models import Laptop

        laptop_seed = [
            {'name': 'Dell XPS 13', 'brand': 'Dell', 'price': 1299, 'specs': 'Core Ultra 7, 16GB RAM, 512GB SSD', 'stock': 8},
            {'name': 'Dell Inspiron 14', 'brand': 'Dell', 'price': 899, 'specs': 'Core i7, 16GB RAM, 1TB SSD', 'stock': 15},
            {'name': 'MacBook Air M3', 'brand': 'Apple', 'price': 1249, 'specs': 'M3, 16GB RAM, 512GB SSD', 'stock': 7},
            {'name': 'MacBook Pro 14', 'brand': 'Apple', 'price': 1999, 'specs': 'M3 Pro, 18GB RAM, 1TB SSD', 'stock': 4},
            {'name': 'Asus ROG Zephyrus G14', 'brand': 'Asus', 'price': 1699, 'specs': 'Ryzen 9, RTX 4060, 32GB RAM', 'stock': 6},
            {'name': 'Asus Vivobook S 15', 'brand': 'Asus', 'price': 999, 'specs': 'Core Ultra 5, 16GB RAM, 1TB SSD', 'stock': 12},
            {'name': 'Lenovo ThinkPad X1 Carbon', 'brand': 'Lenovo', 'price': 1499, 'specs': 'Core i7, 16GB RAM, 512GB SSD', 'stock': 9},
            {'name': 'Lenovo Legion 5 Pro', 'brand': 'Lenovo', 'price': 1599, 'specs': 'Ryzen 7, RTX 4070, 32GB RAM', 'stock': 5},
            {'name': 'HP Spectre x360', 'brand': 'HP', 'price': 1399, 'specs': 'Core i7, 16GB RAM, OLED Touch', 'stock': 11},
            {'name': 'Acer Swift Go 14', 'brand': 'Acer', 'price': 849, 'specs': 'Core Ultra 5, 16GB RAM, 512GB SSD', 'stock': 14},
        ]

        for item in laptop_seed:
            Laptop.objects.update_or_create(
                name=item['name'],
                defaults=item,
            )
    except (OperationalError, ProgrammingError):
        return


class LaptopCoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'laptop_core'

    def ready(self):
        post_migrate.connect(seed_laptop_catalog, sender=self, dispatch_uid='laptop_core_seed_catalog')
