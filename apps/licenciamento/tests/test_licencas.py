"""Módulo 3 — Licenciamento (TDD, datamodel + REQUIREMENTS)."""

from datetime import date, timedelta
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.core.models import Cliente, Projeto
from apps.financeiro.models import Gasto
from apps.licenciamento.models import DIAS_JANELA_ALERTA, Licenca, OrgaoEmissor


class StatusEfetivoVencidaTests(TestCase):
    def test_licenca_vencida_retorna_status_expirada_ou_alerta(self):
        cliente = Cliente.objects.create(nome="C", cpf_cnpj="1", contato="")
        projeto = Projeto.objects.create(
            nome="P",
            cliente=cliente,
            status=Projeto.Status.ATIVO,
        )
        orgao = OrgaoEmissor.objects.create(nome="IDEMA", url_portal="https://idema.rn.gov.br")
        lic = Licenca.objects.create(
            projeto=projeto,
            orgao=orgao,
            numero_processo="123",
            data_vencimento=date.today() - timedelta(days=5),
            status=Licenca.Status.PENDENTE,
        )
        self.assertIn(
            lic.status_efetivo,
            (Licenca.Status.EXPIRADA, Licenca.Status.ALERTA),
        )
        self.assertEqual(lic.status_efetivo, Licenca.Status.EXPIRADA)


class FiltroCriticasTests(TestCase):
    def test_filtro_licencas_criticas_retorna_apenas_escopo_correto(self):
        cliente = Cliente.objects.create(nome="C", cpf_cnpj="1", contato="")
        projeto = Projeto.objects.create(
            nome="P",
            cliente=cliente,
            status=Projeto.Status.ATIVO,
        )
        orgao = OrgaoEmissor.objects.create(nome="Bombeiros", url_portal="")
        ref = date(2026, 6, 15)
        limite_superior = ref + timedelta(days=DIAS_JANELA_ALERTA - 1)

        l_vencida = Licenca.objects.create(
            projeto=projeto,
            orgao=orgao,
            numero_processo="A",
            data_vencimento=ref - timedelta(days=1),
            status=Licenca.Status.APROVADO,
        )
        l_critica = Licenca.objects.create(
            projeto=projeto,
            orgao=orgao,
            numero_processo="B",
            data_vencimento=limite_superior,
            status=Licenca.Status.APROVADO,
        )
        l_ok = Licenca.objects.create(
            projeto=projeto,
            orgao=orgao,
            numero_processo="C",
            data_vencimento=limite_superior + timedelta(days=1),
            status=Licenca.Status.APROVADO,
        )

        qs = Licenca.objects.criticas(ref_date=ref)
        ids = set(qs.values_list("id", flat=True))
        self.assertEqual(ids, {l_vencida.id, l_critica.id})
        self.assertNotIn(l_ok.id, ids)


class GastoVinculoLicencaTests(TestCase):
    def test_gasto_com_vinculo_licenciamento_pode_associar_licenca(self):
        cliente = Cliente.objects.create(nome="C", cpf_cnpj="1", contato="")
        projeto = Projeto.objects.create(
            nome="P",
            cliente=cliente,
            status=Projeto.Status.ATIVO,
        )
        orgao = OrgaoEmissor.objects.create(nome="Prefeitura", url_portal="")
        lic = Licenca.objects.create(
            projeto=projeto,
            orgao=orgao,
            numero_processo="PROC-1",
            data_vencimento=date.today() + timedelta(days=60),
            status=Licenca.Status.PENDENTE,
        )
        g = Gasto.objects.create(
            projeto=projeto,
            categoria=Gasto.Categoria.LICENCA,
            valor=Decimal("200.00"),
            parceiro=None,
            data_transacao=date.today(),
            vinculo_licenciamento=True,
            licenca=lic,
        )
        self.assertEqual(g.licenca_id, lic.id)

    def test_gasto_sem_vinculo_nao_aceita_licenca(self):
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
            numero_processo="X",
            data_vencimento=date.today() + timedelta(days=30),
        )
        g = Gasto(
            projeto=projeto,
            categoria=Gasto.Categoria.MATERIAL,
            valor=Decimal("10.00"),
            parceiro=None,
            data_transacao=date.today(),
            vinculo_licenciamento=False,
            licenca=lic,
        )
        with self.assertRaises(ValidationError):
            g.full_clean()
