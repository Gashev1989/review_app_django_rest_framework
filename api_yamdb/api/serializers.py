import re
from datetime import datetime

from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from rest_framework.validators import UniqueValidator

from reviews.models import Category, Comment, Genre, Review, Title, User
from .helpers import get_users


class AuthSerializer(serializers.Serializer):

    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all())])
    username = serializers.CharField(
        validators=[UniqueValidator(queryset=User.objects.all())])

    def validate_email(self, value):
        if len(value) > 254:
            raise serializers.ValidationError(
                'длина email должна быть меньше 254 символов')
        return value

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError('username не может быть me')

        if not re.match(r'[\w.@+-]+\Z', value):
            raise serializers.ValidationError(
                'поле username должно состоять из латинских букв и цифр')

        if len(value) > 150:
            raise serializers.ValidationError(
                'длина username должна быть меньше 150 символов')
        return value


class UsersSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name',
                  'last_name', 'bio', 'role']

    def validate(self, data):
        email = data.get('email')

        if any(get_users(data)):
            raise serializers.ValidationError(
                'поля username и email должны быть  уникальными')

        if email and len(email) > 254:
            raise serializers.ValidationError(
                'длина email должна быть меньше 254 символов')

        for field in ('username', 'first_name', 'last_name'):
            field = data.get(field)
            if field and 1 < len(field) > 150:
                raise serializers.ValidationError(
                    f'{field} не должен привышать 150 символов')

        return data


class CategorySerializer(serializers.ModelSerializer):
    """Сериалайзер для категорий."""

    class Meta:
        fields = ('name', 'slug')
        model = Category


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для жанров."""

    class Meta:
        fields = ('name', 'slug')
        model = Genre


class CommentSerializer(serializers.ModelSerializer):
    """Сериалайзер для комментариев."""
    author = SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        fields = '__all__'
        read_only_fields = ('review',)
        model = Comment


class TitleSerializerForChange(serializers.ModelSerializer):
    """Сериалайзер для внесения изменений в названия произведения."""
    category = SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all()
    )
    genre = SlugRelatedField(
        slug_field='slug',
        many=True,
        queryset=Genre.objects.all()
    )

    class Meta:
        fields = '__all__'
        model = Title

    def validate_year(self, value):
        if value > datetime.now().year:
            raise serializers.ValidationError(
                'Год создания не может быть больше текущего!')
        return value


class TitleSerializerForRead(serializers.ModelSerializer):
    """Сериалайзер для чтения названий произведений."""
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(many=True, read_only=True)
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        fields = '__all__'
        model = Title


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для отзыва."""
    author = SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        fields = '__all__'
        read_only_fields = ('title',)
        model = Review

    def validate(self, data):
        author = self.context.get('request').user
        title_id = self.context.get('view').kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        if self.context.get('request').method == 'POST':
            if Review.objects.filter(title=title, author=author).exists():
                raise serializers.ValidationError('Вы уже создавали отзыв.')
        return data
