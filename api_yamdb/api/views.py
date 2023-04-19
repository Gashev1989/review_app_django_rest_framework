from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .filters import TitleFilter
from .mixinviewsets import CreateListDestroyMixins
from .permissions import IsAdminOrReadOnly, IsOwnerIReadOnly
from .serializers import (AuthSerializer,
                          CategorySerializer,
                          CommentSerializer,
                          GenreSerializer,
                          ReviewSerializer,
                          TitleSerializerForChange,
                          TitleSerializerForRead,
                          UsersSerializer)
from api.permissions import IsAdmin
from reviews.models import Category, Genre, Review, Title, User
from .helpers import send_massege, get_users


class CommentViewSet(viewsets.ModelViewSet):
    """Вьюсет для комментариев."""
    serializer_class = CommentSerializer
    permission_classes = (IsOwnerIReadOnly,)

    def get_queryset(self):
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, id=review_id)
        return review.comments.all()

    def perform_create(self, serializer):
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, id=review_id)
        serializer.save(author=self.request.user, review=review)


class ReviewViewSet(viewsets.ModelViewSet):
    """Вьюсет для отзывов."""
    serializer_class = ReviewSerializer
    permission_classes = (IsOwnerIReadOnly,)

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        return title.reviews.all()

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        serializer.save(author=self.request.user, title=title)


class CategoryViewSet(CreateListDestroyMixins):
    """Вьюсет для категорий."""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    permission_classes = (IsAdminOrReadOnly,)


class GenreViewSet(CreateListDestroyMixins):
    """Вьюсет для жанров."""
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    permission_classes = (IsAdminOrReadOnly,)


class TitleViewSet(viewsets.ModelViewSet):
    """Вьюсет для произведений."""
    queryset = Title.objects.annotate(rating=Avg('reviews__score'))
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
    permission_classes = (IsAdminOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return TitleSerializerForRead
        return TitleSerializerForChange


class RegistrationView(APIView):
    """
    Регистрация пользователя с прверкой username и email на уникальность,
    в случае успеха создает юзера и оправляет секретный ключ на почту.
    Если пользователь уже существует в системе, то происходит повторная
    отправка секретного ключа на почту.
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request):

        serializer = AuthSerializer(data=request.data)
        user, _ = get_users(request.data)

        if serializer.is_valid():
            user, _ = User.objects.get_or_create(**serializer.validated_data)
            send_massege(user)

            return Response(data=request.data, status=status.HTTP_200_OK)
        elif (user and user.email == request.data.get('email')):
            send_massege(user)

            return Response(data=request.data, status=status.HTTP_200_OK)
        else:
            return Response(
                data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TokenView(APIView):
    """
    Выдает токен для авторизации пользователя.
    проверяет существование юзера и секретного ключа.
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request):

        username = request.data.get('username')
        confirmation_code = request.data.get('confirmation_code')

        if username:
            user = User.objects.filter(username=username).first()

            if not user:
                return Response(
                    {'error': 'пользоваетель не найден'},
                    status=status.HTTP_404_NOT_FOUND
                )

            if confirmation_code == user.key:
                refresh = RefreshToken.for_user(user)
                token = {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
                return Response(token, status=status.HTTP_200_OK)

            return Response(
                {'error': 'не верный ключ'},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    """
    Реализация CRUD для пользователей.
    переопределены методы получения, обновления и удаления,
    для работы со своим профилем исходя из требований.
    """

    queryset = User.objects.all()
    serializer_class = UsersSerializer
    permission_classes = [IsAdmin]
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    http_method_names = ('get', 'post', 'patch', 'delete')

    def get_object(self):
        name = self.request.parser_context['kwargs']['pk']

        if name == 'me':
            instance = get_object_or_404(
                User,
                username=self.request.user.username
            )
        else:
            instance = get_object_or_404(User, username=name)

        return instance

    def partial_update(self, request, *args, **kwargs):

        if kwargs.get('pk') == 'me' and request.data.get('role'):
            return Response(
                {'error': 'нельзя изменять роль'},
                status=status.HTTP_400_BAD_REQUEST
            )

        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):

        if kwargs.get('pk') == 'me':
            return Response(
                {'error': 'просите админа'},
                status=status.HTTP_405_METHOD_NOT_ALLOWED
            )

        return super().destroy(request, *args, **kwargs)
