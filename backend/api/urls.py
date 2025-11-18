from api.views import IngredientViewSet, RecipeViewSet, TagViewSet
from django.urls import include, path
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework.routers import DefaultRouter

app_name = 'api'

router_v1 = DefaultRouter()

router_v1.register('users', DjoserUserViewSet, basename='users')
router_v1.register('recipes', RecipeViewSet, basename='recipe')
router_v1.register('ingredients', IngredientViewSet, basename='ingredient')
router_v1.register('tags', TagViewSet, basename='tag')

urlpatterns = [
    path('', include(router_v1.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]