from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model

User = get_user_model()


@receiver(post_save, sender=User)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    """
    为新创建的用户自动创建Token
    """
    if created:
        # 如果settings中配置了rest_framework.authtoken
        if 'rest_framework.authtoken' in settings.INSTALLED_APPS:
            Token.objects.create(user=instance) 