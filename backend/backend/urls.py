from django.contrib import admin
from django.urls import include, path
from django.http import JsonResponse


def home(request):
    return JsonResponse({"message": "Welcome to Foodgram API"})


urlpatterns = [
    path('', home, name='home'),
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
]
