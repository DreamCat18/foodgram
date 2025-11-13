from django.core.validators import MinValueValidator
from django.db import models

from backend.constants import (MAX_LENGTH_MEASUREMENT_UNIT,
                               MAX_LENGTH_NAME_INGREDIENT,
                               MAX_LENGTH_NAME_RECIPE, MAX_LENGTH_NAME_TAG,
                               MAX_LENGTH_SLUG_TAG, MIN_VALUE_AMOUNT,
                               MIN_VALUE_COOKING_TIME,
                               RELATED_NAME_RECIPE_INGREDIENTS,
                               RELATED_NAME_RECIPES,
                               UPLOAD_PATH_RECIPES,
                               VERBOSE_NAME_AMOUNT, VERBOSE_NAME_AUTHOR,
                               VERBOSE_NAME_COOKING_TIME, VERBOSE_NAME_IMAGE,
                               VERBOSE_NAME_INGREDIENT,
                               VERBOSE_NAME_INGREDIENTS,
                               VERBOSE_NAME_MEASUREMENT_UNIT,
                               VERBOSE_NAME_NAME, VERBOSE_NAME_PUB_DATE,
                               VERBOSE_NAME_RECIPE, VERBOSE_NAME_SLUG,
                               VERBOSE_NAME_TAGS, VERBOSE_NAME_TEXT,
                               VERBOSE_NAME_USER)


class Tag(models.Model):
    """Модель тега для рецептов."""

    name = models.CharField(
        VERBOSE_NAME_NAME,
        max_length=MAX_LENGTH_NAME_TAG,
        unique=True
    )
    slug = models.SlugField(
        VERBOSE_NAME_SLUG,
        max_length=MAX_LENGTH_SLUG_TAG,
        unique=True
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ['name']

    def __str__(self):
        """Возвращает строковое представление тега."""
        return self.name


class Ingredient(models.Model):
    """Модель ингредиента."""

    name = models.CharField(
        VERBOSE_NAME_NAME,
        max_length=MAX_LENGTH_NAME_INGREDIENT
    )
    measurement_unit = models.CharField(
        VERBOSE_NAME_MEASUREMENT_UNIT,
        max_length=MAX_LENGTH_MEASUREMENT_UNIT
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_ingredient'
            )
        ]

    def __str__(self):
        """Возвращает строковое представление ингредиента."""
        return f'{self.name} ({self.measurement_unit})'


class Recipe(models.Model):
    """Модель рецепта."""

    author = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name=RELATED_NAME_RECIPES,
        verbose_name=VERBOSE_NAME_AUTHOR
    )
    name = models.CharField(
        VERBOSE_NAME_NAME,
        max_length=MAX_LENGTH_NAME_RECIPE
    )
    image = models.ImageField(
        VERBOSE_NAME_IMAGE,
        upload_to=UPLOAD_PATH_RECIPES
    )
    text = models.TextField(
        VERBOSE_NAME_TEXT
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        related_name=RELATED_NAME_RECIPES,
        verbose_name=VERBOSE_NAME_INGREDIENTS
    )
    tags = models.ManyToManyField(
        Tag,
        related_name=RELATED_NAME_RECIPES,
        verbose_name=VERBOSE_NAME_TAGS
    )
    cooking_time = models.PositiveSmallIntegerField(
        VERBOSE_NAME_COOKING_TIME,
        validators=[MinValueValidator(
            MIN_VALUE_COOKING_TIME,
            message=(
                'Время приготовления не может быть '
                f'меньше {MIN_VALUE_COOKING_TIME} минуты.'
            )
        )]
    )
    pub_date = models.DateTimeField(
        VERBOSE_NAME_PUB_DATE,
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-pub_date']

    def __str__(self):
        """Возвращает строковое представление рецепта."""
        return self.name


class RecipeIngredient(models.Model):
    """Модель ингредиента в рецепте."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name=RELATED_NAME_RECIPE_INGREDIENTS,
        verbose_name=VERBOSE_NAME_RECIPE
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name=RELATED_NAME_RECIPE_INGREDIENTS,
        verbose_name=VERBOSE_NAME_INGREDIENT
    )
    amount = models.PositiveSmallIntegerField(
        VERBOSE_NAME_AMOUNT,
        validators=[MinValueValidator(
            MIN_VALUE_AMOUNT,
            message=(
                'Количество ингредиента '
                f'не может быть меньше {MIN_VALUE_AMOUNT}.'
            )
        )]
    )

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецептах'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_recipe_ingredient'
            )
        ]

    def __str__(self):
        """Возвращает строковое представление ингредиента в рецепте."""
        return f'{self.ingredient} в {self.recipe}'


class BaseUserRecipeRelation(models.Model):
    """Базовая модель для отношений пользователя и рецепта."""

    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        verbose_name=VERBOSE_NAME_USER
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name=VERBOSE_NAME_RECIPE
    )

    class Meta:
        abstract = True
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_%(class)s'
            )
        ]


class Favorite(BaseUserRecipeRelation):
    """Модель избранного рецепта."""

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'

    def __str__(self):
        """Возвращает строковое представление избранного."""
        return f'{self.user} добавил {self.recipe} в избранное'


class ShoppingCart(BaseUserRecipeRelation):
    """Модель списка покупок."""

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'

    def __str__(self):
        """Возвращает строковое представление списка покупок."""
        return f'{self.user} добавил {self.recipe} в список покупок'
