from rest_framework.exceptions import ValidationError
from rest_framework.fields import CurrentUserDefault
from rest_framework.serializers import HyperlinkedModelSerializer, EmailField, CharField, ModelSerializer, Serializer

from users.models import User
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password


class UserSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = (
            "username",
        )


class UserRegisterSerializer(ModelSerializer):
    """Single purpose serializer used for User registration - added validation methods used"""

    # 1. Ensure username is unique
    username = CharField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    # 2. Ensure email is unique
    email = EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    # 3. Run passwords through the 'validate' function, to ensure equality
    password = CharField(
        write_only=True,
        required=True,
        validators=[validate_password]
    )

    password2 = CharField(
        write_only=True,
        required=True
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2',)

    def validate(self, attrs):
        """
        Function to check that passwords are the same
        """
        if attrs['password'] != attrs['password2']:
            raise ValidationError({"password": "Password fields didn't match."})

        return attrs

    def create(self, validated_data):
        """
        Save the user object, with a hashed password - safe to store in the db
        """

        # Create User
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
        )

        # Hash password by calling the set_password function
        user.set_password(validated_data['password'])
        user.save()

        return user


class PasswordUpdateSerializer(Serializer):
    """
    Simple serializer for password update endpoint.
    """

    model = User
    old_password = CharField(required=True)
    new_password = CharField(required=True)
