from django.contrib.auth.backends import ModelBackend

from .models import user


class EmailBackend(ModelBackend):

    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user_obj = user.objects.get(email=username)
            if user_obj.check_password(password):
                return user_obj
        except user.DoesNotExist:
            return None
        return None
