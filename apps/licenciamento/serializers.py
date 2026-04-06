from rest_framework import serializers

from .models import Licenca, Notificacao, OrgaoEmissor


class OrgaoEmissorSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrgaoEmissor
        fields = ("id", "nome", "url_portal")


class LicencaSerializer(serializers.ModelSerializer):
    dias_para_vencer = serializers.ReadOnlyField()
    status_efetivo = serializers.SerializerMethodField()
    orgao_nome = serializers.CharField(source="orgao.nome", read_only=True)

    class Meta:
        model = Licenca
        fields = (
            "id",
            "projeto",
            "orgao",
            "orgao_nome",
            "numero_processo",
            "data_protocolo",
            "data_vencimento",
            "status",
            "status_efetivo",
            "dias_para_vencer",
            "link_portal",
            "arquivo_pdf",
        )

    def get_status_efetivo(self, obj):
        return obj.status_efetivo


class NotificacaoSerializer(serializers.ModelSerializer):
    licenca_numero = serializers.CharField(source="licenca.numero_processo", read_only=True)
    status_efetivo_licenca = serializers.SerializerMethodField()
    dias_para_vencer_licenca = serializers.SerializerMethodField()

    class Meta:
        model = Notificacao
        fields = (
            "id",
            "licenca",
            "licenca_numero",
            "status_efetivo_licenca",
            "dias_para_vencer_licenca",
            "data_envio",
            "lida",
        )
        read_only_fields = ("data_envio", "lida")

    def get_status_efetivo_licenca(self, obj):
        return obj.licenca.status_efetivo

    def get_dias_para_vencer_licenca(self, obj):
        return obj.licenca.dias_para_vencer
