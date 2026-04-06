from decimal import Decimal

from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.models import Sum
from rest_framework import serializers

from apps.financeiro.models import Gasto

from .models import OrcamentoItem, Projeto, RelatorioAtividade
from .project_permissions import assert_usuario_pode_definir_status_ativo


class OrcamentoItemSerializer(serializers.ModelSerializer):
    subtotal = serializers.ReadOnlyField()

    class Meta:
        model = OrcamentoItem
        fields = (
            "id",
            "projeto",
            "parceiro",
            "descricao",
            "quantidade",
            "valor_unitario",
            "tipo",
            "subtotal",
        )
        read_only_fields = ("subtotal",)


class RelatorioAtividadeSerializer(serializers.ModelSerializer):
    class Meta:
        model = RelatorioAtividade
        fields = ("id", "projeto", "tipo", "descricao", "fotos_url")


class ProjetoSerializer(serializers.ModelSerializer):
    valor_total_orcamento_itens = serializers.ReadOnlyField()
    gastos_reais_total = serializers.SerializerMethodField()
    progresso_barra_percentual = serializers.SerializerMethodField()
    percentual_gasto_sobre_orcamento = serializers.SerializerMethodField()

    class Meta:
        model = Projeto
        fields = (
            "id",
            "nome",
            "cliente",
            "status",
            "descricao_escopo",
            "data_aprovacao",
            "data_inicio",
            "data_entrega_prevista",
            "orcamento_estimado",
            "valor_total_orcamento_itens",
            "gastos_reais_total",
            "progresso_barra_percentual",
            "percentual_gasto_sobre_orcamento",
        )
        read_only_fields = (
            "valor_total_orcamento_itens",
            "gastos_reais_total",
            "progresso_barra_percentual",
            "percentual_gasto_sobre_orcamento",
        )

    def get_gastos_reais_total(self, obj):
        t = Gasto.objects.filter(projeto=obj).aggregate(s=Sum("valor"))["s"]
        return str(t if t is not None else Decimal("0"))

    def get_progresso_barra_percentual(self, obj):
        base = obj.orcamento_estimado
        if base is None or base <= 0:
            return None
        gastos = Gasto.objects.filter(projeto=obj).aggregate(s=Sum("valor"))["s"] or Decimal("0")
        pct = (gastos / base) * Decimal("100")
        if pct > 100:
            return float(Decimal("100"))
        return float(pct.quantize(Decimal("0.01")))

    def get_percentual_gasto_sobre_orcamento(self, obj):
        base = obj.orcamento_estimado
        if base is None or base <= 0:
            return None
        gastos = Gasto.objects.filter(projeto=obj).aggregate(s=Sum("valor"))["s"] or Decimal("0")
        pct = (gastos / base) * Decimal("100")
        return float(pct.quantize(Decimal("0.01")))

    def update(self, instance, validated_data):
        novo_status = validated_data.get("status", instance.status)
        if (
            novo_status == Projeto.Status.ATIVO
            and instance.status != Projeto.Status.ATIVO
        ):
            request = self.context.get("request")
            usuario = request.user if request else None
            try:
                assert_usuario_pode_definir_status_ativo(usuario)
            except DjangoValidationError as exc:
                raise serializers.ValidationError(exc.message_dict if hasattr(exc, "message_dict") and exc.message_dict else exc.messages) from exc
        return super().update(instance, validated_data)
