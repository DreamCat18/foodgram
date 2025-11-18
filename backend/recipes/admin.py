from django import forms
from django.contrib import admin

from .models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCart, Tag)


class FavoriteForm(forms.ModelForm):
    """Форма для избранного с валидацией."""

    class Meta:
        model = Favorite
        fields = '__all__'

    def clean(self):
        """Валидирует данные формы."""
        cleaned_data = super().clean()
        user = cleaned_data.get('user')
        recipe = cleaned_data.get('recipe')
        if user and recipe and Favorite.objects.filter(
            user=user, recipe=recipe
        ).exists():
            raise forms.ValidationError(
                'Этот рецепт уже добавлен в избранное.'
            )
        return cleaned_data


class ShoppingCartForm(forms.ModelForm):
    """Форма для корзины с валидацией."""

    class Meta:
        model = ShoppingCart
        fields = '__all__'

    def clean(self):
        """Валидирует данные формы."""
        cleaned_data = super().clean()
        user = cleaned_data.get('user')
        recipe = cleaned_data.get('recipe')
        if user and recipe and ShoppingCart.objects.filter(
            user=user, recipe=recipe
        ).exists():
            raise forms.ValidationError(
                'Этот рецепт уже добавлен в корзину.'
            )
        return cleaned_data


class RecipeIngredientInline(admin.TabularInline):
    """Inline для добавления ингредиентов в рецепт."""
    model = RecipeIngredient
    extra = 1
    min_num = 1


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)
    list_filter = ('measurement_unit',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'cooking_time', 'favorites_count')
    search_fields = ('name', 'author__username', 'author__email')
    list_filter = ('tags', 'cooking_time')
    readonly_fields = ('favorites_count',)
    inlines = (RecipeIngredientInline,)

    @admin.display(description='Количество добавлений в избранное')
    def favorites_count(self, obj):
        return obj.favorite_set.count()


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    form = FavoriteForm
    list_display = ('user', 'recipe')
    search_fields = ('user__username', 'user__email', 'recipe__name')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    form = ShoppingCartForm
    list_display = ('user', 'recipe')
    search_fields = ('user__username', 'user__email', 'recipe__name')
