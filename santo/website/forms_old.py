from django import forms
from localflavor.br.forms import BRPhoneNumberField





class ProducaoData (forms.Form):
    tipo = forms.CharField(max_length=50)
    produto = forms.CharField(max_length=50, required=False)
    quantidade = forms.DecimalField(required=False)
    data_field = forms.DateField(required=False)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super(ProducaoData, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(ProducaoData, self).clean()
        tipo = cleaned_data.get("tipo")
        produto = cleaned_data.get("produto")
        quantidade = cleaned_data.get("quantidade")

        if self.request.method == "POST":
            if not (tipo and produto and quantidade):
                raise forms.ValidationError(
                    "Didn't input all fields for add."
                )
        elif self.request.method == "GET":
            if quantidade:
                raise forms.ValidationError(
                    "Didn't input valid fields for filter."
                )


class EstoqueData (forms.Form):
    tipo = forms.CharField(max_length=50)
    ingrediente = forms.CharField(max_length=50, required=False)
    quantidade = forms.DecimalField(required=False, decimal_places=3, localize=True)
    data_field = forms.DateField(required=False)
    valor = forms.DecimalField(required=False, decimal_places=2, localize=True)


    def clean(self):
        cleaned_data = super(EstoqueData, self).clean()
        tipo = cleaned_data.get("tipo")
        ingrediente = cleaned_data.get("ingrediente")
        quantidade = cleaned_data.get("quantidade")
        valor = cleaned_data.get("valor")

        if request.method == "add":
            if not (tipo and ingrediente and quantidade and valor):
                raise forms.ValidationError(
                    "Didn't input all fields for add."
                )
        elif button == "filter":
            if quantidade or valor:
                raise forms.ValidationError(
                    "Didn't input valid fields for filter."
                )


class ClienteData (forms.Form):
    nome = forms.CharField(max_length=60)
    telefone = forms.CharField(max_length=20, required=False)
    tipo = forms.CharField(max_length=2, required=False)
    endereco = forms.CharField(max_length=50, required=False)
    bairro = forms.CharField(max_length=30, required=False)
    cidade = forms.CharField(max_length=30)
    referencia = forms.CharField(max_length=50, required=False)


class ClienteSearch (forms.Form):
    nome = forms.CharField(max_length=60, required=False)
    telefone = forms.CharField(max_length=20, required=False)

    def clean(self):
        cleaned_data = super(ClienteSearch, self).clean()
        nome = cleaned_data.get("nome")
        telefone = cleaned_data.get("telefone")

        if not (nome or telefone):
            raise forms.ValidationError(
                "Needs to input at least one field."
            )


class ClienteSelection (forms.Form):
    cliente = forms.IntegerField()


class Pedido (forms.Form):
    tipo = forms.CharField(max_length=50)
    produto = forms.CharField(max_length=50)
    quantidade = forms.DecimalField()