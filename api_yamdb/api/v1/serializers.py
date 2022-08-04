from django.db.models import Avg
from rest_framework import serializers

from reviews.models import Category, Comments, Genre, Review, Title
from users.models import User


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        exclude = ['id']
        model = Category


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        exclude = ['id']
        model = Genre


class TitleSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(
        read_only=True,
        many=True
    )
    category = CategorySerializer(read_only=True)
    rating = serializers.IntegerField(required=False)

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'rating', 'description',
                  'genre', 'category')
        read_only_fields = ('id',)


class CreateTitleSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all()
    )
    genre = serializers.SlugRelatedField(
        many=True,
        slug_field='slug',
        queryset=Genre.objects.all(),
    )
    rating = serializers.SerializerMethodField()

    def get_rating(self, obj):
        try:
            rating = obj.reviews.aggregate(Avg('score'))
            return rating.get('score__avg')
        except TypeError:
            return None

    class Meta:
        fields = ('id', 'name', 'year', 'description',
                  'genre', 'category', 'rating')
        model = Title


class ReviewsSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )

    class Meta:
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        model = Review

    def validate(self, data):
        if self.context['request'].method != 'POST':
            return data

        title_id = self.context['view'].kwargs.get('title_id')
        author = self.context['request'].user
        if Review.objects.filter(
                author=author, title=title_id).exists():
            raise serializers.ValidationError(
                'Вы уже написали отзыв к этому произведению.'
            )

        return data


class CommentsSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )

    class Meta:
        fields = ('id', 'text', 'author', 'pub_date')
        model = Comments


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ("username", "email", "first_name",
                  "last_name", "bio", "role")
        model = User


class UserEditSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ("username", "email", "first_name",
                  "last_name", "bio", "role")
        model = User
        read_only_fields = ('role',)


class RegisterDataSerializer(serializers.Serializer):
    username = serializers.CharField(
        max_length=150,
        required=True
    )
    email = serializers.EmailField(
        max_length=150,
        required=True
    )

    def validate_username(self, username):
        if username.lower() == "me":
            raise serializers.ValidationError("Username 'me' is not valid")
        duplicated_username = User.objects.filter(
            username=username
        ).exists()
        if duplicated_username:
            raise serializers.ValidationError(
                'Пользователь с таким именем уже зарегистрирован'
            )
        return username

    def validate_email(self, email):
        duplicated_email = User.objects.filter(email=email).exists()
        if duplicated_email:
            raise serializers.ValidationError(
                'Пользователь с таким email уже зарегистрирован'
            )
        return email


class TokenSerializer(serializers.Serializer):
    username = serializers.RegexField(
        max_length=150,
        required=True,
        regex=r"^[\w.@+-]+\Z"
    )
    confirmation_code = serializers.CharField(required=True)
