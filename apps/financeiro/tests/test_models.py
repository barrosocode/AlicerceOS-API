"""Testes de unidade — Módulo 1 Financeiro (docs/specs/finance_spec.md)."""

from datetime import timedelta
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from apps.core.models import Cliente, Parceiro, Projeto
from apps.financeiro.models import Entrada, Gasto, calcular_saldo


class SaldoTests(TestCase):
    def test_calcular_saldo_entradas_menos_saidas(self):
        cliente = Cliente.objects.create(nome="C", cpf_cnpj="1", contato="")
        p = Projeto.objects.create(
            nome="P",
            cliente=cliente,
            status=Projeto.Status.ATIVO,
        )
        hoje = timezone.localdate()
        Entrada.objects.create(
            projeto=p,
            categoria=Entrada.Categoria.PROJETO,
            valor=Decimal("1000.00"),
            data_transacao=hoje,
        )
        parceiro = Parceiro.objects.create(
            nome="Fornecedor",
            especialidade=Parceiro.Especialidade.OUTROS,
            telefone="",
        )
        Gasto.objects.create(
            projeto=p,
            categoria=Gasto.Categoria.MATERIAL,
            valor=Decimal("300.00"),
            parceiro=None,
            data_transacao=hoje,
        )
        Gasto.objects.create(
            projeto=p,
            categoria=Gasto.Categoria.MAO_DE_OBRA,
            valor=Decimal("200.00"),
            parceiro=parceiro,
            data_transacao=hoje,
        )
        saldo = calcular_saldo()
        self.assertEqual(saldo, Decimal("500.00"))


class DataTransacaoFuturaTests(TestCase):
    def test_entrada_data_futura_acima_de_365_dias_invalida(self):
        hoje = timezone.localdate()
        limite_ok = hoje + timedelta(days=365)
        limite_invalido = hoje + timedelta(days=366)
        Entrada(
            projeto=None,
            categoria=Entrada.Categoria.OUTROS,
            valor=Decimal("10.00"),
            data_transacao=limite_ok,
        ).full_clean()

        with self.assertRaises(ValidationError):
            Entrada(
                projeto=None,
                categoria=Entrada.Categoria.OUTROS,
                valor=Decimal("10.00"),
                data_transacao=limite_invalido,
            ).full_clean()

    def test_gasto_data_futura_acima_de_365_dias_invalida(self):
        hoje = timezone.localdate()
        limite_invalido = hoje + timedelta(days=366)
        with self.assertRaises(ValidationError):
            Gasto(
                projeto=None,
                categoria=Gasto.Categoria.FIXO,
                valor=Decimal("10.00"),
                parceiro=None,
                data_transacao=limite_invalido,
            ).full_clean()


class ObrigatoriedadeParceiroMaoDeObraTests(TestCase):
    def test_obrigatoriedade_parceiro_em_mao_de_obra(self):
        hoje = timezone.localdate()
        with self.assertRaises(ValidationError):
            Gasto(
                projeto=None,
                categoria=Gasto.Categoria.MAO_DE_OBRA,
                valor=Decimal("100.00"),
                parceiro=None,
                data_transacao=hoje,
            ).full_clean()


class TotalPorProjetoTests(TestCase):
    """finance_spec: soma de gastos do projeto X não inclui gastos do projeto Y."""

    def test_total_projeto_calculo(self):
        cliente = Cliente.objects.create(nome="C", cpf_cnpj="1", contato="")
        px = Projeto.objects.create(
            nome="X",
            cliente=cliente,
            status=Projeto.Status.ATIVO,
        )
        py = Projeto.objects.create(
            nome="Y",
            cliente=cliente,
            status=Projeto.Status.ATIVO,
        )
        hoje = timezone.localdate()
        Gasto.objects.create(
            projeto=px,
            categoria=Gasto.Categoria.MATERIAL,
            valor=Decimal("100.00"),
            parceiro=None,
            data_transacao=hoje,
        )
        Gasto.objects.create(
            projeto=py,
            categoria=Gasto.Categoria.MATERIAL,
            valor=Decimal("999.00"),
            parceiro=None,
            data_transacao=hoje,
        )
        qg_x = Gasto.objects.filter(projeto=px)
        qg_y = Gasto.objects.filter(projeto=py)
        self.assertEqual(
            calcular_saldo(queryset_entradas=Entrada.objects.none(), queryset_gastos=qg_x),
            Decimal("-100.00"),
        )
        self.assertEqual(
            calcular_saldo(queryset_entradas=Entrada.objects.none(), queryset_gastos=qg_y),
            Decimal("-999.00"),
        )


class VinculoLicenciamentoTests(TestCase):
    def test_vinculo_licenciamento_forca_categoria_licenca(self):
        hoje = timezone.localdate()
        g = Gasto(
            projeto=None,
            categoria=Gasto.Categoria.MATERIAL,
            valor=Decimal("50.00"),
            parceiro=None,
            data_transacao=hoje,
            vinculo_licenciamento=True,
        )
        g.full_clean()
        self.assertEqual(g.categoria, Gasto.Categoria.LICENCA)
