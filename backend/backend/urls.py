from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import include, path


def home(request):
    return redirect('/api/')


def short_url(request, short_link):
    return redirect(f"{settings.FRONTEND_BASE_URL}/recipes/{short_link}")


urlpatterns = [
    path('', home, name='home'),
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('s/<slug:short_link>/', short_url, name='short_url'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
