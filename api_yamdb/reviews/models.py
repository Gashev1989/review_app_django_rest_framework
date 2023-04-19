from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone

USER = 'user'
MODERATOR = 'moderator'
ADMIN = 'admin'
ROLE_CHOICES = (
    (USER, 'пользователь'),
    (MODERATOR, 'модератор'),
    (ADMIN, 'администратор')
)


class User(AbstractUser):
    """Модель пользователей."""
    email = models.EmailField(
        max_length=254,
        unique=True,
        verbose_name='E-mail пользователя')
    bio = models.TextField(
        verbose_name='Биография пользователя',
        null=True,
        blank=True
    )
    password = models.CharField(max_length=100, blank=True)
    role = models.CharField(
        max_length=9,
        choices=ROLE_CHOICES,
        default=USER,
        verbose_name='Роль пользователя'
    )
    key = models.IntegerField(null=True, blank=True)

    @property
    def is_admin(self):
        return self.role == ADMIN

    @property
    def is_moderator(self):
        return self.role == MODERATOR

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=~models.Q(username__exact='me'),
                name="username shouldn't be 'me'"
            )
        ]

    def __str__(self):
        return self.username


class Category(models.Model):
    """Модель категорий произведений."""
    name = models.CharField(
        max_length=256,
        verbose_name='Категория произведения'
    )
    slug = models.SlugField(
        max_length=50,
        verbose_name='Slug категории произведения',
        unique=True
    )

    def __str__(self):
        return self.name


class Genre(models.Model):
    """Модель жанров произведений."""
    name = models.CharField(
        max_length=256,
        verbose_name='Жанр произведения'
    )
    slug = models.SlugField(
        max_length=50,
        verbose_name='Slug жанра произведения',
        unique=True
    )

    def __str__(self):
        return self.name


class Title(models.Model):
    """Модель произведений."""
    name = models.CharField(
        max_length=256,
        verbose_name='Название произведения'
    )
    year = models.IntegerField(
        verbose_name='Год создания произведения',
        validators=[MaxValueValidator(timezone.now().year)]
    )
    description = models.TextField(
        verbose_name='Описание произведения',
        null=True,
        blank=True
    )
    genre = models.ManyToManyField(
        Genre,
        verbose_name='Ссылки на жанры произведения',
        through='TitleGenre'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        verbose_name='Ссылка на категорию произведения',
        related_name='titles',
        null=True
    )

    def __str__(self):
        return self.name


class TitleGenre(models.Model):
    """Модель связи произведений и жанров."""
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        verbose_name='Ссылка на произведение'
    )
    genre = models.ForeignKey(
        Genre,
        on_delete=models.CASCADE,
        verbose_name='Ссылка на жанр произведения'
    )


class Review(models.Model):
    """Модель отзывов на произведения."""
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        verbose_name='Ссылка на произведение',
        related_name='reviews'
    )
    text = models.TextField(
        verbose_name='Текст отзыва'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Ссылка на автора отзыва',
        related_name='reviews'
    )
    score = models.PositiveSmallIntegerField(
        verbose_name='Оценка отзыва',
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата и время создания отзыва',
        auto_now_add=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'author'],
                name='unique_review'
            )
        ]

    def __str__(self):
        return self.text


class Comment(models.Model):
    """Модель комментариев на отзывы."""
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        verbose_name='Ссылка на отзыв',
        related_name='comments'
    )
    text = models.TextField(
        verbose_name='Текст комментария'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Ссылка на автора комментария',
        related_name='comments'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата и время создания коммента',
        auto_now_add=True
    )

    def __str__(self):
        return self.text
