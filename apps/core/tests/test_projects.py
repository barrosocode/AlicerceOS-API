"""Módulo 2 — Projetos e orçamentos (REQUIREMENTS + datamodel)."""

from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.core.models import Cliente, OrcamentoItem, Parceiro, Projeto
from apps.core.project_permissions import assert_usuario_pode_definir_status_ativo
from apps.financeiro.models import Gasto

User = get_user_model()


class GastoProjetoOrcamentoTests(TestCase):
    """Cross-app: projeto em Orçamento não aceita gastos reais no financeiro."""

    def test_projeto_em_orcamento_bloqueia_gasto_real(self):
        cliente = Cliente.objects.create(nome="C", cpf_cnpj="1", contato="")
        projeto = Projeto.objects.create(nome="Obra", cliente=cliente, status=Projeto.Status.ORCAMENTO)
        g = Gasto(
            projeto=projeto,
            categoria=Gasto.Categoria.MATERIAL,
            valor=Decimal("50.00"),
            parceiro=None,
            data_transacao=date.today(),
        )
        with self.assertRaises(ValidationError):
            g.full_clean()


class ValorTotalOrcamentoItensTests(TestCase):
    def test_valor_total_orcamento_itens_soma_subtotais(self):
        cliente = Cliente.objects.create(nome="C", cpf_cnpj="1", contato="")
        projeto = Projeto.objects.create(nome="P", cliente=cliente)
        parceiro = Parceiro.objects.create(
            nome="Pedreiro",
            especialidade=Parceiro.Especialidade.CIVIL,
            telefone="",
        )
        OrcamentoItem.objects.create(
            projeto=projeto,
            parceiro=None,
            descricao="Cimento",
            quantidade=Decimal("10"),
            valor_unitario=Decimal("30.00"),
            tipo=OrcamentoItem.Tipo.MATERIAL,
        )
        OrcamentoItem.objects.create(
            projeto=projeto,
            parceiro=parceiro,
            descricao="Alvenaria",
            quantidade=Decimal("2"),
            valor_unitario=Decimal("150.00"),
            tipo=OrcamentoItem.Tipo.MAO_DE_OBRA,
        )
        self.assertEqual(projeto.valor_total_orcamento_itens, Decimal("600.00"))


class PermissaoStatusAtivoTests(TestCase):
    def test_apenas_admin_ou_gestor_podem_definir_status_ativo(self):
        colab = User.objects.create_user(
            email="c@j.com",
            password="x",
            role="colaborador",
        )
        gestor = User.objects.create_user(
            email="g@j.com",
            password="x",
            role="gestor",
        )
        with self.assertRaises(ValidationError):
            assert_usuario_pode_definir_status_ativo(colab)
        assert_usuario_pode_definir_status_ativo(gestor)
