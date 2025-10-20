from django.contrib.auth.models import AbstractUser
from django.db import models

from backend.constants import (
    MAX_LENGTH_FIRST_NAME,
    MAX_LENGTH_LAST_NAME,
    MAX_LENGTH_EMAIL,
    UPLOAD_PATH_USERS,
    VERBOSE_NAME_EMAIL,
    VERBOSE_NAME_AVATAR,
    VERBOSE_NAME_FIRST_NAME,
    VERBOSE_NAME_LAST_NAME,
)


class CustomUser(AbstractUser):
    """Модель пользователя."""

    email = models.EmailField(
        VERBOSE_NAME_EMAIL,
        max_length=MAX_LENGTH_EMAIL,
        unique=True,
        blank=False,
        null=False
    )
    first_name = models.CharField(
        VERBOSE_NAME_FIRST_NAME,
        max_length=MAX_LENGTH_FIRST_NAME,
        blank=True
    )
    last_name = models.CharField(
        VERBOSE_NAME_LAST_NAME,
        max_length=MAX_LENGTH_LAST_NAME,
        blank=True
    )
    avatar = models.ImageField(
        VERBOSE_NAME_AVATAR,
        upload_to=UPLOAD_PATH_USERS,
        blank=True,
        null=True
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        """Возвращает строковое представление пользователя."""
        return self.username
