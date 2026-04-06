from django.contrib import admin

from .models import Entrada, Gasto


@admin.register(Entrada)
class EntradaAdmin(admin.ModelAdmin):
    list_display = ("categoria", "valor", "projeto", "data_transacao")
    list_filter = ("categoria",)


@admin.register(Gasto)
class GastoAdmin(admin.ModelAdmin):
    list_display = ("categoria", "valor", "projeto", "parceiro", "data_transacao", "vinculo_licenciamento")
    list_filter = ("categoria", "vinculo_licenciamento")
