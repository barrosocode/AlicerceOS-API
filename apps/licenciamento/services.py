import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db.models import Q
from django.utils import timezone

from .models import Licenca, Notificacao

logger = logging.getLogger(__name__)


def licencas_criticas(ref_date=None):
    """Delega ao manager: licenças vencidas ou com vencimento em menos de 15 dias."""
    return Licenca.objects.criticas(ref_date=ref_date)


def contagem_criticas(ref_date=None) -> int:
    return licencas_criticas(ref_date=ref_date).count()


def _destinatarios_alertas():
    User = get_user_model()
    return User.objects.filter(Q(role__in=("admin", "gestor")) | Q(is_superuser=True))


def executar_verificacao_vencimentos() -> int:
    """
    RF08: varre licenças críticas com status efetivo Alerta/Expirada, registra Notificacao
    e simula envio (e-mail via EMAIL_BACKEND + log).
    Não cria nova notificação não lida para a mesma licença/destinatário no mesmo dia.
    """
    hoje = timezone.localdate()
    agora = timezone.now()
    usuarios = _destinatarios_alertas()
    criticas = Licenca.objects.criticas(ref_date=hoje).select_related("orgao", "projeto")
    criadas = 0

    for lic in criticas:
        if lic.status_efetivo not in (Licenca.Status.ALERTA, Licenca.Status.EXPIRADA):
            continue
        for user in usuarios:
            if not getattr(user, "email", None):
                continue
            if Notificacao.objects.filter(
                licenca=lic,
                destinatario=user,
                lida=False,
                data_envio__date=hoje,
            ).exists():
                continue
            Notificacao.objects.create(
                licenca=lic,
                destinatario=user,
                lida=False,
                data_envio=agora,
            )
            criadas += 1
            assunto = f"[Alicerce OS] Licença crítica: {lic.numero_processo}"
            corpo = (
                f"Processo: {lic.numero_processo}\n"
                f"Órgão: {lic.orgao}\n"
                f"Vencimento: {lic.data_vencimento}\n"
                f"Status efetivo: {lic.status_efetivo}\n"
                f"Dias para vencer: {lic.dias_para_vencer}\n"
            )
            try:
                send_mail(
                    assunto,
                    corpo,
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=True,
                )
            except Exception:
                logger.exception(
                    "Falha ao enviar e-mail de alerta (licenca=%s user=%s)",
                    lic.pk,
                    user.pk,
                )
            logger.info(
                "RF08 alerta registrado: licenca_id=%s destinatario=%s",
                lic.pk,
                user.email,
            )
    return criadas
