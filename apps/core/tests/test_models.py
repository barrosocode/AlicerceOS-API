"""Testes alinhados a docs/specs/datamodel_spec.md (entidades base e integridade)."""

from datetime import date
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.core.models import Cliente, Parceiro, Projeto
from apps.financeiro.models import Gasto


class ClienteModelTests(TestCase):
    def test_campos_obrigatorios_e_data_criacao(self):
        c = Cliente.objects.create(nome="Obra Silva", cpf_cnpj="12.345.678/0001-90", contato="")
        c.refresh_from_db()
        self.assertEqual(c.nome, "Obra Silva")
        self.assertEqual(c.cpf_cnpj, "12.345.678/0001-90")
        self.assertIsNotNone(c.data_criacao)


class ParceiroModelTests(TestCase):
    def test_especialidade_deve_ser_choice_valida(self):
        p = Parceiro(nome="Elétrica Norte", especialidade=Parceiro.Especialidade.ELETRICA, telefone="")
        p.full_clean()
        p.save()

        with self.assertRaises(ValidationError):
            Parceiro(nome="X", especialidade="invalido", telefone="").full_clean()


class ProjetoModelTests(TestCase):
    def test_exige_cliente_e_status_padrao_orcamento(self):
        cliente = Cliente.objects.create(nome="Cliente A", cpf_cnpj="000", contato="")
        projeto = Projeto.objects.create(nome="Edifício Central", cliente=cliente)
        self.assertEqual(projeto.status, Projeto.Status.ORCAMENTO)
        self.assertEqual(projeto.cliente_id, cliente.id)


class IntegridadeGastoProjetoTests(TestCase):
    """Regra: excluir Projeto não exclui Gastos (SET_NULL no FK)."""

    def test_ao_deletar_projeto_gasto_permance_com_projeto_nulo(self):
        cliente = Cliente.objects.create(nome="C", cpf_cnpj="1", contato="")
        projeto = Projeto.objects.create(
            nome="P",
            cliente=cliente,
            status=Projeto.Status.ATIVO,
        )
        gasto = Gasto.objects.create(
            projeto=projeto,
            categoria=Gasto.Categoria.MATERIAL,
            valor=Decimal("100.00"),
            data_transacao=date.today(),
        )
        gid = gasto.id
        projeto.delete()
        gasto.refresh_from_db()
        self.assertEqual(gasto.id, gid)
        self.assertIsNone(gasto.projeto_id)


class IntegridadeMaoDeObraTests(TestCase):
    """Regra: Gasto categoria mão de obra exige Parceiro vinculado."""

    def test_mao_de_obra_sem_parceiro_falha_validacao(self):
        g = Gasto(
            projeto=None,
            categoria=Gasto.Categoria.MAO_DE_OBRA,
            valor=Decimal("500.00"),
            parceiro=None,
            data_transacao=date.today(),
        )
        with self.assertRaises(ValidationError):
            g.full_clean()

    def test_mao_de_obra_com_parceiro_valido(self):
        parceiro = Parceiro.objects.create(
            nome="Pedreiro Ltda",
            especialidade=Parceiro.Especialidade.CIVIL,
            telefone="",
        )
        g = Gasto(
            projeto=None,
            categoria=Gasto.Categoria.MAO_DE_OBRA,
            valor=Decimal("500.00"),
            parceiro=parceiro,
            data_transacao=date.today(),
        )
        g.full_clean()
        g.save()

