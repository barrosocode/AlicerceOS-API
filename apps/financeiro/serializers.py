from rest_framework import serializers

from .models import Entrada, Gasto


class EntradaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Entrada
        fields = ("id", "projeto", "categoria", "valor", "data_transacao")


class GastoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gasto
        fields = (
            "id",
            "projeto",
            "categoria",
            "valor",
            "parceiro",
            "data_transacao",
            "vinculo_licenciamento",
            "licenca",
        )
