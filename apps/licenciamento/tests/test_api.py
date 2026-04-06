"""API — licenciamento (listagem + dashboard de alertas)."""

from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.core.models import Cliente, Projeto
from apps.licenciamento.models import DIAS_JANELA_ALERTA, Licenca, OrgaoEmissor


User = get_user_model()


def _bearer(user):
    return f"Bearer {RefreshToken.for_user(user).access_token}"


class LicenciamentoAlertasAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.gestor = User.objects.create_user(
            email="g@j.com",
            password="x",
            role="gestor",
        )
        self.colab = User.objects.create_user(
            email="c@j.com",
            password="x",
            role="colaborador",
        )
        cliente = Cliente.objects.create(nome="C", cpf_cnpj="1", contato="")
        self.projeto = Projeto.objects.create(
            nome="P",
            cliente=cliente,
            status=Projeto.Status.ATIVO,
        )
        orgao = OrgaoEmissor.objects.create(nome="IDEMA", url_portal="")
        hoje = date.today()
        self.l_critica = Licenca.objects.create(
            projeto=self.projeto,
            orgao=orgao,
            numero_processo="C1",
            data_vencimento=hoje + timedelta(days=5),
        )
        self.l_ok = Licenca.objects.create(
            projeto=self.projeto,
            orgao=orgao,
            numero_processo="C2",
            data_vencimento=hoje + timedelta(days=DIAS_JANELA_ALERTA + 10),
        )

    def test_alertas_retorna_apenas_criticas_para_gestor(self):
        self.client.credentials(HTTP_AUTHORIZATION=_bearer(self.gestor))
        url = reverse("licenciamento-alertas")
        r = self.client.get(url)
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        ids = {x["id"] for x in r.data["resultados"]}
        self.assertIn(self.l_critica.id, ids)
        self.assertNotIn(self.l_ok.id, ids)
        for item in r.data["resultados"]:
            self.assertIn("dias_para_vencer", item)
            self.assertIn("status_efetivo", item)

    def test_alertas_colaborador_403(self):
        self.client.credentials(HTTP_AUTHORIZATION=_bearer(self.colab))
        url = reverse("licenciamento-alertas")
        r = self.client.get(url)
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)


class LicencaListagemAPITests(TestCase):
    def test_list_licencas_inclui_dias_para_vencer_e_status_efetivo(self):
        client = APIClient()
        user = User.objects.create_user(email="a@j.com", password="x", role="admin")
        cliente = Cliente.objects.create(nome="C", cpf_cnpj="1", contato="")
        projeto = Projeto.objects.create(
            nome="P",
            cliente=cliente,
            status=Projeto.Status.ATIVO,
        )
        orgao = OrgaoEmissor.objects.create(nome="IDEMA", url_portal="")
        lic = Licenca.objects.create(
            projeto=projeto,
            orgao=orgao,
            numero_processo="L1",
            data_vencimento=date.today() + timedelta(days=3),
        )
        client.credentials(HTTP_AUTHORIZATION=_bearer(user))
        url = reverse("licenca-list")
        r = client.get(url)
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        row = next(x for x in r.data if x["id"] == lic.id)
        self.assertEqual(row["dias_para_vencer"], 3)
        self.assertEqual(row["status_efetivo"], Licenca.Status.ALERTA)
