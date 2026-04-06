from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import FinanceiroResumoView, TransacaoViewSet

router = DefaultRouter()
router.register(r"transacoes", TransacaoViewSet, basename="financeiro-transacao")

urlpatterns = [
    path("resumo/", FinanceiroResumoView.as_view(), name="financeiro-resumo"),
    *router.urls,
]
