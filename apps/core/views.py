from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated

from .models import OrcamentoItem, Projeto
from .serializers import OrcamentoItemSerializer, ProjetoSerializer


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
