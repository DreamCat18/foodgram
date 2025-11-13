from django.contrib import admin

from .models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCart, Tag)


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
        return obj.favorites.count()


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    search_fields = ('user__username', 'user__email', 'recipe__name')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    search_fields = ('user__username', 'user__email', 'recipe__name')
