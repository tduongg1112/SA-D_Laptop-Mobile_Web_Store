from django.apps import AppConfig
from django.contrib.auth import get_user_model
from django.db.models.signals import post_migrate
from django.db.utils import OperationalError, ProgrammingError


def seed_staff_user(sender, **kwargs):
    try:
        user_model = get_user_model()
        user, _ = user_model.objects.get_or_create(
            username='staff',
            defaults={'email': 'staff@nova.local'}
        )
        user.set_password('123456')
        user.is_staff = True
        user.is_superuser = False
        user.save()
    except (OperationalError, ProgrammingError):
        return


class StaffCoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'staff_core'

    def ready(self):
        post_migrate.connect(seed_staff_user, sender=self, dispatch_uid='staff_core_seed_user')
