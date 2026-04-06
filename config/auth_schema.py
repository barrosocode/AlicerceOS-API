"""Views JWT com anotações OpenAPI (drf-spectacular)."""

from drf_spectacular.utils import extend_schema
from rest_framework import serializers
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


class _LoginRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(help_text="E-mail do usuário (login).")
    password = serializers.CharField(write_only=True, help_text="Senha.")


class _TokenPairResponseSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()


class _TokenRefreshRequestSerializer(serializers.Serializer):
    refresh = serializers.CharField(help_text="Refresh token JWT.")


class _TokenRefreshResponseSerializer(serializers.Serializer):
    access = serializers.CharField()


@extend_schema(
    summary="Autenticação JWT — obter tokens",
    description=(
        "Autenticação por e-mail e senha. Retorna `access` e `refresh`. "
        "O corpo utiliza **`email`** e **`password`** (USERNAME_FIELD do projeto)."
    ),
    tags=["Autenticação (Módulo 0)"],
    request=_LoginRequestSerializer,
    responses={200: _TokenPairResponseSerializer},
)
class SchemaTokenObtainPairView(TokenObtainPairView):
    pass


@extend_schema(
    summary="Renovar access token",
    description="Envia `refresh` válido para obter um novo `access`.",
    tags=["Autenticação (Módulo 0)"],
    request=_TokenRefreshRequestSerializer,
    responses={200: _TokenRefreshResponseSerializer},
)
class SchemaTokenRefreshView(TokenRefreshView):
    pass
