from collections import defaultdict
from decimal import Decimal

from django.db.models import Sum

from apps.core.models import Projeto

from .models import Entrada, Gasto, calcular_saldo


def aplicar_filtros_transacoes(request, qs_entradas, qs_gastos):
    params = request.query_params
    projeto = params.get("projeto")
    if projeto:
        qs_entradas = qs_entradas.filter(projeto_id=projeto)
        qs_gastos = qs_gastos.filter(projeto_id=projeto)
    categoria = params.get("categoria")
    if categoria:
        qs_entradas = qs_entradas.filter(categoria=categoria)
        qs_gastos = qs_gastos.filter(categoria=categoria)
    start_date = params.get("start_date")
    if start_date:
        qs_entradas = qs_entradas.filter(data_transacao__gte=start_date)
        qs_gastos = qs_gastos.filter(data_transacao__gte=start_date)
    end_date = params.get("end_date")
    if end_date:
        qs_entradas = qs_entradas.filter(data_transacao__lte=end_date)
        qs_gastos = qs_gastos.filter(data_transacao__lte=end_date)
    return qs_entradas, qs_gastos


def montar_resumo_financeiro(qs_entradas, qs_gastos):
    saldo = calcular_saldo(qs_entradas, qs_gastos)

    ent_cat = {
        row["categoria"]: row["total"] or Decimal("0")
        for row in qs_entradas.values("categoria").annotate(total=Sum("valor"))
    }
    sai_cat = {
        row["categoria"]: row["total"] or Decimal("0")
        for row in qs_gastos.values("categoria").annotate(total=Sum("valor"))
    }

    por_projeto_map = defaultdict(lambda: {"entradas": Decimal("0"), "gastos": Decimal("0")})
    for row in qs_entradas.exclude(projeto_id=None).values("projeto_id").annotate(total=Sum("valor")):
        por_projeto_map[row["projeto_id"]]["entradas"] = row["total"] or Decimal("0")
    for row in qs_gastos.exclude(projeto_id=None).values("projeto_id").annotate(total=Sum("valor")):
        por_projeto_map[row["projeto_id"]]["gastos"] = row["total"] or Decimal("0")

    por_projeto = []
    for pid, totais in por_projeto_map.items():
        nome = Projeto.objects.filter(pk=pid).values_list("nome", flat=True).first() or ""
        ent = totais["entradas"]
        sai = totais["gastos"]
        por_projeto.append(
            {
                "projeto_id": pid,
                "projeto_nome": nome,
                "total_entradas": str(ent),
                "total_gastos": str(sai),
                "saldo": str(ent - sai),
            }
        )

    return {
        "saldo": str(saldo),
        "entradas_por_categoria": {k: str(v) for k, v in ent_cat.items()},
        "gastos_por_categoria": {k: str(v) for k, v in sai_cat.items()},
        "por_projeto": por_projeto,
    }
