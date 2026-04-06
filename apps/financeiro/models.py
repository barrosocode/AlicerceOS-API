from datetime import timedelta
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Sum
from django.utils import timezone

from apps.core.models import Parceiro, Projeto

MAX_DIAS_TRANSACAO_FUTURA = 365


def validar_data_transacao_nao_alem_de_um_ano(data_transacao):
    if data_transacao is None:
        return
    hoje = timezone.localdate()
    limite = hoje + timedelta(days=MAX_DIAS_TRANSACAO_FUTURA)
    if data_transacao > limite:
        raise ValidationError(
            {
                "data_transacao": (
                    f"Não é permitido registrar transação com data além de "
                    f"{MAX_DIAS_TRANSACAO_FUTURA} dias no futuro."
                )
            }
        )


class Entrada(models.Model):
    """Registro de entradas de caixa (RF03)."""

    class Categoria(models.TextChoices):
        PROJETO = "projeto", "Projeto"
        INVESTIMENTO = "investimento", "Investimento"
        OUTROS = "outros", "Outros"

    projeto = models.ForeignKey(
        Projeto,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="entradas",
    )
    categoria = models.CharField(max_length=32, choices=Categoria.choices)
    valor = models.DecimalField(max_digits=12, decimal_places=2)
    data_transacao = models.DateField()

    class Meta:
        ordering = ("-data_transacao",)
        verbose_name = "entrada"
        verbose_name_plural = "entradas"

    def clean(self):
        super().clean()
        validar_data_transacao_nao_alem_de_um_ano(self.data_transacao)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Entrada — {self.valor}"


class Gasto(models.Model):
    """Saídas / gastos (RF03). Integridade com Projeto e Parceiro (datamodel)."""

    class Categoria(models.TextChoices):
        MATERIAL = "material", "Material"
        MAO_DE_OBRA = "mao_de_obra", "Mão de obra"
        LICENCA = "licenca", "Licença"
        FIXO = "fixo", "Fixo"
        OUTROS = "outros", "Outros"

    projeto = models.ForeignKey(
        Projeto,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="gastos",
    )
    categoria = models.CharField(max_length=32, choices=Categoria.choices)
    valor = models.DecimalField(max_digits=12, decimal_places=2)
    parceiro = models.ForeignKey(
        Parceiro,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="gastos",
    )
    data_transacao = models.DateField()
    vinculo_licenciamento = models.BooleanField(
        default=False,
        help_text="Se verdadeiro, a categoria é fixada em Licença (RF03).",
    )
    licenca = models.ForeignKey(
        "licenciamento.Licenca",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="gastos",
    )

    class Meta:
        ordering = ("-data_transacao",)
        verbose_name = "gasto"
        verbose_name_plural = "gastos"

    def clean(self):
        super().clean()
        if self.projeto_id:
            projeto = self.projeto
            if projeto.status == Projeto.Status.ORCAMENTO:
                raise ValidationError(
                    {
                        "projeto": (
                            "Não é permitido lançar gastos reais em projeto em fase de orçamento. "
                            "Ative o projeto após aprovação."
                        )
                    }
                )
        if self.vinculo_licenciamento:
            self.categoria = self.Categoria.LICENCA
        validar_data_transacao_nao_alem_de_um_ano(self.data_transacao)
        if self.categoria == self.Categoria.MAO_DE_OBRA and self.parceiro_id is None:
            raise ValidationError(
                {"parceiro": "Gastos do tipo mão de obra exigem um parceiro vinculado."}
            )
        if self.licenca_id:
            if not self.vinculo_licenciamento:
                raise ValidationError(
                    {
                        "licenca": (
                            "Associe uma licença apenas quando vinculo_licenciamento estiver ativo."
                        )
                    }
                )
            if self.projeto_id and self.licenca.projeto_id != self.projeto_id:
                raise ValidationError(
                    {"licenca": "A licença deve pertencer ao mesmo projeto do gasto."}
                )
            if not self.projeto_id:
                raise ValidationError(
                    {"licenca": "Informe o projeto ao vincular uma licença ao gasto."}
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Gasto — {self.valor}"


def calcular_saldo(queryset_entradas=None, queryset_gastos=None):
    """Saldo = soma das entradas − soma das saídas (RF03)."""
    qe = queryset_entradas if queryset_entradas is not None else Entrada.objects.all()
    qg = queryset_gastos if queryset_gastos is not None else Gasto.objects.all()
    total_ent = qe.aggregate(t=Sum("valor"))["t"] or Decimal("0")
    total_sai = qg.aggregate(t=Sum("valor"))["t"] or Decimal("0")
    return total_ent - total_sai
