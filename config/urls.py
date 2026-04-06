from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

from .auth_schema import SchemaTokenObtainPairView, SchemaTokenRefreshView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/token/", SchemaTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/auth/token/refresh/", SchemaTokenRefreshView.as_view(), name="token_refresh"),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    path("api/financeiro/", include("apps.financeiro.urls")),
    path("api/licenciamento/", include("apps.licenciamento.urls")),
    path("api/", include("apps.core.urls")),
]
