from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import models

User = get_user_model()


class Category(models.Model):
    name = models.CharField(max_length=50, verbose_name='Название')
    slug = models.SlugField(max_length=50, unique=True, verbose_name='Слаг')

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=50, verbose_name='Название')
    slug = models.SlugField(max_length=50, unique=True, verbose_name='Слаг')

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField(max_length=50, verbose_name='Название')
    year = models.IntegerField(
        validators=[
            MaxValueValidator(timezone.now().year)
        ],
        db_index=True,
        verbose_name='Год'
    )
    description = models.TextField(blank=True, verbose_name='Описание')
    category = models.ForeignKey(
        Category,
        null=True,
        blank=True,
        related_name='titles',
        on_delete=models.SET_NULL,
        verbose_name='Категория'
    )

    genre = models.ManyToManyField(
        Genre,
        related_name='titles',
        verbose_name='Жанр'
    )

    class Meta:
        verbose_name = 'Тайтл'
        verbose_name_plural = 'Тайтлы'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'year'],
                name='unique_title'
            )
        ]
        ordering = ['-year']

    def __str__(self):
        return self.name


class Review(models.Model):
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Произведение'
    )
    text = models.TextField(verbose_name='Текст')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Автор отзыва'
    )
    score = models.IntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(10)
        ],
        verbose_name='Рейтинг'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        unique_together = ['author', 'title']

    def __str__(self):
        return f'{self.title} {self.text} {self.author} {self.score}'


class Comments(models.Model):
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        verbose_name='Отзыв',
        related_name='comments'
    )
    text = models.TextField(verbose_name='Текст')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return f'{self.author} {self.text}'
