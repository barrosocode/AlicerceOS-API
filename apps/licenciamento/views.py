from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.financeiro.permissions import PodeVerResumoFinanceiroGlobal

from .models import Licenca, Notificacao, OrgaoEmissor
from .serializers import LicencaSerializer, NotificacaoSerializer, OrgaoEmissorSerializer
from .services import licencas_criticas


class OrgaoEmissorViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = OrgaoEmissor.objects.all()
    serializer_class = OrgaoEmissorSerializer
    permission_classes = [IsAuthenticated]


class LicencaViewSet(viewsets.ModelViewSet):
    queryset = Licenca.objects.select_related("projeto", "orgao").all()
    serializer_class = LicencaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        projeto = self.request.query_params.get("projeto")
        if projeto:
            qs = qs.filter(projeto_id=projeto)
        return qs


class LicenciamentoAlertasView(APIView):
    """Dashboard: apenas licenças críticas (Admin/Gestor)."""

    permission_classes = [IsAuthenticated, PodeVerResumoFinanceiroGlobal]

    def get(self, request):
        qs = licencas_criticas().select_related("projeto", "orgao")
        data = LicencaSerializer(qs, many=True).data
        return Response(
            {
                "total": len(data),
                "resultados": data,
            }
        )


class NotificacaoViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """Alertas RF08 do usuário (pendentes por padrão)."""

    serializer_class = NotificacaoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Notificacao.objects.filter(destinatario=self.request.user).select_related(
            "licenca",
            "licenca__orgao",
        )
        if self.request.query_params.get("todas") != "1":
            qs = qs.filter(lida=False)
        return qs

    @action(detail=True, methods=["patch"], url_path="ler")
    def ler(self, request, pk=None):
        notif = self.get_object()
        notif.lida = True
        notif.save(update_fields=["lida"])
        return Response(NotificacaoSerializer(notif).data, status=status.HTTP_200_OK)
