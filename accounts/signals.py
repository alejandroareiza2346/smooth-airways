from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.sites.models import Site
from django.conf import settings

@receiver(post_migrate)
def create_default_site(sender, **kwargs):
    """
    Crea el sitio por defecto después de que todas las migraciones se hayan aplicado
    """
    if Site.objects.count() == 0:
        # Crear el sitio por defecto
        Site.objects.create(
            id=settings.SITE_ID,
            domain=settings.SITE_DOMAIN,
            name=settings.SITE_NAME
        ) 