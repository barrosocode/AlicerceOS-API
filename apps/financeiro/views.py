from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Entrada, Gasto
from .permissions import PodeVerResumoFinanceiroGlobal
from .serializers import EntradaSerializer, GastoSerializer
from .services import aplicar_filtros_transacoes, montar_resumo_financeiro


@extend_schema(
    summary="Resumo financeiro agregado",
    description=(
        "RF04 — Agregação de entradas e saídas no período, com totais por categoria e por projeto. "
        "Disponível apenas para perfis autorizados (Admin/Gestor)."
    ),
    tags=["Financeiro (Módulo 1)"],
    parameters=[
        OpenApiParameter(
            name="start_date",
            type=OpenApiTypes.DATE,
            location=OpenApiParameter.QUERY,
            required=True,
            description="Início do período (YYYY-MM-DD).",
        ),
        OpenApiParameter(
            name="end_date",
            type=OpenApiTypes.DATE,
            location=OpenApiParameter.QUERY,
            required=True,
            description="Fim do período (YYYY-MM-DD).",
        ),
        OpenApiParameter(
            name="project_id",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            required=False,
            description="Filtrar por projeto.",
        ),
    ],
    responses={200: OpenApiTypes.OBJECT, 400: OpenApiTypes.OBJECT, 403: OpenApiTypes.OBJECT},
)
class FinanceiroResumoView(APIView):
    permission_classes = [IsAuthenticated, PodeVerResumoFinanceiroGlobal]

    def get(self, request):
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")
        if not start_date or not end_date:
            return Response(
                {"detail": "Parâmetros obrigatórios: start_date e end_date (YYYY-MM-DD)."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        project_id = request.query_params.get("project_id")
        qs_e = Entrada.objects.all()
        qs_g = Gasto.objects.all()
        if project_id:
            qs_e = qs_e.filter(projeto_id=project_id)
            qs_g = qs_g.filter(projeto_id=project_id)

        qs_e = qs_e.filter(data_transacao__gte=start_date, data_transacao__lte=end_date)
        qs_g = qs_g.filter(data_transacao__gte=start_date, data_transacao__lte=end_date)

        payload = montar_resumo_financeiro(qs_e, qs_g)
        payload["filtros"] = {
            "start_date": start_date,
            "end_date": end_date,
            "project_id": project_id,
        }
        return Response(payload)


@extend_schema_view(
    list=extend_schema(
        summary="Listar transações (entrada + saída)",
        description=(
            "Lista unificada de entradas e saídas. Cada item inclui `tipo`: `entrada` ou `saida`."
        ),
        tags=["Financeiro (Módulo 1)"],
        parameters=[
            OpenApiParameter("projeto", OpenApiTypes.INT, OpenApiParameter.QUERY, required=False),
            OpenApiParameter("categoria", OpenApiTypes.STR, OpenApiParameter.QUERY, required=False),
            OpenApiParameter("start_date", OpenApiTypes.DATE, OpenApiParameter.QUERY, required=False),
            OpenApiParameter("end_date", OpenApiTypes.DATE, OpenApiParameter.QUERY, required=False),
        ],
        responses={200: OpenApiTypes.OBJECT},
    ),
    create=extend_schema(
        summary="Criar transação",
        description='Corpo deve incluir `tipo`: `entrada` ou `saida` e os campos do serializer correspondente.',
        tags=["Financeiro (Módulo 1)"],
        request=OpenApiTypes.OBJECT,
        responses={201: OpenApiTypes.OBJECT, 400: OpenApiTypes.OBJECT},
    ),
)
class TransacaoViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        qs_e = Entrada.objects.all()
        qs_g = Gasto.objects.all()
        qs_e, qs_g = aplicar_filtros_transacoes(request, qs_e, qs_g)

        itens = []
        for e in qs_e.order_by("-data_transacao", "-id"):
            data = EntradaSerializer(e).data
            data["tipo"] = "entrada"
            itens.append(data)
        for g in qs_g.order_by("-data_transacao", "-id"):
            data = GastoSerializer(g).data
            data["tipo"] = "saida"
            itens.append(data)

        itens.sort(
            key=lambda x: (x["data_transacao"], x["tipo"], x["id"]),
            reverse=True,
        )
        return Response(itens)

    def create(self, request):
        tipo = request.data.get("tipo")
        body = {k: v for k, v in request.data.items() if k != "tipo"}
        if tipo == "entrada":
            serializer = EntradaSerializer(data=body)
        elif tipo == "saida":
            serializer = GastoSerializer(data=body)
        else:
            return Response(
                {"detail": 'Campo "tipo" deve ser "entrada" ou "saida".'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        out = dict(serializer.data)
        out["tipo"] = tipo
        return Response(out, status=status.HTTP_201_CREATED)
