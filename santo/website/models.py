from django.db import models

# Create your models here.


class Produto(models.Model):
    class Meta:
        db_table = "produto"
    nome = models.CharField(max_length=50)
    tipo = models.CharField(max_length=20)
    valor = models.FloatField()
    estoque = models.FloatField()
    variacao_estoque = models.FloatField()


class Ingrediente(models.Model):
    class Meta:
        db_table = "ingrediente"
    nome = models.CharField(max_length=50)
    tipo = models.CharField(max_length=20)
    unidade = models.CharField(max_length=10)
    ultima_compra = models.DateField()
    estoque = models.FloatField()
    prazo_compra = models.IntegerField()
    total_comprado = models.FloatField()
    valor_comprado = models.FloatField()
    preco_medio = models.FloatField()
    variacao_estoque = models.FloatField()


class Quantidade(models.Model):
    class Meta:
        db_table = "quantidade"
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    ingrediente = models.ForeignKey(Ingrediente, on_delete=models.CASCADE)
    quantidade_receita = models.FloatField()
    quantidade_unitaria = models.FloatField()
    rendimento = models.FloatField()
    obs = models.CharField(max_length=30)


class Producao(models.Model):
    class Meta:
        db_table = "produção"
    data = models.DateField(auto_now_add=True)
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    quantidade = models.IntegerField()
    usuario = models.CharField(max_length=50)


class Bairro(models.Model):
    class Meta:
        db_table = "bairro"
    nome = models.CharField(max_length=60)
    delivery = models.FloatField()


class Cliente(models.Model):
    class Meta:
        db_table = "cliente"
    nome = models.CharField(max_length=60)
    telefone = models.CharField(max_length=20)
    tipo = models.CharField(max_length=2)
    endereco = models.CharField(max_length=50)
    bairro = models.ForeignKey(Bairro, on_delete=models.CASCADE)
    cidade = models.CharField(max_length=30)
    referencia = models.CharField(max_length=50)
    credito = models.FloatField()


class Fornecedor(models.Model):
    class Meta:
        db_table = "fornecedor"
    razao_social = models.CharField(max_length=60)
    nome = models.CharField(max_length=60)
    endereco = models.CharField(max_length=60)
    cidade = models.CharField(max_length=30)
    estado = models.CharField(max_length=30)
    tipo = models.CharField(max_length=5)
    cnpj = models.CharField(max_length=20)
    telefone = models.CharField(max_length=20)
    whatsapp = models.CharField(max_length=20)
    contato = models.CharField(max_length=60)


class Compra(models.Model):
    class Meta:
        db_table = "compra"
    fornecedor = models.ForeignKey(Fornecedor, on_delete=models.CASCADE)
    nota = models.FloatField()
    desconto = models.FloatField()
    imposto = models.FloatField()
    total = models.FloatField()
    data = models.DateField(auto_now_add=True)
    usuario = models.CharField(max_length=30)


class Pedido(models.Model):
    class Meta:
        db_table = "pedido"
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    total = models.FloatField()
    data = models.DateField(auto_now_add=True)
    hora = models.TimeField(auto_now_add=True)
    data_entrega = models.DateField()
    pago = models.BooleanField()
    entregue = models.BooleanField()
    delivery = models.BooleanField()
    delivery_valor = models.FloatField()
    debito = models.FloatField()
    desconto = models.FloatField()


class PedidoDetalhe(models.Model):
    class Meta:
        db_table = "pedido_detalhe"
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    quantidade = models.FloatField()
    valor_unitario = models.FloatField()
    total = models.FloatField()

