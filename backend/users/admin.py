from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import Subscription, UserAdmin

User = get_user_model()


@admin.register(User)
class CustomUserAdmin(UserAdmin):  
    list_display = ('email', 'username', 'first_name', 'last_name', 'is_staff') 
    search_fields = ('email', 'username', 'first_name', 'last_name')
    list_filter = ('is_staff', 'is_active', 'date_joined') 
    ordering = ('email',)
    
    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'author')
    search_fields = (
        'user__username',
        'user__email', 
        'author__username',
        'author__email'
    )
