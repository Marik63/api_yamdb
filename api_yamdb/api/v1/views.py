from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.tokens import default_token_generator

from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.pagination import PageNumberPagination
from rest_framework import permissions, status, viewsets, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.mixins import (
    CreateModelMixin,
    DestroyModelMixin,
    ListModelMixin
)
from rest_framework.viewsets import GenericViewSet
from api_yamdb.settings import DEFAULT_FROM_EMAIL

from api.v1.permissions import (
    AdminOnly,
    AdminOrReadOnly,
    IsAdminModeratorAuthorOrReadOnly,
)
from api.v1.serializers import (
    CategorySerializer,
    CommentsSerializer,
    CreateTitleSerializer,
    GenreSerializer,
    RegisterDataSerializer,
    ReviewsSerializer,
    TitleSerializer,
    TokenSerializer,
    UserEditSerializer,
    UserSerializer
)

from reviews.models import Category, Genre, Review, Title
from users.models import User
from api.v1.filters import TitleFilter


class CategoryViewSet(CreateModelMixin, ListModelMixin,
                      DestroyModelMixin, GenericViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AdminOrReadOnly]
    pagination_class = PageNumberPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class GenresViewSet(CreateModelMixin, ListModelMixin,
                    DestroyModelMixin, GenericViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [AdminOrReadOnly]
    pagination_class = PageNumberPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class TitleViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete']
    permission_classes = [AdminOrReadOnly]
    pagination_class = PageNumberPagination
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_class = TitleFilter

    queryset = Title.objects.all().annotate(rating=Avg('reviews__score'))

    def get_serializer_class(self):
        if self.action in ('partial_update', 'create'):
            return CreateTitleSerializer
        return TitleSerializer


class ReviewsViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete']
    permission_classes = [
        IsAdminModeratorAuthorOrReadOnly,
        permissions.IsAuthenticatedOrReadOnly
    ]
    serializer_class = ReviewsSerializer

    def get_queryset(self):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete']
    permission_classes = [
        IsAdminModeratorAuthorOrReadOnly,
        permissions.IsAuthenticatedOrReadOnly
    ]
    serializer_class = CommentsSerializer

    def get_queryset(self):
        review = get_object_or_404(Review, id=self.kwargs.get('review_id'),
                                   title_id=self.kwargs.get('title_id'))
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(
            Review, id=self.kwargs.get('review_id'),
            title_id=self.kwargs.get('title_id')
        )
        serializer.save(author=self.request.user, review=review)


class UserViewSet(viewsets.ModelViewSet):
    """Класс пользователей."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AdminOnly,)
    search_fields = ('username',)
    lookup_field = "username"

    @action(
        methods=['GET', 'PATCH'],
        detail=False,
        url_path="me",
        permission_classes=[permissions.IsAuthenticated],
        serializer_class=UserEditSerializer,
    )
    def users_own_profile(self, request):
        """
        Функция обрабатывает 'GET' и 'PATCH' запросы на эндпоинт '/users/me/'
        """
        user = request.user
        if request.method == "GET":
            serializer = self.get_serializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)

        serializer = self.get_serializer(
            user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def register(request):
    """
    Функция обрабатывает POST-запрос для регистрации нового пользователя и
    получаения кода подтверждения, который необходим для получения JWT-токена.
    На вход подается 'username' и 'email', а в ответ происходит отправка
    на почту письма с кодом подтверждения.
    """
    serializer = RegisterDataSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    user, created = User.objects.get_or_create(
        username=serializer.validated_data["username"],
        email=serializer.validated_data["email"],
    )

    confirmation_code = default_token_generator.make_token(user)

    send_mail(
        subject="YaMDb registration",
        message=f"Your confirmation code: {confirmation_code}",
        from_email=DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
    )

    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def get_jwt_token(request):
    """
    Функция обрабатывает POST-запрос для получаения JWT-токена.
    На вход подается 'username' и 'confirmation_code',
    а в ответ формируется JWT-токен.
    """
    serializer = TokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = get_object_or_404(
        User,
        username=serializer.validated_data["username"]
    )

    if default_token_generator.check_token(
            user, serializer.validated_data["confirmation_code"]
    ):
        token = AccessToken.for_user(user)
        return Response({"token": str(token)}, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
