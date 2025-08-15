# users/serializers.py

from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.validators import validate_email
from django.core.exceptions import ValidationError as DjangoValidationError

User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password']
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'username': {'required': True},
            'email': {'required': True},
            'password': {'write_only': True, 'required': True},
        }

    def create(self, validated_data):
        # Use create_user to ensure the password is hashed
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name'),
            last_name=validated_data.get('last_name')
        )
        return user

    def validate_email(self, value):
        try:
            validate_email(value)
        except DjangoValidationError:
            raise serializers.ValidationError("Enter a valid email address.")

        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")

        return value


# login users/serializers.py
def validate_username(value):
    # Check if it's a valid email
    try:
        validate_email(value)
    except DjangoValidationError:
        raise serializers.ValidationError("Enter a valid email address.")

    # Check if user exists
    if not User.objects.filter(email=value).exists():
        raise serializers.ValidationError("User with this email does not exist.")

    return value


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)