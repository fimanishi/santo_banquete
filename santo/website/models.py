from django.db import models

# Create your models here.


class Produto(models.Model):
    class Meta:
        db_table = "produto"
    nome = models.CharField(max_length=50)
    tipo = models.CharField(max_length=20)
    valor = models.FloatField()


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


class Cliente(models.Model):
    class Meta:
        db_table = "cliente"
    nome = models.CharField(max_length=60)
    telefone = models.CharField(max_length=20)
    tipo = models.CharField(max_length=2)
    endereco = models.CharField(max_length=50)
    bairro = models.CharField(max_length=30)
    cidade = models.CharField(max_length=30)
    referencia = models.CharField(max_length=50)
