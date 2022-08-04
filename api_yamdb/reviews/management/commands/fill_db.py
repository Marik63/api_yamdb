import os
import csv

from django.db import IntegrityError
from django.core.management.base import BaseCommand

from users.models import User
from reviews.models import Category, Comments, Genre, Title, Review

ABS_PATH = os.path.abspath('')

MODELS = {
    User: 'users.csv',
    Category: 'category.csv',
    Title: 'titles.csv',
    Genre: 'genre.csv',
    Review: 'review.csv',
    Comments: 'comments.csv',
}


class Command(BaseCommand):
    help = 'Filling tables using csv file from static/data.'

    def handle(self, *args, **options):
        for model in MODELS:
            try:
                csv_path = os.path.join(
                    ABS_PATH,
                    f'static/data/{MODELS.get(model)}'
                )
                with open(csv_path, encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        model.objects.get_or_create(
                            **dict(row)
                        )

            except IntegrityError as _ex:
                print(f'Cant upload data: {_ex.args}')
            except TypeError as _ex:
                print(f'Cant find column name to upload data {_ex.args}')
            except ValueError as _ex:
                print(f'Wrong type data: {_ex.args}')
            else:
                print(f'{MODELS.get(model)} file was correct upload')
