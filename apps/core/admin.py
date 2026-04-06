from django.contrib import admin

from .models import Cliente, OrcamentoItem, Parceiro, Projeto, RelatorioAtividade


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ("nome", "cpf_cnpj", "contato", "data_criacao")
    search_fields = ("nome", "cpf_cnpj")


@admin.register(Parceiro)
class ParceiroAdmin(admin.ModelAdmin):
    list_display = ("nome", "especialidade", "telefone")
    list_filter = ("especialidade",)


@admin.register(Projeto)
class ProjetoAdmin(admin.ModelAdmin):
    list_display = (
        "nome",
        "cliente",
        "status",
        "data_aprovacao",
        "data_inicio",
        "data_entrega_prevista",
    )
    list_filter = ("status",)


@admin.register(OrcamentoItem)
class OrcamentoItemAdmin(admin.ModelAdmin):
    list_display = ("descricao", "projeto", "tipo", "quantidade", "valor_unitario", "parceiro")
    list_filter = ("tipo",)


@admin.register(RelatorioAtividade)
class RelatorioAtividadeAdmin(admin.ModelAdmin):
    list_display = ("projeto", "tipo", "descricao")
    list_filter = ("tipo",)
