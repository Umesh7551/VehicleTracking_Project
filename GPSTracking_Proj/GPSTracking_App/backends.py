# backends.py

from django.contrib.auth import get_user_model
from django.contrib.auth.models import User

from .models import FleetOwner


class EmailBackend(object):
    def authenticate(self, request, email=None, password=None):
        user = get_user_model()
        try:
            user = User.objects.get(email=email)
            print(user)
            if user.check_password(password):
                print("User authenticated successfully:", user)
                return user
            else:
                print("Password incorrect for user:", user)
        except user.DoesNotExist:
            print("User not found with email:", email)
        return None

    def get_user(self, user_id):
        FleetOwner = get_user_model()
        try:
            return FleetOwner.objects.get(pk=user_id)
        except FleetOwner.DoesNotExist:
            return None