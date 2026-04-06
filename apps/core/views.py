from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated

from .models import OrcamentoItem, Projeto, RelatorioAtividade
from .serializers import (
    OrcamentoItemSerializer,
    ProjetoSerializer,
    RelatorioAtividadeSerializer,
)


@extend_schema_view(
    list=extend_schema(
        summary="Listar projetos com indicadores de execução",
        description=(
            "Inclui `gastos_reais_total`, `progresso_barra_percentual`, `valor_total_orcamento_itens` e demais campos do projeto."
        ),
        tags=["Projetos (Módulo 2)"],
        responses={200: OpenApiTypes.OBJECT},
    ),
    retrieve=extend_schema(tags=["Projetos (Módulo 2)"]),
    update=extend_schema(tags=["Projetos (Módulo 2)"]),
    partial_update=extend_schema(
        summary="Atualizar projeto (ex.: status)",
        description="Transição para `ativo` exige perfil Admin ou Gestor (RBAC).",
        tags=["Projetos (Módulo 2)"],
        responses={200: OpenApiTypes.OBJECT, 400: OpenApiTypes.OBJECT},
    ),
)
class ProjetoViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    """Listagem com progresso (gastos reais vs. orçamento estimado) e atualização de status."""

    queryset = Projeto.objects.select_related("cliente").all()
    serializer_class = ProjetoSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["request"] = self.request
        return ctx


@extend_schema_view(
    list=extend_schema(
        tags=["Projetos (Módulo 2)"],
        parameters=[
            OpenApiParameter("projeto", OpenApiTypes.INT, OpenApiParameter.QUERY, required=False),
        ],
    ),
    retrieve=extend_schema(tags=["Projetos (Módulo 2)"]),
    create=extend_schema(tags=["Projetos (Módulo 2)"]),
    update=extend_schema(tags=["Projetos (Módulo 2)"]),
    partial_update=extend_schema(tags=["Projetos (Módulo 2)"]),
    destroy=extend_schema(tags=["Projetos (Módulo 2)"]),
)
class OrcamentoItemViewSet(viewsets.ModelViewSet):
    queryset = OrcamentoItem.objects.select_related("projeto", "parceiro").all()
    serializer_class = OrcamentoItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        projeto = self.request.query_params.get("projeto")
        if projeto:
            qs = qs.filter(projeto_id=projeto)
        return qs


@extend_schema_view(
    list=extend_schema(
        tags=["Projetos (Módulo 2)"],
        parameters=[
            OpenApiParameter("projeto", OpenApiTypes.INT, OpenApiParameter.QUERY, required=False),
        ],
    ),
    retrieve=extend_schema(tags=["Projetos (Módulo 2)"]),
    create=extend_schema(tags=["Projetos (Módulo 2)"]),
    update=extend_schema(tags=["Projetos (Módulo 2)"]),
    partial_update=extend_schema(tags=["Projetos (Módulo 2)"]),
    destroy=extend_schema(tags=["Projetos (Módulo 2)"]),
)
class RelatorioAtividadeViewSet(viewsets.ModelViewSet):
    queryset = RelatorioAtividade.objects.select_related("projeto").all()
    serializer_class = RelatorioAtividadeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        projeto = self.request.query_params.get("projeto")
        if projeto:
            qs = qs.filter(projeto_id=projeto)
        return qs
