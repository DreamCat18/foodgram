import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from backend.constants import MIN_VALUE_AMOUNT

from recipes.models import (
    Favorite, Ingredient, Recipe, RecipeIngredient,
    ShoppingCart, Subscription, Tag
)

User = get_user_model()


class Base64ImageField(serializers.ImageField):
    """Преобразует base64 строку в файл изображения."""

    def to_internal_value(self, data):

        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class CustomUserSerializer(serializers.ModelSerializer):
    """Сериализатор для пользователя."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribed', 'avatar'
        )
        read_only_fields = ('id', 'is_subscribed')

    def get_is_subscribed(self, obj):
        """Проверяет, подписан ли текущий пользователь на данного."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Subscription.objects.filter(
                user=request.user, author=obj
            ).exists()
        return False


class CustomUserCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания пользователя."""

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'password'
        )
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        """Создает нового пользователя."""
        user = User.objects.create_user(**validated_data)
        return user


class SetAvatarSerializer(serializers.ModelSerializer):
    """Сериализатор для установки аватара."""

    avatar = Base64ImageField()

    class Meta:
        model = User
        fields = ('avatar',)


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для тега."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиента."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиента в рецепте."""

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeMinifiedSerializer(serializers.ModelSerializer):
    """Сокращенный сериализатор для рецепта."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для рецепта."""

    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = IngredientInRecipeSerializer(
        source='recipe_ingredients',
        many=True,
        read_only=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        )
        read_only_fields = (
            'id',
            'author',
            'is_favorited',
            'is_in_shopping_cart'
        )

    def get_is_favorited(self, obj):
        """Проверяет, добавлен ли рецепт в избранное."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Favorite.objects.filter(
                user=request.user, recipe=obj
            ).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        """Проверяет, добавлен ли рецепт в корзину."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return ShoppingCart.objects.filter(
                user=request.user, recipe=obj
            ).exists()
        return False


class IngredientCreateSerializer(serializers.Serializer):
    """Сериализатор для создания ингредиента в рецепте."""
    id = serializers.IntegerField()
    amount = serializers.IntegerField(min_value=MIN_VALUE_AMOUNT)


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания рецепта."""

    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    ingredients = IngredientCreateSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time'
        )

    def validate_ingredients(self, value):
        """Валидирует ингредиенты."""
        if not value:
            raise ValidationError(
                'Необходимо указать хотя бы один ингредиент.'
            )
        ingredient_ids = [item['id'] for item in value]
        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise ValidationError('Ингредиенты должны быть уникальными.')
        return value

    def validate_tags(self, value):
        """Валидирует теги."""
        if not value:
            raise ValidationError('Необходимо указать хотя бы один тег.')
        return value

    @transaction.atomic
    def create(self, validated_data):
        """Создает рецепт."""
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        recipe = Recipe.objects.create(
            author=self.context['request'].user,
            **validated_data
        )
        recipe.tags.set(tags_data)
        for ingredient_data in ingredients_data:
            ingredient = Ingredient.objects.get(id=ingredient_data['id'])
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient,
                amount=ingredient_data['amount']
            )
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        """Обновляет рецепт."""
        ingredients_data = validated_data.pop('ingredients', None)
        tags_data = validated_data.pop('tags', None)
        if ingredients_data is not None:
            instance.recipe_ingredients.all().delete()
            for ingredient_data in ingredients_data:
                ingredient = Ingredient.objects.get(id=ingredient_data['id'])
                RecipeIngredient.objects.create(
                    recipe=instance,
                    ingredient=ingredient,
                    amount=ingredient_data['amount']
                )
        if tags_data is not None:
            instance.tags.set(tags_data)
        return super().update(instance, validated_data)


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор для избранного."""

    class Meta:
        model = Favorite
        fields = ('user', 'recipe')

    def to_representation(self, instance):
        return RecipeMinifiedSerializer(instance.recipe).data


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор для корзины."""

    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')

    def to_representation(self, instance):
        return RecipeMinifiedSerializer(instance.recipe).data


class UserWithRecipesSerializer(CustomUserSerializer):
    """Сериализатор пользователя с рецептами."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(CustomUserSerializer.Meta):
        fields = CustomUserSerializer.Meta.fields + (
            'recipes',
            'recipes_count'
        )

    def get_recipes(self, obj):
        """Возвращает рецепты пользователя."""
        request = self.context.get('request')
        recipes_limit = request.query_params.get('recipes_limit')
        recipes = obj.recipes.all()
        if recipes_limit:
            try:
                recipes = recipes[:int(recipes_limit)]
            except ValueError:
                pass
        return RecipeMinifiedSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        """Возвращает количество рецептов."""
        return obj.recipes.count()


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор для подписки."""

    class Meta:
        model = Subscription
        fields = ('user', 'author')

    def to_representation(self, instance):
        return UserWithRecipesSerializer(
            instance.author,
            context=self.context
        ).data


class RecipeGetShortLinkSerializer(serializers.Serializer):
    """Сериализатор для короткой ссылки на рецепт."""

    short_link = serializers.URLField()
