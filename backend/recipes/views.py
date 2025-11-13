import base64

from django.conf import settings
from django.shortcuts import get_object_or_404, redirect

from .models import Recipe


def short_url(request, short_link):
    """Перенаправляет на рецепт по короткой ссылке."""
    try:
        short_link += '=' * (4 - len(short_link) % 4)
        recipe_pk = int(base64.urlsafe_b64decode(short_link).decode())
        recipe = get_object_or_404(Recipe, pk=recipe_pk)
        return redirect(
            f"{settings.FRONTEND_BASE_URL}/recipes/{recipe.slug}"
        )
    except (ValueError, UnicodeDecodeError):
        return redirect('/api/')
