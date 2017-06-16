from rest_framework import serializers


class UserFormSerializer (serializers.Serializer):
    user_name = serializers.CharField(max_length=20)
    user_password = serializers.CharField(max_length=20)


class ProducaoSerializer (serializers.Serializer):
    tipo = serializers.CharField(max_length=50, required=False)
    produto = serializers.CharField(max_length=50, required=False)
    quantidade = serializers.DecimalField(required=False, decimal_places=2, localize=True, max_digits=5)
    data_field = serializers.DateField(required=False)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super(ProducaoSerializer, self).__init__(*args, **kwargs)

    def validate(self, data):
        data = super().validate(data)
        print(data)
        if self.request.method == "POST":
            if not (data["produto"] and data["quantidade"]):
                raise serializers.ValidationError(
                    "Didn't input all fields for add."
                )
        elif self.request.method == "GET":
            if data["quantidade"]:
                raise serializers.ValidationError(
                    "Didn't input valid fields for filter."
                )
        return data


class EstoqueSerializer (serializers.Serializer):
    tipo = serializers.CharField(max_length=50)
    ingrediente = serializers.CharField(max_length=50, required=False)
    quantidade = serializers.DecimalField(required=False, decimal_places=3, localize=True, max_digits=5)
    data_field = serializers.DateField(required=False)
    valor = serializers.DecimalField(required=False, decimal_places=2, localize=True, max_digits=5)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super(ProducaoData, self).__init__(*args, **kwargs)

    def clean(self):
        validated_data = super(EstoqueSerializer, self).clean()
        tipo = validated_data.get("tipo")
        ingrediente = validated_data.get("ingrediente")
        quantidade = validated_data.get("quantidade")
        valor = validated_data.get("valor")

        if self.request.method == "add":
            if not (tipo and ingrediente and quantidade and valor):
                raise serializers.ValidationError(
                    "Didn't input all fields for add."
                )
        elif self.request.method == "filter":
            if quantidade or valor:
                raise serializers.ValidationError(
                    "Didn't input valid fields for filter."
                )


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