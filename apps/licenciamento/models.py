from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.core.models import Projeto

# Janela crítica: vencimento em menos de 15 dias (0–14 dias) ou já vencida.
DIAS_JANELA_ALERTA = 15


class LicencaQuerySet(models.QuerySet):
    def criticas(self, ref_date=None):
        """
        Licenças críticas: já vencidas ou com vencimento em menos de 15 dias
        (data_vencimento <= hoje + 14 dias).
        """
        hoje = ref_date if ref_date is not None else timezone.localdate()
        limite = hoje + timedelta(days=DIAS_JANELA_ALERTA - 1)
        return self.filter(data_vencimento__lte=limite)


class LicencaManager(models.Manager.from_queryset(LicencaQuerySet)):
    pass


class OrgaoEmissor(models.Model):
    nome = models.CharField(max_length=255, unique=True)
    url_portal = models.URLField(blank=True)

    class Meta:
        ordering = ("nome",)
        verbose_name = "órgão emissor"
        verbose_name_plural = "órgãos emissores"

    def __str__(self):
        return self.nome


class Licenca(models.Model):
    class Status(models.TextChoices):
        PENDENTE = "pendente", "Pendente"
        APROVADO = "aprovado", "Aprovado"
        ALERTA = "alerta", "Alerta"
        EXPIRADA = "expirada", "Expirada"

    projeto = models.ForeignKey(
        Projeto,
        on_delete=models.CASCADE,
        related_name="licencas",
    )
    orgao = models.ForeignKey(
        OrgaoEmissor,
        on_delete=models.PROTECT,
        related_name="licencas",
    )
    numero_processo = models.CharField(max_length=128)
    data_protocolo = models.DateField(null=True, blank=True)
    data_vencimento = models.DateField()
    status = models.CharField(
        max_length=16,
        choices=Status.choices,
        default=Status.PENDENTE,
    )
    link_portal = models.URLField(blank=True)
    arquivo_pdf = models.FileField(upload_to="licencas/pdfs/", blank=True, null=True)

    objects = LicencaManager()

    class Meta:
        ordering = ("data_vencimento",)
        verbose_name = "licença"
        verbose_name_plural = "licenças"

    @property
    def dias_para_vencer(self) -> int:
        hoje = timezone.localdate()
        return (self.data_vencimento - hoje).days

    @property
    def status_efetivo(self) -> str:
        """
        Status derivado para exibição e alertas: vencida no passado → Expirada;
        vencimento em menos de 15 dias (e ainda não vencida) → Alerta;
        caso contrário, mantém o status persistido (Pendente/Aprovado/Alerta).
        """
        hoje = timezone.localdate()
        if self.data_vencimento < hoje:
            return self.Status.EXPIRADA
        if self.dias_para_vencer < DIAS_JANELA_ALERTA:
            return self.Status.ALERTA
        return self.status

    def __str__(self):
        return f"{self.numero_processo} ({self.orgao})"


class Notificacao(models.Model):
    """Registro de alertas RF08 (evita reenvio no mesmo dia se ainda não lidos)."""

    licenca = models.ForeignKey(
        Licenca,
        on_delete=models.CASCADE,
        related_name="notificacoes",
    )
    destinatario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notificacoes_licenciamento",
    )
    data_envio = models.DateTimeField(default=timezone.now)
    lida = models.BooleanField(default=False)

    class Meta:
        ordering = ("-data_envio",)
        verbose_name = "notificação"
        verbose_name_plural = "notificações"
        indexes = [
            models.Index(fields=("licenca", "destinatario", "lida", "data_envio")),
        ]

    def __str__(self):
        return f"Notif {self.licenca_id} → {self.destinatario_id}"
