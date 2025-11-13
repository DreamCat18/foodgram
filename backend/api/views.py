from collections import defaultdict

from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from recipes.models import (Favorite, Ingredient, Recipe, ShoppingCart,
                            Subscription, Tag)
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from backend.constants import HTTP_201_CREATED, HTTP_204_NO_CONTENT

from .filters import IngredientFilter, RecipeFilter
from .paginations import CustomPagination
from .permissions import IsAuthorOrReadOnlyPermission
from .serializers import (FavoriteSerializer, IngredientSerializer,
                          RecipeCreateSerializer, RecipeSerializer,
                          SetAvatarSerializer, ShoppingCartSerializer,
                          SubscriptionCreateSerializer, TagSerializer,
                          UserGetSerializer, UserPostSerializer,
                          UserWithRecipesSerializer)

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """Представление для пользователей."""

    queryset = User.objects.all()
    pagination_class = CustomPagination
    permission_classes = [AllowAny]

    def get_permissions(self):
        """Разные permissions для разных действий."""
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]

        if self.action in [
            'update',
            'partial_update',
            'destroy',
            'subscriptions',
            'subscribe',
            'me',
        ]:
            return [IsAuthenticated()]

        return [AllowAny()]

    def get_serializer_class(self):
        """Возвращает класс сериализатора в зависимости от действия."""
        if self.action == 'create':
            return UserPostSerializer
        if self.action == 'retrieve':
            return UserWithRecipesSerializer
        return UserGetSerializer

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def me(self, request):
        """Возвращает данные текущего пользователя."""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(
        detail=True,
        methods=['put'],
        permission_classes=[IsAuthenticated],
        url_path='me/avatar',
    )
    def set_avatar(self, request, pk=None):
        """Устанавливает аватар пользователя."""
        if pk != 'me':
            return Response(
                {'error': 'Invalid request'},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = SetAvatarSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @set_avatar.mapping.delete
    def delete_avatar(self, request, pk=None):
        """Удаляет аватар пользователя."""
        if pk != 'me':
            return Response(
                {'error': 'Invalid request'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if request.user.avatar:
            request.user.avatar.delete()
        return Response(status=HTTP_204_NO_CONTENT)

    def get_subscriptions_queryset(self):
        """Возвращает queryset для подписок."""
        return Subscription.objects.filter(
            user=self.request.user
        ).select_related(
            'author'
        )

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        """Возвращает подписки пользователя."""
        queryset = self.get_subscriptions_queryset()
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = UserWithRecipesSerializer(
                [sub.author for sub in page],
                many=True,
                context={'request': request}
            )
            return self.get_paginated_response(serializer.data)

        authors = [sub.author for sub in queryset]
        serializer = UserWithRecipesSerializer(
            authors, many=True, context={'request': request}
        )
        return Response(serializer.data)

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, pk=None):
        """Подписывается на пользователя."""
        author = get_object_or_404(User, pk=pk)
        serializer = SubscriptionCreateSerializer(
            data={'user': request.user.id, 'author': author.id},
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=HTTP_201_CREATED)

    @subscribe.mapping.delete
    def unsubscribe(self, request, pk=None):
        """Отписывается от пользователя."""
        author = get_object_or_404(User, pk=pk)
        subscription = get_object_or_404(
            Subscription,
            user=request.user,
            author=author
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
    permission_classes = [IsAuthorOrReadOnlyPermission]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        """Возвращает класс сериализатора в зависимости от действия."""
        if self.action in ['create', 'update', 'partial_update']:
            return RecipeCreateSerializer
        return RecipeSerializer

    def _add_relation(
        self,
        request,
        pk,
        serializer_class,
        model_class,
        error_message
    ):
        """Общий метод для добавления связи."""
        recipe = get_object_or_404(Recipe, pk=pk)
        serializer = serializer_class(
            data={'user': request.user.id, 'recipe': recipe.id},
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=HTTP_201_CREATED)

    def _remove_relation(self, request, pk, model_class):
        """Общий метод для удаления связи."""
        recipe = get_object_or_404(Recipe, pk=pk)
        relation = get_object_or_404(
            model_class,
            user=request.user,
            recipe=recipe
        )
        relation.delete()
        return Response(status=HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk=None):
        """Добавляет рецепт в избранное."""
        return self._add_relation(
            request,
            pk,
            FavoriteSerializer,
            Favorite,
            'Рецепт уже в избранном.'
        )

    @favorite.mapping.delete
    def remove_favorite(self, request, pk=None):
        """Удаляет рецепт из избранного."""
        return self._remove_relation(request, pk, Favorite)

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk=None):
        """Добавляет рецепт в корзину."""
        return self._add_relation(
            request,
            pk,
            ShoppingCartSerializer,
            ShoppingCart,
            'Рецепт уже в корзине.'
        )

    @shopping_cart.mapping.delete
    def remove_shopping_cart(self, request, pk=None):
        """Удаляет рецепт из корзины."""
        return self._remove_relation(request, pk, ShoppingCart)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        """Скачивает список покупок."""
        recipes = Recipe.objects.filter(shopping_cart__user=request.user)
        ingredients = defaultdict(float)
        for recipe in recipes:
            for ri in recipe.recipe_ingredients.all():
                key = (ri.ingredient.name, ri.ingredient.measurement_unit)
                ingredients[key] += ri.amount

        content_lines = ['Список покупок:\n']
        content_lines.extend(
            f'• {name}: {amount} {unit}'
            for (name, unit), amount in ingredients.items()
        )
        content_lines.append(f'\nВсего позиций: {len(ingredients)}')
        content = '\n'.join(content_lines)

        response = HttpResponse(
            content,
            content_type='text/plain; charset=utf-8'
        )
        response['Content-Disposition'] = (
            'attachment; filename="shopping_list.txt"'
        )
        return response

    @action(detail=True, methods=['get'], permission_classes=[AllowAny])
    def get_short_link(self, request, pk=None):
        """Возвращает короткую ссылку на рецепт."""
        import base64
        recipe = get_object_or_404(Recipe, pk=pk)
        short_code = base64.urlsafe_b64encode(
            str(recipe.pk).encode()
        ).decode().rstrip('=')
        short_link = request.build_absolute_uri(f'/s/{short_code}/')
        return Response({'short_link': short_link}, status=status.HTTP_200_OK)
