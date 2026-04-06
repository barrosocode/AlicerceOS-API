from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    LicencaViewSet,
    LicenciamentoAlertasView,
    NotificacaoViewSet,
    OrgaoEmissorViewSet,
)

router = DefaultRouter()
router.register(r"orgaos", OrgaoEmissorViewSet, basename="orgao-emissor")
router.register(r"licencas", LicencaViewSet, basename="licenca")
router.register(r"notificacoes", NotificacaoViewSet, basename="notificacao")

urlpatterns = [
    path("alertas/", LicenciamentoAlertasView.as_view(), name="licenciamento-alertas"),
    path("", include(router.urls)),
]
