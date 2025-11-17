from django import forms
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from users.models import Subscription

User = get_user_model()


class SubscriptionForm(forms.ModelForm):
    """Форма для подписки с валидацией."""

    class Meta:
        model = Subscription
        fields = '__all__'

    def clean(self):
        """Валидирует данные формы."""
        cleaned_data = super().clean()
        user = cleaned_data.get('user')
        author = cleaned_data.get('author')
        if user and author and user == author:
            raise forms.ValidationError(
                'Нельзя подписаться на самого себя.'
            )
        return cleaned_data


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    list_display = ('email', 'username', 'first_name', 'last_name', 'is_staff')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    list_filter = ('is_staff', 'is_active', 'date_joined')
    ordering = ('email',)


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    form = SubscriptionForm
    list_display = ('user', 'author')
    search_fields = (
        'user__username',
        'user__email',
        'author__username',
        'author__email'
    )
