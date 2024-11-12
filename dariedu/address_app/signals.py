from django.dispatch import receiver
from django.core.exceptions import ValidationError
from django.db.models.signals import pre_save

from .models import Beneficiar


def get_phone_number(phone: str) -> str:
    if phone.startswith('+7'):
        phone = phone.replace('+7', '8', 1)
    elif phone.startswith('7'):
        phone = phone.replace('7', '8', 1)

    phone = ''.join(filter(str.isdigit, phone))

    if len(phone) != 11:
        raise ValidationError(message='Не правильный формат телефона')

    return phone


@receiver(signal=pre_save, sender=Beneficiar)
def beneficiary_pre_save(sender, instance: Beneficiar, **kwargs):
    if instance.phone:
        instance.phone = get_phone_number(instance.phone)
    if instance.second_phone:
        instance.second_phone = get_phone_number(instance.second_phone)
