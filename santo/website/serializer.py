from rest_framework import serializers
import datetime


class UserFormSerializer (serializers.Serializer):
    user_name = serializers.CharField(max_length=20)
    user_password = serializers.CharField(max_length=20)


class ProducaoSerializer (serializers.Serializer):
    tipo = serializers.CharField(max_length=50, required=False, allow_blank=True)
    produto = serializers.CharField(max_length=50, required=False, allow_blank=True)
    quantidade = serializers.DecimalField(required=False, decimal_places=2, localize=True, max_digits=5)
    data_field = serializers.DateField(required=False, input_formats=["%d/%m/%Y"])
    action = serializers.CharField(max_length=10)

    def validate(self, data):
        print("test")
        data = super().validate(data)
        if data["action"] == "add":
            print(data)
            if not (data["produto"] and data["quantidade"]):
                raise serializers.ValidationError(
                    "Didn't input all fields for add."
                )
        elif data["action"] == "filter":
            print(data)
            if not (data["tipo"] or data["produto"] or data["data_field"]):
                raise serializers.ValidationError(
                    "Didn't input valid fields for filter."
                )
        return data


class EstoqueSerializer (serializers.Serializer):
    tipo = serializers.CharField(max_length=50, required=False)
    ingrediente = serializers.CharField(max_length=50, required=False)
    quantidade = serializers.DecimalField(required=False, decimal_places=3, localize=True, max_digits=5)
    data_field = serializers.DateField(required=False)
    valor = serializers.DecimalField(required=False, decimal_places=2, localize=True, max_digits=5)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super(EstoqueSerializer, self).__init__(*args, **kwargs)

    def validate(self, data):
        data = super().validate(data)

        if self.request.method == "add":
            if not (data["ingrediente"] and data["quantidade"] and data["valor"]):
                raise serializers.ValidationError(
                    "Didn't input all fields for add."
                )
        elif self.request.method == "filter":
            if data["quantidade"] or data["valor"]:
                raise serializers.ValidationError(
                    "Didn't input valid fields for filter."
                )
        return data


class ClienteSerializer (serializers.Serializer):
    nome = serializers.CharField(max_length=60)
    telefone = serializers.CharField(max_length=20, required=False)
    tipo = serializers.CharField(max_length=2, required=False)
    endereco = serializers.CharField(max_length=50, required=False)
    bairro = serializers.CharField(max_length=30, required=False)
    cidade = serializers.CharField(max_length=30)
    referencia = serializers.CharField(max_length=50, required=False)


class ClienteSearchSerializer (serializers.Serializer):
    nome = serializers.CharField(max_length=60, required=False)
    telefone = serializers.CharField(max_length=20, required=False)

    def validate(self, data):
        validated_data = super(ClienteSearchSerializer, self).validate(data)
        nome = validated_data.get("nome")
        telefone = validated_data.get("telefone")

        if not (nome or telefone):
            raise serializers.ValidationError(
                "Needs to input at least one field."
            )
        return validated_data


class ClienteSelectionSerializer (serializers.Serializer):
    cliente = serializers.IntegerField()


class Pedido (serializers.Serializer):
    tipo = serializers.CharField(max_length=50)
    produto = serializers.CharField(max_length=50)