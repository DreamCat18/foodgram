from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from backend.constants import (
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST,
)

from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    ShoppingCart,
    Subscription,
    Tag
)

from .filters import IngredientFilter, RecipeFilter
from .pagination import CustomPagination
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    CustomUserSerializer,
    FavoriteSerializer,
    IngredientSerializer,
    RecipeCreateSerializer,
    RecipeSerializer,
    SetAvatarSerializer,
    ShoppingCartSerializer,
    SubscriptionSerializer,
    TagSerializer,
    UserWithRecipesSerializer
)

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """Представление для пользователей."""

    queryset = User.objects.all()
    pagination_class = CustomPagination

    def get_serializer_class(self):
        """Возвращает класс сериализатора в зависимости от действия."""
        if self.action == 'create':
            return CustomUserSerializer
        return CustomUserSerializer

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def me(self, request):
        """Возвращает данные текущего пользователя."""
        serializer = CustomUserSerializer(
            request.user,
            context={'request': request}
        )
        return Response(serializer.data)

    @action(
        detail=True,
        methods=['put'],
        permission_classes=[IsAuthenticated]
    )
    def avatar(self, request, pk=None):
        """Устанавливает аватар пользователя."""
        if pk != 'me':
            return Response(
                {'error': 'Invalid request'},
                status=HTTP_400_BAD_REQUEST
            )
        serializer = SetAvatarSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @avatar.mapping.delete
    def delete_avatar(self, request, pk=None):
        """Удаляет аватар пользователя."""
        if pk != 'me':
            return Response(
                {'error': 'Invalid request'},
                status=HTTP_400_BAD_REQUEST
            )
        request.user.avatar.delete()
        return Response(status=HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        """Возвращает подписки пользователя."""
        subscriptions = Subscription.objects.filter(user=request.user)
        authors = [subscription.author for subscription in subscriptions]
        page = self.paginate_queryset(authors)
        serializer = UserWithRecipesSerializer(
            page,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, pk=None):
        """Подписывается или отписывается от пользователя."""
        author = get_object_or_404(User, pk=pk)
        if request.method == 'POST':
            if Subscription.objects.filter(
                user=request.user,
                author=author
            ).exists():
                return Response(
                    {'errors': 'Вы уже подписаны на этого пользователя.'},
                    status=HTTP_400_BAD_REQUEST
                )
            if author == request.user:
                return Response(
                    {'errors': 'Нельзя подписаться на себя.'},
                    status=HTTP_400_BAD_REQUEST
                )
            Subscription.objects.create(user=request.user, author=author)
            serializer = SubscriptionSerializer(
                Subscription.objects.get(user=request.user, author=author),
                context={'request': request}
            )
            return Response(serializer.data, status=HTTP_201_CREATED)
        if request.method == 'DELETE':
            subscription = get_object_or_404(
                Subscription, user=request.user, author=author
            )
            subscription.delete()
            return Response(status=HTTP_204_NO_CONTENT)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Представление для тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Представление для ингредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    """Представление для рецептов."""

    queryset = Recipe.objects.all()
    pagination_class = CustomPagination
    permission_classes = [IsAuthorOrReadOnly]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_queryset(self):
        """Возвращает queryset с учетом фильтров избранного и корзины."""
        queryset = super().get_queryset()

        if self.action == 'favorite' and self.request.user.is_authenticated:
            return queryset.filter(favorites__user=self.request.user)

        if self.action == (
            'shopping_cart' and self.request.user.is_authenticated
        ):
            return queryset.filter(shopping_cart__user=self.request.user)

        return queryset

    def get_serializer_class(self):
        """Возвращает класс сериализатора в зависимости от действия."""
        if self.action in ['create', 'update', 'partial_update']:
            return RecipeCreateSerializer
        return RecipeSerializer

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated],
        url_path='favorites'
    )
    def favorites_list(self, request):
        """Возвращает список избранных рецептов."""
        favorites = Favorite.objects.filter(user=request.user)
        recipes = [favorite.recipe for favorite in favorites]
        tags = request.query_params.getlist('tags')
        if tags:
            recipes = [recipe for recipe in recipes if any(
                tag.slug in tags for tag in recipe.tags.all())]
        page = self.paginate_queryset(recipes)
        serializer = RecipeSerializer(
            page,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk=None):
        """Добавляет или удаляет рецепт из избранного."""
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            if Favorite.objects.filter(
                user=request.user,
                recipe=recipe
            ).exists():
                return Response(
                    {'errors': 'Рецепт уже в избранном.'},
                    status=HTTP_400_BAD_REQUEST
                )
            Favorite.objects.create(user=request.user, recipe=recipe)
            serializer = FavoriteSerializer(
                Favorite.objects.get(user=request.user, recipe=recipe)
            )
            return Response(serializer.data, status=HTTP_201_CREATED)
        if request.method == 'DELETE':
            favorite = get_object_or_404(
                Favorite, user=request.user, recipe=recipe
            )
            favorite.delete()
            return Response(status=HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated],
        url_path='shopping-cart'
    )
    def shopping_cart_list(self, request):
        """Возвращает список рецептов в корзине."""
        shopping_cart = ShoppingCart.objects.filter(user=request.user)
        recipes = [item.recipe for item in shopping_cart]
        page = self.paginate_queryset(recipes)
        serializer = RecipeSerializer(
            page,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk=None):
        """Добавляет или удаляет рецепт из списка покупок."""
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            if ShoppingCart.objects.filter(
                user=request.user,
                recipe=recipe
            ).exists():
                return Response(
                    {'errors': 'Рецепт уже в списке покупок.'},
                    status=HTTP_400_BAD_REQUEST
                )
            ShoppingCart.objects.create(user=request.user, recipe=recipe)
            serializer = ShoppingCartSerializer(
                ShoppingCart.objects.get(user=request.user, recipe=recipe)
            )
            return Response(serializer.data, status=HTTP_201_CREATED)
        if request.method == 'DELETE':
            shopping_cart = get_object_or_404(
                ShoppingCart, user=request.user, recipe=recipe
            )
            shopping_cart.delete()
            return Response(status=HTTP_204_NO_CONTENT)
