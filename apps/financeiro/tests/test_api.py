"""Testes de integração — API Financeiro (docs/specs/finance_spec.md)."""

from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.core.models import Cliente, Parceiro, Projeto
from apps.financeiro.models import Entrada, Gasto


User = get_user_model()


def _bearer(user):
    token = RefreshToken.for_user(user)
    return f"Bearer {token.access_token}"


class FinanceiroResumoAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.gestor = User.objects.create_user(
            email="gestor@jell.com",
            password="senha-segura",
            role="gestor",
        )
        self.colaborador = User.objects.create_user(
            email="colab@jell.com",
            password="senha-segura",
            role="colaborador",
        )
        cliente = Cliente.objects.create(nome="Cliente", cpf_cnpj="1", contato="")
        self.projeto = Projeto.objects.create(
            nome="Obra Alfa",
            cliente=cliente,
            status=Projeto.Status.ATIVO,
        )
        self.hoje = timezone.localdate()
        self.inicio = (self.hoje - timedelta(days=7)).isoformat()
        self.fim = (self.hoje + timedelta(days=7)).isoformat()

    def test_get_financeiro_summary_filter(self):
        """Filtro de datas reduz o escopo do resumo (finance_spec)."""
        Gasto.objects.create(
            projeto=self.projeto,
            categoria=Gasto.Categoria.MATERIAL,
            valor=Decimal("100.00"),
            parceiro=None,
            data_transacao=self.hoje,
        )
        Gasto.objects.create(
            projeto=self.projeto,
            categoria=Gasto.Categoria.FIXO,
            valor=Decimal("999.00"),
            parceiro=None,
            data_transacao=self.hoje - timedelta(days=60),
        )
        self.client.credentials(HTTP_AUTHORIZATION=_bearer(self.gestor))
        url = reverse("financeiro-resumo")
        response = self.client.get(
            url,
            {"start_date": self.inicio, "end_date": self.fim, "project_id": self.projeto.pk},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["saldo"], str(Decimal("-100.00")))

    def test_unauthorized_access_colaborador_resumo(self):
        """Colaborador não acessa o resumo financeiro global (finance_spec)."""
        self.client.credentials(HTTP_AUTHORIZATION=_bearer(self.colaborador))
        url = reverse("financeiro-resumo")
        response = self.client.get(
            url,
            {"start_date": self.inicio, "end_date": self.fim},
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TransacoesFiltrosAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="admin@jell.com",
            password="senha-segura",
            role="admin",
        )
        cliente = Cliente.objects.create(nome="C", cpf_cnpj="1", contato="")
        self.p1 = Projeto.objects.create(
            nome="P1",
            cliente=cliente,
            status=Projeto.Status.ATIVO,
        )
        self.p2 = Projeto.objects.create(
            nome="P2",
            cliente=cliente,
            status=Projeto.Status.ATIVO,
        )
        self.hoje = timezone.localdate()
        Entrada.objects.create(
            projeto=self.p1,
            categoria=Entrada.Categoria.PROJETO,
            valor=Decimal("50.00"),
            data_transacao=self.hoje,
        )
        Gasto.objects.create(
            projeto=self.p1,
            categoria=Gasto.Categoria.MATERIAL,
            valor=Decimal("10.00"),
            parceiro=None,
            data_transacao=self.hoje,
        )
        Gasto.objects.create(
            projeto=self.p2,
            categoria=Gasto.Categoria.MATERIAL,
            valor=Decimal("999.00"),
            parceiro=None,
            data_transacao=self.hoje,
        )

    def test_list_transacoes_filtra_por_projeto(self):
        self.client.credentials(HTTP_AUTHORIZATION=_bearer(self.user))
        url = reverse("financeiro-transacao-list")
        response = self.client.get(url, {"projeto": self.p1.pk})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids_saida = [x["id"] for x in response.data if x["tipo"] == "saida"]
        self.assertEqual(len(ids_saida), 1)
        g = Gasto.objects.get(pk=ids_saida[0])
        self.assertEqual(g.projeto_id, self.p1.pk)

    def test_list_transacoes_filtra_por_categoria_e_intervalo(self):
        inicio = (self.hoje - timedelta(days=1)).isoformat()
        fim = (self.hoje + timedelta(days=1)).isoformat()
        self.client.credentials(HTTP_AUTHORIZATION=_bearer(self.user))
        url = reverse("financeiro-transacao-list")
        response = self.client.get(
            url,
            {"categoria": "material", "start_date": inicio, "end_date": fim},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for item in response.data:
            if item["tipo"] == "saida":
                self.assertEqual(item["categoria"], "material")
