from django.contrib.auth import get_user_model
from django.db import transaction
from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag
)
from users.models import Subscription
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.relations import PrimaryKeyRelatedField, SlugRelatedField

from backend.constants import MIN_VALUE_AMOUNT
from .fields import Base64ImageField

User = get_user_model()


class UserGetSerializer(serializers.ModelSerializer):
    """Сериализатор для пользователя."""

    is_subscribed = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'avatar',
        )
        read_only_fields = ('id', 'is_subscribed')

    def get_is_subscribed(self, obj):
        """Проверяет, подписан ли текущий пользователь на данного."""
        request = self.context.get('request')
        return (
            request
            and request.user.is_authenticated
            and Subscription.objects.filter(
                user=request.user,
                author=obj,
            ).exists()
        )

    def get_avatar(self, obj):
        """Возвращает полный URL аватара."""
        request = self.context.get('request')
        if obj.avatar and request:
            return request.build_absolute_uri(obj.avatar.url)
        return obj.avatar.url if obj.avatar else None


class UserPostSerializer(serializers.ModelSerializer):
    """Сериализатор для создания пользователя."""

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
        )
        extra_kwargs = {'password': {'write_only': True}}

    def validate_username(self, value):
        """Запрещает использование username 'me'."""
        if value.lower() == 'me':
            raise ValidationError(
                'Нельзя использовать "me" в качестве username.'
            )
        return value

    def create(self, validated_data):
        """Создает нового пользователя."""
        return User.objects.create_user(**validated_data)


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

    id = PrimaryKeyRelatedField(
        source='ingredient',
        read_only=True,
    )
    name = SlugRelatedField(
        source='ingredient',
        slug_field='name',
        read_only=True,
    )
    measurement_unit = SlugRelatedField(
        source='ingredient',
        slug_field='measurement_unit',
        read_only=True,
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeShortSerializer(serializers.ModelSerializer):
    """Сокращенный сериализатор для рецепта."""

    image = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')

    def get_image(self, obj):
        """Возвращает полный URL изображения."""
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return obj.image.url if obj.image else None


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для рецепта."""

    tags = TagSerializer(
        many=True,
        read_only=True,
    )
    author = UserGetSerializer(read_only=True)
    ingredients = IngredientInRecipeSerializer(
        source='recipe_ingredients',
        many=True,
        read_only=True,
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )
        read_only_fields = (
            'id',
            'author',
            'is_favorited',
            'is_in_shopping_cart',
        )

    def get_image(self, obj):
        """Возвращает полный URL изображения."""
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return obj.image.url if obj.image else None

    def get_is_favorited(self, obj):
        """Проверяет, добавлен ли рецепт в избранное."""
        request = self.context.get('request')
        return (
            request
            and request.user.is_authenticated
            and Favorite.objects.filter(
                user=request.user,
                recipe=obj,
            ).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        """Проверяет, добавлен ли рецепт в корзину."""
        request = self.context.get('request')
        return (
            request
            and request.user.is_authenticated
            and ShoppingCart.objects.filter(
                user=request.user,
                recipe=obj,
            ).exists()
        )


class IngredientCreateSerializer(serializers.Serializer):
    """Сериализатор для создания ингредиента в рецепте."""

    id = serializers.IntegerField()
    amount = serializers.IntegerField(min_value=MIN_VALUE_AMOUNT)

    def to_representation(self, instance):
        """Возвращает представление ингредиента."""
        return {
            'id': instance.ingredient.id,
            'name': instance.ingredient.name,
            'measurement_unit': instance.ingredient.measurement_unit,
            'amount': instance.amount,
        }


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания рецепта."""

    tags = PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
    )
    ingredients = IngredientCreateSerializer(many=True, write_only=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
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

    def _create_recipe_ingredients(self, recipe, ingredients_data):
        """Создает ингредиенты для рецепта через bulk_create."""
        recipe_ingredients = (
            RecipeIngredient(
                recipe=recipe,
                ingredient_id=ingredient_data['id'],
                amount=ingredient_data['amount'],
            )
            for ingredient_data in ingredients_data
        )
        RecipeIngredient.objects.bulk_create(recipe_ingredients)

    @transaction.atomic
    def create(self, validated_data):
        """Создает рецепт."""
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')

        recipe = Recipe.objects.create(
            author=self.context['request'].user,
            **validated_data,
        )

        recipe.tags.set(tags_data)
        self._create_recipe_ingredients(recipe, ingredients_data)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        """Обновляет рецепт."""
        ingredients_data = validated_data.pop('ingredients', None)
        tags_data = validated_data.pop('tags', None)

        if ingredients_data is not None:
            instance.ingredients.clear()
            self._create_recipe_ingredients(instance, ingredients_data)

        if tags_data is not None:
            instance.tags.set(tags_data)

        return super().update(instance, validated_data)


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор для избранного."""

    class Meta:
        model = Favorite
        fields = ('user', 'recipe')

    def validate(self, data):
        """Валидирует данные для избранного."""
        if Favorite.objects.filter(
            user=data['user'],
            recipe=data['recipe'],
        ).exists():
            raise ValidationError('Рецепт уже в избранном.')
        return data

    def to_representation(self, instance):
        return RecipeShortSerializer(instance.recipe).data


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор для корзины."""

    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')

    def validate(self, data):
        """Валидирует данные для корзины."""
        if ShoppingCart.objects.filter(
            user=data['user'],
            recipe=data['recipe'],
        ).exists():
            raise ValidationError('Рецепт уже в корзине.')
        return data

    def to_representation(self, instance):
        return RecipeShortSerializer(instance.recipe).data


class UserWithRecipesSerializer(UserGetSerializer):
    """Сериализатор пользователя с рецептами."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'avatar',
            'recipes',
            'recipes_count',
        )

    def get_recipes(self, obj):
        """Возвращает рецепты пользователя."""
        request = self.context.get('request')
        recipes_limit = (
            request.query_params.get('recipes_limit')
            if request else None
        )
        recipes = obj.recipes.all()

        if recipes_limit:
            try:
                recipes = recipes[:int(recipes_limit)]
            except ValueError:
                pass

        return RecipeShortSerializer(
            recipes,
            many=True,
            context=self.context,
        ).data

    def get_recipes_count(self, obj):
        """Возвращает количество рецептов."""
        return obj.recipes.count()


class SubscriptionCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания подписки."""

    class Meta:
        model = Subscription
        fields = ('user', 'author')

    def validate(self, data):
        """Валидирует данные для подписки."""
        if data['user'] == data['author']:
            raise ValidationError('Нельзя подписаться на себя.')

        if Subscription.objects.filter(
            user=data['user'],
            author=data['author'],
        ).exists():
            raise ValidationError('Вы уже подписаны на этого пользователя.')

        return data

    def to_representation(self, instance):
        return UserWithRecipesSerializer(instance.author).data
