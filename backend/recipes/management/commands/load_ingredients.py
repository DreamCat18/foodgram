import os
from csv import reader

from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.models import Ingredient, Tag


class Command(BaseCommand):
    """Загружает данные из CSV файлов в базу данных."""

    help = 'Загрузка данных из CSV-файлов'

    def handle(self, *args, **options):
        """Загружает ингредиенты и теги из CSV файлов."""
        
        ingredients_path = os.path.join(settings.BASE_DIR, 'data', 'ingredients.csv')
        if os.path.exists(ingredients_path):
            ingredients_created = 0
            with open(ingredients_path, 'r', encoding='utf-8') as file:
                csv_reader = reader(file)
                for row in csv_reader:
                    if len(row) >= 2:
                        name = row[0].strip()
                        measurement_unit = row[1].strip()
                        ingredient, created = Ingredient.objects.get_or_create(
                            name=name,
                            measurement_unit=measurement_unit
                        )
                        if created:
                            ingredients_created += 1
            self.stdout.write(f'Загружено {ingredients_created} новых ингредиентов')
        else:
            self.stdout.write('Файл ingredients.csv не найден')

        tags_path = os.path.join(settings.BASE_DIR, 'data', 'tags.csv')
        if os.path.exists(tags_path):
            tags_created = 0
            tags_in_csv = set()
            with open(tags_path, 'r', encoding='utf-8') as file:
                csv_reader = reader(file)
                for row in csv_reader:
                    if len(row) >= 2:
                        name = row[0].strip()
                        slug = row[1].strip()
                        tags_in_csv.add(slug)
                        tag, created = Tag.objects.get_or_create(
                            name=name,
                            slug=slug
                        )
                        if created:
                            tags_created += 1
            # Удаляем теги, которых нет в CSV
            tags_deleted = 0
            for tag in Tag.objects.all():
                if tag.slug not in tags_in_csv:
                    tag.delete()
                    tags_deleted += 1
            self.stdout.write(f'Загружено {tags_created} новых тегов')
            self.stdout.write(f'Удалено {tags_deleted} тегов')
        else:
            self.stdout.write('Файл tags.csv не найден')

        self.stdout.write('Загрузка данных завершена!')