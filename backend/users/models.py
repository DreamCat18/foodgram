from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models

from backend.constants import (
    MAX_LENGTH_EMAIL,
    MAX_LENGTH_FIRST_NAME,
    MAX_LENGTH_LAST_NAME,
    UPLOAD_PATH_USERS,
    VERBOSE_NAME_AVATAR,
    VERBOSE_NAME_EMAIL,
    VERBOSE_NAME_FIRST_NAME,
    VERBOSE_NAME_LAST_NAME,
    RELATED_NAME_SUBSCRIBERS,
    RELATED_NAME_SUBSCRIPTIONS,
    VERBOSE_NAME_AUTHOR,
    VERBOSE_NAME_USER
)


class Subscription(models.Model):
    """Модель подписки на автора."""

    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name=RELATED_NAME_SUBSCRIPTIONS,
        verbose_name=VERBOSE_NAME_USER
    )
    author = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name=RELATED_NAME_SUBSCRIBERS,
        verbose_name=VERBOSE_NAME_AUTHOR
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_subscription'
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F('author')),
                name='prevent_self_subscription'
            )
        ]

    def __str__(self):
        """Возвращает строковое представление подписки."""
        return f'{self.user} подписан на {self.author}'


class User(AbstractUser):
    """Модель пользователя."""

    email = models.EmailField(
        VERBOSE_NAME_EMAIL,
        max_length=MAX_LENGTH_EMAIL,
        unique=True,
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

    def __str__(self):
        """Возвращает строковое представление пользователя."""
        return self.email

    def clean(self):
        """Валидация модели."""
        super().clean()
        if self.username.lower() == 'me':
            raise ValidationError({
                'username': 'Имя пользователя "me" не разрешено.'
            })
