from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.financeiro.permissions import PodeVerResumoFinanceiroGlobal

from .models import Licenca, Notificacao, OrgaoEmissor
from .serializers import LicencaSerializer, NotificacaoSerializer, OrgaoEmissorSerializer
from .services import licencas_criticas


@extend_schema_view(
    list=extend_schema(tags=["Licenciamento (Módulo 3)"]),
    retrieve=extend_schema(tags=["Licenciamento (Módulo 3)"]),
)
class OrgaoEmissorViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = OrgaoEmissor.objects.all()
    serializer_class = OrgaoEmissorSerializer
    permission_classes = [IsAuthenticated]


@extend_schema_view(
    list=extend_schema(
        tags=["Licenciamento (Módulo 3)"],
        parameters=[
            OpenApiParameter("projeto", OpenApiTypes.INT, OpenApiParameter.QUERY, required=False),
        ],
    ),
    retrieve=extend_schema(tags=["Licenciamento (Módulo 3)"]),
    create=extend_schema(tags=["Licenciamento (Módulo 3)"]),
    update=extend_schema(tags=["Licenciamento (Módulo 3)"]),
    partial_update=extend_schema(tags=["Licenciamento (Módulo 3)"]),
    destroy=extend_schema(tags=["Licenciamento (Módulo 3)"]),
)
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


@extend_schema(
    summary="Painel de licenças críticas",
    tags=["Licenciamento (Módulo 3)"],
    responses={200: OpenApiTypes.OBJECT, 403: OpenApiTypes.OBJECT},
)
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


@extend_schema_view(
    list=extend_schema(
        tags=["Licenciamento (Módulo 3)"],
        parameters=[
            OpenApiParameter(
                "todas",
                OpenApiTypes.STR,
                OpenApiParameter.QUERY,
                required=False,
                description="Use `1` para incluir notificações já lidas.",
            ),
        ],
    ),
    retrieve=extend_schema(tags=["Licenciamento (Módulo 3)"]),
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

    @extend_schema(
        summary="Marcar notificação como lida",
        tags=["Licenciamento (Módulo 3)"],
        responses={200: OpenApiTypes.OBJECT},
    )
    @action(detail=True, methods=["patch"], url_path="ler")
    def ler(self, request, pk=None):
        notif = self.get_object()
        notif.lida = True
        notif.save(update_fields=["lida"])
        return Response(NotificacaoSerializer(notif).data, status=status.HTTP_200_OK)
