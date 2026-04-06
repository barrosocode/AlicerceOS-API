"""RF08 — alertas automáticos (engine + API)."""

from datetime import date, timedelta
from io import StringIO

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.core.models import Cliente, Projeto
from apps.licenciamento.models import Licenca, Notificacao, OrgaoEmissor
from apps.licenciamento.services import executar_verificacao_vencimentos

User = get_user_model()


def _bearer(user):
    return f"Bearer {RefreshToken.for_user(user).access_token}"


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    DEFAULT_FROM_EMAIL="test@alicerce.local",
)
class VerificacaoVencimentosEngineTests(TestCase):
    def setUp(self):
        self.cliente = Cliente.objects.create(nome="C", cpf_cnpj="1", contato="")
        self.projeto = Projeto.objects.create(
            nome="P",
            cliente=self.cliente,
            status=Projeto.Status.ATIVO,
        )
        self.orgao = OrgaoEmissor.objects.create(nome="IDEMA", url_portal="")
        self.admin = User.objects.create_user(
            email="admin@j.com",
            password="x",
            role="admin",
        )
        self.gestor = User.objects.create_user(
            email="gestor@j.com",
            password="x",
            role="gestor",
        )
        User.objects.create_user(
            email="colab@j.com",
            password="x",
            role="colaborador",
        )

    def test_comando_cria_notificacoes_apenas_para_licencas_alerta_ou_expirada(self):
        """Licença fora da janela crítica não gera notificação (status efetivo seguro)."""
        hoje = date.today()
        lic_segura = Licenca.objects.create(
            projeto=self.projeto,
            orgao=self.orgao,
            numero_processo="SAFE",
            data_vencimento=hoje + timedelta(days=120),
            status=Licenca.Status.APROVADO,
        )
        lic_alerta = Licenca.objects.create(
            projeto=self.projeto,
            orgao=self.orgao,
            numero_processo="CRIT",
            data_vencimento=hoje + timedelta(days=5),
            status=Licenca.Status.PENDENTE,
        )
        n = executar_verificacao_vencimentos()
        self.assertEqual(n, 2)
        self.assertFalse(Notificacao.objects.filter(licenca=lic_segura).exists())
        self.assertEqual(Notificacao.objects.filter(licenca=lic_alerta).count(), 2)

    def test_nao_duplica_notificacao_nao_lida_mesmo_dia(self):
        hoje = date.today()
        lic = Licenca.objects.create(
            projeto=self.projeto,
            orgao=self.orgao,
            numero_processo="DUP",
            data_vencimento=hoje + timedelta(days=3),
        )
        n1 = executar_verificacao_vencimentos()
        n2 = executar_verificacao_vencimentos()
        self.assertEqual(n1, 2)
        self.assertEqual(n2, 0)
        self.assertEqual(Notificacao.objects.filter(licenca=lic).count(), 2)

    def test_management_command_executa_engine(self):
        hoje = date.today()
        Licenca.objects.create(
            projeto=self.projeto,
            orgao=self.orgao,
            numero_processo="CMD",
            data_vencimento=hoje + timedelta(days=2),
        )
        out = StringIO()
        call_command("verificar_vencimentos", stdout=out)
        self.assertIn("Notificações criadas: 2", out.getvalue())

    def test_notificacoes_vao_apenas_para_admin_e_gestor(self):
        hoje = date.today()
        Licenca.objects.create(
            projeto=self.projeto,
            orgao=self.orgao,
            numero_processo="RBAC",
            data_vencimento=hoje + timedelta(days=1),
        )
        executar_verificacao_vencimentos()
        emails = set(Notificacao.objects.values_list("destinatario__email", flat=True))
        self.assertEqual(emails, {"admin@j.com", "gestor@j.com"})
        self.assertFalse(Notificacao.objects.filter(destinatario__email="colab@j.com").exists())


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    DEFAULT_FROM_EMAIL="test@alicerce.local",
)
class NotificacoesAPITests(TestCase):
    def setUp(self):
        self.api = APIClient()
        self.user = User.objects.create_user(
            email="g2@j.com",
            password="x",
            role="gestor",
        )
        cliente = Cliente.objects.create(nome="C", cpf_cnpj="2", contato="")
        projeto = Projeto.objects.create(
            nome="P2",
            cliente=cliente,
            status=Projeto.Status.ATIVO,
        )
        orgao = OrgaoEmissor.objects.create(nome="Bombeiros", url_portal="")
        lic = Licenca.objects.create(
            projeto=projeto,
            orgao=orgao,
            numero_processo="API-1",
            data_vencimento=date.today() + timedelta(days=4),
        )
        self.notif = Notificacao.objects.create(
            licenca=lic,
            destinatario=self.user,
            lida=False,
        )

    def test_get_lista_pendentes_e_patch_ler(self):
        self.api.credentials(HTTP_AUTHORIZATION=_bearer(self.user))
        url = reverse("notificacao-list")
        r = self.api.get(url)
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(len(r.data), 1)
        self.assertFalse(r.data[0]["lida"])

        url_ler = reverse("notificacao-ler", args=[self.notif.pk])
        r2 = self.api.patch(url_ler, {}, format="json")
        self.assertEqual(r2.status_code, status.HTTP_200_OK)
        self.assertTrue(r2.data["lida"])

        r3 = self.api.get(url)
        self.assertEqual(len(r3.data), 0)

        r4 = self.api.get(url, {"todas": "1"})
        self.assertEqual(len(r4.data), 1)
