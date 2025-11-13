from django.urls import path

from .views import short_url

app_name = 'recipes'

urlpatterns = [
    path('s/<slug:short_link>/', short_url, name='short_url'),
]
