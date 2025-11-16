import django_filters as filters
from django.contrib.auth import get_user_model
from django_filters.rest_framework import FilterSet
from recipes.models import Ingredient, Recipe, Tag

User = get_user_model()


class IngredientFilter(FilterSet):
    """Фильтр для ингредиентов."""

    name = filters.CharFilter(
        field_name='name',
        lookup_expr='istartswith'
    )

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(FilterSet):
    """Фильтр для рецептов."""

    tags = filters.MultipleChoiceFilter(
        field_name='tags__slug',
        choices=lambda: [(tag.slug, tag.slug) for tag in Tag.objects.all()],
        conjoined=False
    )
    author = filters.ModelChoiceFilter(
        queryset=User.objects.all()
    )
    is_favorited = filters.CharFilter(
        method='filter_is_favorited'
    )
    is_in_shopping_cart = filters.CharFilter(
        method='filter_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_favorited', 'is_in_shopping_cart')

    def filter_is_favorited(self, queryset, name, value):
        """Фильтрует рецепты по избранному."""
        if value == '1' and self.request.user.is_authenticated:
            return queryset.filter(favorite__user=self.request.user)
        elif value == '1' and not self.request.user.is_authenticated:
            return queryset.none()
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        """Фильтрует рецепты по списку покупок."""
        if value == '1' and self.request.user.is_authenticated:
            return queryset.filter(shoppingcart__user=self.request.user)
        elif value == '1' and not self.request.user.is_authenticated:
            return queryset.none()
        return queryset
