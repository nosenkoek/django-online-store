import datetime

from django.dispatch import receiver
from django.db.models.signals import post_delete


@receiver(post_delete, sender='store.Product')
def foo(sender, instance, **kwargs):
    if instance.name:
        print(instance.name)
