from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import DecimalField, ExpressionWrapper, F, Sum


class Cliente(models.Model):
    nome = models.CharField(max_length=255)
    cpf_cnpj = models.CharField(max_length=18)
    contato = models.CharField(max_length=255, blank=True)
    data_criacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("nome",)
        verbose_name = "cliente"
        verbose_name_plural = "clientes"

    def __str__(self):
        return self.nome


class Parceiro(models.Model):
    class Especialidade(models.TextChoices):
        ELETRICA = "eletrica", "Elétrica"
        CIVIL = "civil", "Civil"
        HIDRAULICA = "hidraulica", "Hidráulica"
        PINTURA = "pintura", "Pintura"
        OUTROS = "outros", "Outros"

    nome = models.CharField(max_length=255)
    especialidade = models.CharField(max_length=32, choices=Especialidade.choices)
    telefone = models.CharField(max_length=32, blank=True)

    class Meta:
        ordering = ("nome",)
        verbose_name = "parceiro"
        verbose_name_plural = "parceiros"

    def __str__(self):
        return self.nome


class Projeto(models.Model):
    class Status(models.TextChoices):
        ORCAMENTO = "orcamento", "Orçamento"
        ATIVO = "ativo", "Ativo"
        PAUSADO = "pausado", "Pausado"
        FINALIZADO = "finalizado", "Finalizado"

    nome = models.CharField(max_length=255)
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.PROTECT,
        related_name="projetos",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ORCAMENTO,
    )
    descricao_escopo = models.TextField(blank=True)
    data_aprovacao = models.DateField(null=True, blank=True)
    data_inicio = models.DateField(null=True, blank=True)
    data_entrega_prevista = models.DateField(null=True, blank=True)
    orcamento_estimado = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    class Meta:
        ordering = ("nome",)
        verbose_name = "projeto"
        verbose_name_plural = "projetos"

    def __str__(self):
        return self.nome

    @property
    def valor_total_orcamento_itens(self) -> Decimal:
        """Soma (quantidade × valor_unitario) dos itens de orçamento (RF05)."""
        agg = self.orcamento_itens.aggregate(
            s=Sum(
                ExpressionWrapper(
                    F("quantidade") * F("valor_unitario"),
                    output_field=DecimalField(max_digits=18, decimal_places=4),
                )
            )
        )
        return agg["s"] if agg["s"] is not None else Decimal("0")


class OrcamentoItem(models.Model):
    class Tipo(models.TextChoices):
        MATERIAL = "material", "Material"
        MAO_DE_OBRA = "mao_de_obra", "Mão de obra"

    projeto = models.ForeignKey(
        Projeto,
        on_delete=models.CASCADE,
        related_name="orcamento_itens",
    )
    parceiro = models.ForeignKey(
        Parceiro,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="orcamento_itens",
    )
    descricao = models.CharField(max_length=500)
    quantidade = models.DecimalField(max_digits=14, decimal_places=4)
    valor_unitario = models.DecimalField(max_digits=12, decimal_places=2)
    tipo = models.CharField(max_length=20, choices=Tipo.choices)

    class Meta:
        ordering = ("projeto", "id")
        verbose_name = "item de orçamento"
        verbose_name_plural = "itens de orçamento"

    def clean(self):
        super().clean()
        if self.tipo == self.Tipo.MAO_DE_OBRA and self.parceiro_id is None:
            raise ValidationError(
                {"parceiro": "Itens de mão de obra no orçamento exigem um parceiro vinculado."}
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def subtotal(self) -> Decimal:
        return (self.quantidade * self.valor_unitario).quantize(Decimal("0.01"))

    def __str__(self):
        return f"{self.descricao} ({self.get_tipo_display()})"


class RelatorioAtividade(models.Model):
    class Tipo(models.TextChoices):
        DIARIO = "diario", "Diário"
        SEMANAL = "semanal", "Semanal"

    projeto = models.ForeignKey(
        Projeto,
        on_delete=models.CASCADE,
        related_name="relatorios_atividade",
    )
    tipo = models.CharField(max_length=16, choices=Tipo.choices)
    descricao = models.TextField()
    fotos_url = models.TextField(
        blank=True,
        help_text="URLs das fotos (ex.: JSON ou uma URL por linha).",
    )

    class Meta:
        ordering = ("-id",)
        verbose_name = "relatório de atividade"
        verbose_name_plural = "relatórios de atividade"

    def __str__(self):
        return f"{self.get_tipo_display()} — {self.projeto_id}"
