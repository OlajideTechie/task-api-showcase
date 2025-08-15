# users/views.py
from datetime import datetime
from django.contrib.auth import authenticate
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework_simplejwt.views import TokenRefreshView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.permissions import AllowAny

from .serializers import UserRegistrationSerializer, UserLoginSerializer

class RegisterView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="Register a new user",
        request_body=UserRegistrationSerializer,
        responses={
            201: openapi.Response(
                description="User created successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "first_name": openapi.Schema(type=openapi.TYPE_STRING, example="Jane"),
                        "last_name": openapi.Schema(type=openapi.TYPE_STRING, example="Doe"),
                        "username": openapi.Schema(type=openapi.TYPE_STRING, example="jane.doe"),
                        "email": openapi.Schema(type=openapi.TYPE_STRING, format="email", example="jane@example.com")
                    }
                ),
                examples={
                    "application/json": {
                        "first_name": "Jane",
                        "last_name": "Doe",
                        "username": "jane.doe",
                        "email": "jane@example.com",
                        'password': "test123"
                    }
                }
            )
        }
    )
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(self.get_serializer(user).data, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="Authenticate User",
        request_body=UserLoginSerializer,
        responses={
            200: openapi.Response(
                description="Access and refresh tokens",
                examples={
                    "application/json": {
                        "access": "access_token_string",
                        "refresh": "refresh_token_string",
                        "expire_at": "2025-12-31T23:59:59Z"
                    }
                }
            ),
            401: openapi.Response(description="Invalid credentials")
        }
    )
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = authenticate(
            username=serializer.validated_data['username'],
            password=serializer.validated_data['password']
        )

        if user:
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token

            expire_at = datetime.fromtimestamp(access_token['exp'])
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'expire_at': expire_at.isoformat()
            })

        return Response({'detail': 'Invalid username or password'}, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Logout a user (Blacklist refresh token)",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "refresh": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    title="Refresh Token",
                    description="JWT refresh token to be blacklisted"
                )
            },
            required=["refresh"]
        ),
        responses={
            205: openapi.Response(description="Logged out successfully"),
            400: openapi.Response(description="Invalid or expired refresh token")
        }
    )
    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response(
                {"detail": "Refresh token is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {"detail": "Logged out successfully"},
                status=status.HTTP_205_RESET_CONTENT
            )
        except TokenError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class CustomTokenRefreshView(TokenRefreshView):
    @swagger_auto_schema(
        operation_summary="Refresh access token using refresh token",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["refresh"],
            properties={
                "refresh": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    title="Refresh Token",
                    description="JWT refresh token used to get a new access token",
                    example="your-refresh-token"
                )
            }
        ),
        responses={
            200: openapi.Response(
                description="New access token and optionally a new refresh token",
                examples={
                    "application/json": {
                        "access": "new-access-token",
                        "refresh": "optional-new-refresh-token"  # Only returned if `ROTATE_REFRESH_TOKENS=True`
                    }
                }
            ),
            401: openapi.Response(description="Token is invalid or expired")
        }
    )
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)


        if response.status_code == 200 and 'access' in response.data:
            access_token = response.data['access']
            decoded = AccessToken(access_token)
            expire_at = datetime.fromtimestamp(decoded['exp']).isoformat()

            response.data['expire_at'] = expire_at

            #retruns refresh token in the response
            response.data['refresh'] = request.data.get('refresh')

        return response
