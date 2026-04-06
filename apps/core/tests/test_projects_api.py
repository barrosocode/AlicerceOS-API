"""API — Módulo 2 (projetos, orçamento, progresso)."""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.core.models import Cliente, OrcamentoItem, Parceiro, Projeto
from apps.financeiro.models import Gasto


User = get_user_model()


def _bearer(user):
    return f"Bearer {RefreshToken.for_user(user).access_token}"


class ProjetosListagemProgressoAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="gestor@j.com",
            password="x",
            role="gestor",
        )
        cliente = Cliente.objects.create(nome="C", cpf_cnpj="1", contato="")
        self.projeto = Projeto.objects.create(
            nome="Obra",
            cliente=cliente,
            status=Projeto.Status.ATIVO,
            orcamento_estimado=Decimal("1000.00"),
        )
        Gasto.objects.create(
            projeto=self.projeto,
            categoria=Gasto.Categoria.MATERIAL,
            valor=Decimal("250.00"),
            parceiro=None,
            data_transacao="2026-04-01",
        )

    def test_list_projetos_inclui_progresso_e_gastos_reais(self):
        self.client.credentials(HTTP_AUTHORIZATION=_bearer(self.user))
        url = reverse("projeto-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        row = next(p for p in response.data if p["id"] == self.projeto.pk)
        self.assertEqual(row["gastos_reais_total"], "250.00")
        self.assertEqual(row["orcamento_estimado"], "1000.00")
        self.assertEqual(row["progresso_barra_percentual"], 25.0)


class OrcamentoItensAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="admin@j.com",
            password="x",
            role="admin",
        )
        cliente = Cliente.objects.create(nome="C", cpf_cnpj="1", contato="")
        self.projeto = Projeto.objects.create(nome="P", cliente=cliente)
        self.parceiro = Parceiro.objects.create(
            nome="P",
            especialidade=Parceiro.Especialidade.CIVIL,
            telefone="",
        )

    def test_post_orcamento_item_e_listagem_filtrada_por_projeto(self):
        self.client.credentials(HTTP_AUTHORIZATION=_bearer(self.user))
        url = reverse("orcamento-item-list")
        payload = {
            "projeto": self.projeto.pk,
            "parceiro": self.parceiro.pk,
            "descricao": "Serviço",
            "quantidade": "3",
            "valor_unitario": "100.00",
            "tipo": OrcamentoItem.Tipo.MAO_DE_OBRA,
        }
        r = self.client.post(url, payload, format="json")
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        self.assertEqual(str(r.data["subtotal"]), "300.00")

        r2 = self.client.get(url, {"projeto": self.projeto.pk})
        self.assertEqual(r2.status_code, status.HTTP_200_OK)
        self.assertEqual(len(r2.data), 1)


class StatusProjetoAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.colab = User.objects.create_user(
            email="c@j.com",
            password="x",
            role="colaborador",
        )
        self.gestor = User.objects.create_user(
            email="g@j.com",
            password="x",
            role="gestor",
        )
        cliente = Cliente.objects.create(nome="C", cpf_cnpj="1", contato="")
        self.projeto = Projeto.objects.create(nome="P", cliente=cliente, status=Projeto.Status.ORCAMENTO)

    def test_colaborador_nao_pode_patch_status_para_ativo(self):
        self.client.credentials(HTTP_AUTHORIZATION=_bearer(self.colab))
        url = reverse("projeto-detail", args=[self.projeto.pk])
        r = self.client.patch(url, {"status": Projeto.Status.ATIVO}, format="json")
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_gestor_pode_patch_status_para_ativo(self):
        self.client.credentials(HTTP_AUTHORIZATION=_bearer(self.gestor))
        url = reverse("projeto-detail", args=[self.projeto.pk])
        r = self.client.patch(url, {"status": Projeto.Status.ATIVO}, format="json")
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.projeto.refresh_from_db()
        self.assertEqual(self.projeto.status, Projeto.Status.ATIVO)
