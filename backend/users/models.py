from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models

from backend.constants import (MAX_LENGTH_EMAIL, MAX_LENGTH_FIRST_NAME,
                               MAX_LENGTH_LAST_NAME, UPLOAD_PATH_USERS,
                               VERBOSE_NAME_AVATAR, VERBOSE_NAME_EMAIL,
                               VERBOSE_NAME_FIRST_NAME, VERBOSE_NAME_LAST_NAME)


class User(AbstractUser):
    """Модель пользователя."""

    email = models.EmailField(
        VERBOSE_NAME_EMAIL,
        max_length=MAX_LENGTH_EMAIL,
        unique=True,
        null=False
    )
    first_name = models.CharField(
        VERBOSE_NAME_FIRST_NAME,
        max_length=MAX_LENGTH_FIRST_NAME,
    )
    last_name = models.CharField(
        VERBOSE_NAME_LAST_NAME,
        max_length=MAX_LENGTH_LAST_NAME,
    )
    avatar = models.ImageField(
        VERBOSE_NAME_AVATAR,
        upload_to=UPLOAD_PATH_USERS,
        null=True
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def clean(self):
        """Валидация модели."""
        super().clean()
        if self.username.lower() == 'me':
            raise ValidationError({
                'username': 'Имя пользователя "me" не разрешено.'
            })

    def __str__(self):
        """Возвращает строковое представление пользователя."""

        return self.email

    def save(self, *args, **kwargs):
        """Сохранение с предварительной очисткой."""

        self.full_clean()
        super().save(*args, **kwargs)
