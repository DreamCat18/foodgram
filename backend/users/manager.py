from django.contrib.auth.base_user import BaseUserManager


class CustomUserManager(BaseUserManager):
    """Кастомный менеджер для модели пользователя.
    """

    def create_user(self, email, username, first_name,
                    last_name, password=None):
        """
        Создает и сохраняет пользователя с email, username,
        first_name, last_name и password.
        """
        if not email:
            raise ValueError('Email должен быть указан')
        if not username:
            raise ValueError('Username должен быть указан')
        user = self.model(
            email=self.normalize_email(email),
            username=username,
            first_name=first_name,
            last_name=last_name,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, first_name,
                         last_name, password=None):
        """
        Создает и сохраняет суперпользователя с email, username,
        first_name, last_name и password.
        """
        user = self.create_user(
            email=email,
            username=username,
            first_name=first_name,
            last_name=last_name,
            password=password,
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user
