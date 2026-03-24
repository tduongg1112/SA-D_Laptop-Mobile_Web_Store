from django.apps import AppConfig
from django.contrib.auth import get_user_model
from django.db.models.signals import post_migrate
from django.db.utils import OperationalError, ProgrammingError


def seed_customer_user(sender, **kwargs):
    try:
        user_model = get_user_model()
        user, _ = user_model.objects.get_or_create(
            username='customer',
            defaults={'email': 'customer@nova.local'}
        )
        user.set_password('123456')
        user.is_staff = False
        user.is_superuser = False
        user.save()
    except (OperationalError, ProgrammingError):
        return


class CustomerCoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'customer_core'

    def ready(self):
        post_migrate.connect(seed_customer_user, sender=self, dispatch_uid='customer_core_seed_user')
