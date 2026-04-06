from django.contrib import admin

from .models import Licenca, Notificacao, OrgaoEmissor


@admin.register(OrgaoEmissor)
class OrgaoEmissorAdmin(admin.ModelAdmin):
    list_display = ("nome", "url_portal")
    search_fields = ("nome",)


@admin.register(Notificacao)
class NotificacaoAdmin(admin.ModelAdmin):
    list_display = ("id", "licenca", "destinatario", "data_envio", "lida")
    list_filter = ("lida",)


@admin.register(Licenca)
class LicencaAdmin(admin.ModelAdmin):
    list_display = (
        "numero_processo",
        "orgao",
        "projeto",
        "data_vencimento",
        "status",
    )
    list_filter = ("status", "orgao")
