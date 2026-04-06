from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import OrcamentoItemViewSet, ProjetoViewSet

router = DefaultRouter()
router.register(r"projetos", ProjetoViewSet, basename="projeto")
router.register(r"orcamento-itens", OrcamentoItemViewSet, basename="orcamento-item")

urlpatterns = [
    path("", include(router.urls)),
]
