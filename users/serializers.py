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
        password = validated_data.get('password')
        firsyt_name = validated_data.get('first_name')
        last_name = validated_data.get('last_name')
        
        if len(password) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        
        if not any(char.isdigit() for char in password):
            raise serializers.ValidationError("Password must contain at least one numeral.")
        
        if not any(char.isalpha() for char in password):
                raise serializers.ValidationError("Password must contain at least one letter.")
            
        if not any(char.isupper() for char in password):
            raise serializers.ValidationError("Password must contain at least one uppercase letter.")
        
        if not any(char.islower() for char in password):
            raise serializers.ValidationError("Password must contain at least one lowercase letter.")
        
        if not any(char in '!@#$%^&*()_+-=[]{}|;:,.<>?/' for char in password):
            raise serializers.ValidationError("Password must contain at least one special character.")
        
        if len(firsyt_name) < 2 or len(last_name) < 2:
            raise serializers.ValidationError("First name and last name must be at least 2 characters long.")
                    
        
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