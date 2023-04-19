import random

from django.conf import settings
from django.core.mail import send_mail

from reviews.models import User


CONFIRMATION_CODE = random.randint(1000, 9999)


def send_massege(user):
    """
    Оптправляет на почту сообщение с генерированым ключом.
    присваивает ключ к юзеру
    """

    email_message = f'Your confirmation code is: {CONFIRMATION_CODE}'
    send_mail(
        'Confirmation Code',
        email_message,
        settings.EMAIL_HOST_USER,
        [user.email],
        fail_silently=False,
    )
    user.key = CONFIRMATION_CODE
    user.save()


def get_users(data):
    """
    возвращает два оюъекта типа User:

    -фильтрованый по email;

    -фильтрованый по username;
    """

    user_filter_name = User.objects.filter(
        username=data.get('username')).first()
    user_filter_email = User.objects.filter(
        email=data.get('email')).first()

    return (user_filter_name, user_filter_email)
