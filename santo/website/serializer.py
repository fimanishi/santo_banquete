from rest_framework import serializers
import datetime


class UserFormSerializer (serializers.Serializer):
    user_name = serializers.CharField(max_length=20)
    user_password = serializers.CharField(max_length=20)


class ProdutoSerializer (serializers.Serializer):
    id = serializers.IntegerField(required=False)
    produto = serializers.CharField(max_length=50, required=False, allow_blank=True)
    estoque = serializers.DecimalField(required=False, decimal_places=3, localize=True, max_digits=5)
    tipo = serializers.CharField(max_length=50, required=False, allow_blank=True)


class ProducaoSerializer (serializers.Serializer):
    id = serializers.IntegerField(required=False)
    data_output = serializers.DateField(required=False, format="%d/%m/%Y")
    tipo = serializers.CharField(max_length=50, required=False, allow_blank=True)
    produto = serializers.CharField(max_length=50, required=False, allow_blank=True)
    quantidade = serializers.DecimalField(required=False, decimal_places=2, localize=True, max_digits=5)
    data_field = serializers.DateField(required=False, input_formats=["%d/%m/%Y", ""])
    action = serializers.CharField(max_length=10, required=False)

    def validate(self, data):
        data = super().validate(data)
        try:
            if data["action"] == "add":
                if not (data["produto"] and data["quantidade"]):
                    raise serializers.ValidationError(
                        "Didn't input all fields for add."
                    )
            elif data["action"] == "filter":
                if not (data["tipo"] or data["produto"] or data["data_field"]):
                    raise serializers.ValidationError(
                        "Didn't input valid fields for filter."
                    )
        except KeyError:
            pass
        return data


class EstoqueSerializer (serializers.Serializer):
    id = serializers.IntegerField(required=False)
    data_output = serializers.DateField(required=False, format="%d/%m/%Y")
    tipo = serializers.CharField(max_length=50, required=False, allow_blank=True)
    ingrediente = serializers.CharField(max_length=50, required=False, allow_blank=True)
    quantidade = serializers.DecimalField(required=False, decimal_places=3, localize=True, max_digits=5)
    data_field = serializers.DateField(required=False, input_formats=["%d/%m/%Y", ""])
    action = serializers.CharField(max_length=10, required=False)
    valor = serializers.DecimalField(required=False, decimal_places=2, localize=True, max_digits=5)
    estoque = serializers.DecimalField(required=False, decimal_places=3, localize=True, max_digits=5)

    def validate(self, data):
        data = super().validate(data)
        try:
            if data["action"] == "add":
                if not (data["ingrediente"] and data["quantidade"] and data["valor"]):
                    raise serializers.ValidationError(
                        "Didn't input all fields for add."
                    )
            elif data["action"] == "filter":
                if not (data["tipo"] or data["ingrediente"] or data["data_field"] or data["quantidade"]):
                    raise serializers.ValidationError(
                        "Didn't input valid fields for filter."
                    )
        except KeyError:
            pass
        return data


class ClienteSerializer (serializers.Serializer):
    id = serializers.IntegerField(required=False)
    nome = serializers.CharField(max_length=60)
    telefone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    tipo = serializers.CharField(max_length=2, required=False, allow_blank=True)
    endereco = serializers.CharField(max_length=50, required=False, allow_blank=True)
    bairro = serializers.CharField(max_length=30, required=False, allow_blank=True)
    cidade = serializers.CharField(max_length=30)
    referencia = serializers.CharField(max_length=50, required=False, allow_blank=True)


class ClienteSearchSerializer (serializers.Serializer):
    nome = serializers.CharField(max_length=60, required=False, allow_blank=True)
    telefone = serializers.CharField(max_length=20, required=False, allow_blank=True)

    def validate(self, data):
        data = super().validate(data)

        if not (data["nome"] or data["telefone"]):
            raise serializers.ValidationError(
                "Needs to input at least one field."
            )
        return data


class ClienteSelectionSerializer (serializers.Serializer):
    cliente = serializers.IntegerField()


class PedidoSerializer (serializers.Serializer):
    produto = serializers.CharField(max_length=50)
    quantidade = serializers.DecimalField(decimal_places=2, localize=True, max_digits=5)


class ListPedidoSerializer (serializers.Serializer):
    cart = serializers.ListField()


class IdSerializer (serializers.Serializer):
    user_id = serializers.IntegerField()


class FornecedorSearchSerializer (serializers.Serializer):
    id = serializers.IntegerField(required=False)
    nome = serializers.CharField(max_length=60, required=False, allow_blank=True)
    contato = serializers.CharField(max_length=20, required=False, allow_blank=True)
    telefone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    tipo = serializers.CharField(max_length=2, required=False, allow_blank=True)
    endereco = serializers.CharField(max_length=50, required=False, allow_blank=True)
    estado = serializers.CharField(max_length=30, required=False, allow_blank=True)
    cidade = serializers.CharField(max_length=30, required=False, allow_blank=True)
    razao_social = serializers.CharField(max_length=60, required=False, allow_blank=True)
    cnpj = serializers.CharField(max_length=20, required=False, allow_blank=True)
    whatsapp = serializers.CharField(max_length=20, required=False, allow_blank=True)


class CompraSerializer (serializers.Serializer):
    id = serializers.IntegerField()
    nota = serializers.DecimalField(decimal_places=2, localize=True, max_digits=7)
    imposto = serializers.DecimalField(decimal_places=2, localize=True, max_digits=7)
    desconto = serializers.DecimalField(decimal_places=2, localize=True, max_digits=7)


class ConfirmSerializer (serializers.Serializer):
    confirm = serializers.CharField(max_length=10, required=False, allow_blank=True)