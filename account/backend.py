import datetime
from django.conf import settings
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

from .models import InviteKey, PhoneToken


class AccountBackend(ModelBackend):
    def __init__(self, *args, **kwargs):
        self.user_model = get_user_model()

    def create_user(self, phone_token, **extra_fields):
        """Create and return user based on the phone token"""
        password = self.user_model.objects.make_random_password()
        password = extra_fields.get("password", password)

        kwargs = {
            "username": phone_token.phone_number,
            "password": password,
            "phone_number": phone_token.phone_number,
        }
        user = self.user_model.objects.create_user(**kwargs)
        return user

    def authenticate(self, request, phone_number, otp=None, **extra_fields):
        """Verify PhoneToken and create InviteKey"""
        if not otp:
            return

        timestamp_difference = datetime.datetime.now() - datetime.timedelta(
            minutes=getattr(settings, "ACCOUNT_INVITEKEY_LIFE", 5)
        )

        try:
            phone_token = PhoneToken.objects.get(
                phone_number=phone_number,
                otp=otp,
                used=False,
            )
        except PhoneToken.DoesNotExist:
            return print("PhoneToken does not exist")

        user = self.user_model.objects.filter(
            phone_number=phone_token.phone_number
        ).first()

        if not user:
            user = self.create_user(phone_token=phone_token, **extra_fields)
            InviteKey.create_invitekey_for_number(user)

        phone_token.user = True
        phone_token.save()

        return user
