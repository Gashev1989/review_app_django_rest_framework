import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand
from reviews.models import (Category, Comment, Genre,
                            Review, TitleGenre, Title, User)


class Command(BaseCommand):
    help = 'Загрузка инициализационных данных из .csv'

    def handle(self, *args, **options):
        model_file = {
            User: 'users.csv',
            Category: 'category.csv',
            Genre: 'genre.csv',
            Title: 'titles.csv',
            TitleGenre: 'genre_title.csv',
            Review: 'review.csv',
            Comment: 'comments.csv'
        }
        changes = (
            (Title, 'category', Category, 'category'),
            (TitleGenre, 'title', Title, 'title_id'),
            (TitleGenre, 'genre', Genre, 'genre_id'),
            (Review, 'author', User, 'author'),
            (Review, 'title', Title, 'title_id'),
            (Comment, 'author', User, 'author'),
            (Comment, 'review', Review, 'review_id')
        )
        for model, csv_file in model_file.items():
            file_full_path = os.path.join(
                settings.BASE_DIR,
                'static',
                'data',
                csv_file
            )
            with open(file_full_path) as f:
                reader = csv.DictReader(f)
                for line in reader:
                    line.pop('pub_date', None)
                    for (
                        model_to_change,
                        field_base,
                        model_from,
                        field_file
                    ) in changes:
                        if model == model_to_change:
                            line[field_base] = model_from.objects.get(
                                pk=line[field_file]
                            )
                    model.objects.get_or_create(**line)
        self.stdout.write(self.style.SUCCESS('Данные загружены успешно'))
