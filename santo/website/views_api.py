from django.template.response import TemplateResponse
import website.forms
import website.serializer
from django import forms
from django import http
# from django.core.mail import send_mail
# from django.core.mail import EmailMessage
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth import logout, login
import website.models as models
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from datetime import date
from django.core.exceptions import ObjectDoesNotExist
import re
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from decimal import *
import copy


# Create your views here.


# page to add a new client. does the verification of the fields and adds to the database
# required inputs: nome completo and cidade
@api_view(["POST"])
@login_required
def cliente_add(request):
    if request.method == "POST":
        # gets nome, telefone, tipo, endereco, bairro, cidade e referencia from the ClientData form
        serializer = website.serializer.ClienteSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            # checks against the Cliente database to see if a client with nome already exists
            exist_check = models.Cliente.objects.filter(nome=serializer.validated_data["nome"].lower())
            # if client exists
            if exist_check:
                # loops through all clients that have nome as nome
                for each in exist_check:
                    # if a client with nome and the telefone from the form already exists, display message
                    if each.telefone == serializer.validated_data["telefone"]:
                        user_json = {"id": each.id, "nome": each.nome.title()}
                        request.session["cart_user"] = user_json
                        request.session.save()
                        return Response({"id": each.id, "nome": each.nome, "message": "exists"})
                    else:
                        # if the client is in the db but has a different phone number, adds a new instance to the db
                        models.Cliente.objects.create(nome=serializer.validated_data["nome"].lower(),
                                                      telefone=serializer.validated_data["telefone"],
                                                      tipo=serializer.validated_data["tipo"],
                                                      endereco=serializer.validated_data["endereco"].lower(),
                                                      bairro=models.Bairro.objects.get(
                                                          nome=serializer.validated_data["bairro"]),
                                                      cidade=serializer.validated_data["cidade"].lower(),
                                                      referencia=serializer.validated_data["referencia"].lower(),
                                                      credito=0)
                        # gets the id from the new client. this id will be passed to next view
                        client = models.Cliente.objects.last()
                        user_json = {"id": client.id, "nome": client.nome.title()}
                        request.session["cart_user"] = user_json
                        request.session.save()
                        return Response({"id": client.id, "nome": client.nome.title(), "message": "added"})
            else:
                # if the client is in the db but has a different phone number, adds a new instance to the db
                models.Cliente.objects.create(nome=serializer.validated_data["nome"].lower(),
                                              telefone=serializer.validated_data["telefone"],
                                              tipo=serializer.validated_data["tipo"],
                                              endereco=serializer.validated_data["endereco"].lower(),
                                              bairro=models.Bairro.objects.get(
                                                  nome=serializer.validated_data["bairro"]),
                                              cidade=serializer.validated_data["cidade"].lower(),
                                              referencia=serializer.validated_data["referencia"].lower(),
                                              credito=0)
                # gets the id from the new client. this id will be passed to next view
                client = models.Cliente.objects.last()
                user_json = {"id": client.id, "nome": client.nome.title()}
                request.session["cart_user"] = user_json
                request.session.save()
                return Response({"id": client.id, "nome": client.nome.title(), "message": "added"})


@api_view(["POST"])
@login_required
def fornecedor_add(request):
    if request.method == "POST":
        serializer = website.serializer.FornecedorSearchSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            # checks against the Cliente database to see if a supplier with nome already exists
            try:
                exist_check = models.Fornecedor.objects.get(nome=serializer.validated_data["nome"].lower())
                user_json = {"id": exist_check.id, "nome": exist_check.nome.title()}
                request.session["cart_user"] = user_json
                request.session.save()
                return Response({"id": exist_check.id, "nome": exist_check.nome, "message": "exists"})
            except ObjectDoesNotExist:
                # if the client is in the db but has a different phone number, adds a new instance to the db
                models.Fornecedor.objects.create(nome=serializer.validated_data["nome"].lower(),
                                              razao_social=serializer.validated_data["razao_social"].lower(),
                                              contato=serializer.validated_data["contato"].lower(),
                                              telefone=serializer.validated_data["telefone"],
                                              whatsapp=serializer.validated_data["whatsapp"],
                                              cnpj=serializer.validated_data["cnpj"],
                                              tipo=serializer.validated_data["tipo"],
                                              endereco=serializer.validated_data["endereco"].lower(),
                                              estado=serializer.validated_data["estado"].lower(),
                                              cidade=serializer.validated_data["cidade"].lower())
                # gets the id from the new client. this id will be passed to next view
                supplier = models.Fornecedor.objects.last()
                user_json = {"id": supplier.id, "nome": supplier.nome.title()}
                request.session["cart_user"] = user_json
                request.session.save()
                return Response({"id": supplier.id, "nome": supplier.nome.title(), "message": "added"})


@api_view(["POST"])
@login_required
def finalizar_pedido_delivery_update(request):
    if request.method == "POST":
        serializer = website.serializer.DeliverySerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            request.session["delivery_boolean"] = serializer.validated_data["boolean"]
            if request.session["delivery"] == 0:
                request.session["delivery"] = float(serializer.validated_data["valor"])
                request.session["cart_total"] += float(serializer.validated_data["valor"])
            else:
                request.session["cart_total"] += float(serializer.validated_data["valor"]) - request.session["delivery"]
                request.session["delivery"] = float(serializer.validated_data["valor"])
            request.session.save()
            s = website.serializer.DeliverySerializer({"valor": request.session["cart_total"]})
            return Response(s.data)


@api_view(["POST"])
@login_required
def finalizar_pedido_desconto(request):
    if request.method == "POST":
        serializer = website.serializer.DeliverySerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            net = request.session["desconto"] - float(serializer.validated_data["valor"])
            request.session["cart_total"] += net
            request.session["desconto"] = float(serializer.validated_data["valor"])
            request.session.save()
            s = website.serializer.DeliverySerializer({"valor": request.session["cart_total"]})
            return Response(s.data)


@api_view(["POST"])
@login_required
def finalizar_pedido_finish(request):
    if request.method == "POST":
        print("pass1")
        serializer = website.serializer.DataSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            print("pass2")
            if len(request.session["cart"]) > 0:
                cliente = models.Cliente.objects.get(id=request.session["cart_user"]["id"])
                if cliente.credito > 0:
                    credito = cliente.credito
                else:
                    credito = 0
                cliente.credito -= Decimal(request.session["cart_total"])
                cliente.save()
                models.Pedido.objects.create(cliente=models.Cliente.objects.get(id=request.session["cart_user"]["id"]),
                                             total=request.session["cart_total"],
                                             delivery=request.session["delivery_boolean"],
                                             delivery_valor=request.session["delivery"],
                                             data_entrega=serializer.validated_data["data"],
                                             pago=False,
                                             entregue=False,
                                             debito=request.session["cart_total"] - float(credito),
                                             desconto=request.session["desconto"],
                                             )
                pedido = models.Pedido.objects.last()
                for item in request.session["cart"]:
                    produto = models.Produto.objects.get(nome=item["produto"])
                    produto.estoque -= Decimal(item["quantidade"])
                    produto.save()
                    models.PedidoDetalhe.objects.create(pedido=pedido,
                                                 produto=produto,
                                                 quantidade=item["quantidade"],
                                                 valor_unitario=item["valor"],
                                                 total=item["total"])
                return Response("success")
            else:
                return Response("failure")


@api_view(["POST"])
@login_required
def escolher_cliente_filter(request):
    filtered = []
    filtered_json = []
    # if the current view was the referer
    if request.method == "POST":
        # gets cliente from ClienteSearch form
        serializer = website.serializer.ClienteSearchSerializer(data=request.data)
        print(serializer)
        if serializer.is_valid(raise_exception=True):
            # if the user inputs nome and telefone, filters for a match for both
            if serializer.validated_data["nome"] and serializer.validated_data["telefone"]:
                filtered = models.Cliente.objects.filter(nome__icontains=serializer.validated_data["nome"],
                                                         telefone=serializer.validated_data["telefone"]).order_by(
                                                        "nome")
            elif serializer.validated_data["nome"] and serializer.validated_data["referencia"]:
                filtered = models.Cliente.objects.filter(nome__icontains=serializer.validated_data["nome"],
                                                         referencia__icontains=serializer.validated_data[
                                                             "referencia"]).order_by("nome")
            # if the user inputs nome, filters for a match that contains nome
            elif serializer.validated_data["nome"]:
                filtered = models.Cliente.objects.filter(nome__icontains=serializer.validated_data["nome"]).order_by(
                                                        "nome")
            # if the user inputs telefone, filters for a match for the telefone
            elif serializer.validated_data["telefone"]:
                filtered = models.Cliente.objects.filter(telefone=serializer.validated_data["telefone"]).order_by(
                                                        "nome")
            elif serializer.validated_data["referencia"]:
                filtered = models.Cliente.objects.filter(
                    referencia__icontains=serializer.validated_data["referencia"]).order_by("nome")
            if filtered:
                for i in filtered:
                    filtered_json.append({"id": i.id, "nome": i.nome.title(), "telefone": i.telefone,
                                          "endereco": i.endereco.title(), "bairro": i.bairro,
                                          "cidade": i.cidade.title()})
                s = website.serializer.ClienteSerializer(filtered_json, many=True)
                return Response(s.data)
            else:
                return Response("empty")


@api_view(["POST"])
@login_required
def escolher_fornecedor_filter(request):
    filtered = []
    filtered_json = []
    # if the current view was the referer
    if request.method == "POST":
        # gets cliente from ClienteSearch form
        serializer = website.serializer.FornecedorSearchSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            # if the user inputs nome and telefone, filters for a match for both
            if serializer.validated_data["nome"] and serializer.validated_data["contato"]:
                filtered = models.Fornecedor.objects.filter(nome__icontains=serializer.validated_data["nome"],
                                                            contato__icontains=serializer.validated_data[
                                                                "contato"]).order_by("nome")
            # if the user inputs nome, filters for a match that contains nome
            elif serializer.validated_data["nome"]:
                filtered = models.Fornecedor.objects.filter(nome__icontains=serializer.validated_data[
                    "nome"]).order_by("nome")
            # if the user inputs telefone, filters for a match for the telefone
            elif serializer.validated_data["contato"]:
                filtered = models.Fornecedor.objects.filter(contato__icontains=serializer.validated_data[
                    "contato"]).order_by("nome")
            if filtered:
                for i in filtered:
                    filtered_json.append({"id": i.id, "nome": i.nome.title(), "telefone": i.telefone,
                                          "endereco": i.endereco.title(), "estado": i.estado.upper(),
                                          "cidade": i.cidade.title(), "contato": i.contato.title()})
                s = website.serializer.FornecedorSearchSerializer(filtered_json, many=True)
                return Response(s.data)
            else:
                return Response("empty")


@api_view(["POST"])
@login_required
def producao_add(request):
    if request.method == "POST":
        # gets tipo, produto and quantidade from ProducaoData form
        serializer = website.serializer.ProducaoSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            # gets the id of the produto selected on the form
            product_id = models.Produto.objects.get(nome=serializer.validated_data["produto"])
            product_id.estoque += serializer.validated_data["quantidade"]
            product_id.save()
            # filters the Quantidade model for items that have the id of the selected produto
            quantidades = models.Quantidade.objects.filter(produto_id=product_id.id)
            # loops through the filtererd elements
            for quantidade in quantidades:
                # gets that item from the db
                quantidade_get = models.Quantidade.objects.get(id=quantidade.id)
                # gets the item from the Ingrediente model using the relational quantidade_id
                ingredient_to_change = models.Ingrediente.objects.get(id=quantidade_get.ingrediente_id)
                # subtracts from the estoque of that item the quantidade_unitaria for the product times the quantidade
                ingredient_to_change.estoque -= quantidade_get.quantidade_unitaria * serializer.validated_data[
                    "quantidade"]
                # saves the Ingrediente db
                ingredient_to_change.save()
            # checks to see if the produto was already added to the producao today
            try:
                # gets the item
                check = models.Producao.objects.get(produto_id=product_id.id, data=date.today())
                # adds to the previous quantidade the quantidade input by the user
                check.quantidade += serializer.validated_data["quantidade"]
                # saves the Producao db
                check.save()
            # if this produto was not added to the producao today
            except ObjectDoesNotExist:
                # adds the produto produced to the Producao model
                models.Producao.objects.create(produto=product_id,
                                               quantidade=serializer.validated_data["quantidade"], usuario=request.user)
            # produto was either update or added successfully
            return Response("added")
        else:
            # request was invalid. displays message to the user
            return Response(3)


# to be commented
@api_view(["POST"])
@login_required
def producao_filter(request):
    filtered = []
    filtered_json = []
    if request.method == "POST":
        # gets tipo, produto and data_field from ProducaoData serializer
        serializer = website.serializer.ProducaoSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            # if the user adds a starting date
            if serializer.validated_data["data_field"]:
                # if the user also added a produto
                if serializer.validated_data["produto"]:
                    # filters from the Producao model by date and produto
                    filtered = models.Producao.objects.filter(data__gte = serializer.validated_data["data_field"],
                                                              produto_id__nome = serializer.validated_data[
                                                                  "produto"]).order_by("-data")
                # if the user only added the tipo and date
                elif serializer.validated_data["tipo"]:
                    # filters from the Producao model by date and tip
                    filtered = models.Producao.objects.filter(data__gte = serializer.validated_data["data_field"],
                                                              produto_id__tipo = serializer.validated_data[
                                                                  "tipo"]).order_by("-data")
                # if the user only filtered by date
                else:
                    filtered = models.Producao.objects.filter(data__gte=serializer.validated_data[
                        "data_field"]).order_by("-data")
            # if the user doesn't provide the date
            elif not serializer.validated_data["data_field"]:
                # if the user provided the produto
                if serializer.validated_data["produto"]:
                    # filters from the Producao model by produto
                    filtered = models.Producao.objects.filter(produto_id__nome = serializer.validated_data[
                        "produto"]).order_by("-data")
                # if the user provided only the tipo
                elif serializer.validated_data["tipo"]:
                    # filters from the Producao model by tip
                    filtered = models.Producao.objects.filter(produto_id__tipo = serializer.validated_data[
                        "tipo"]).order_by("-data")
            if filtered:
                for i in filtered:
                    filtered_json.append({"quantidade": float(i.quantidade), "id": i.id, "produto": i.produto.nome,
                                          "data_output": i.data})
                s = website.serializer.ProducaoSerializer(filtered_json, many=True)
                return Response(s.data)
            else:
                return Response("empty")
        else:
            return Response(3)

@api_view(["POST"])
@login_required
def producao_delete(request):
    if request.method == "POST":
        # gets id from ProducaoData serializer
        serializer = website.serializer.ProducaoSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            if serializer.validated_data["id"] == 0:
                return Response(False)
            else:
                try:
                    product_id = models.Produto.objects.get(nome=serializer.validated_data["produto"])
                    product_id.estoque -= serializer.validated_data["quantidade"]
                    product_id.save()
                    models.Producao.objects.filter(id=serializer.validated_data["id"]).delete()
                    product_id = models.Produto.objects.get(nome=serializer.validated_data["produto"])
                    # filters the Quantidade model for items that have the id of the selected produto
                    quantidades = models.Quantidade.objects.filter(produto_id=product_id.id)
                    # loops through the filtererd elements
                    for quantidade in quantidades:
                        # gets that item from the db
                        quantidade_get = models.Quantidade.objects.get(id=quantidade.id)
                        # gets the item from the Ingrediente model using the relational quantidade_id
                        ingredient_to_change = models.Ingrediente.objects.get(id=quantidade_get.ingrediente_id)
                        # subtracts from the estoque of that item the quantidade_unitaria for the product times the quantidade
                        ingredient_to_change.estoque += quantidade_get.quantidade_unitaria * serializer.validated_data[
                            "quantidade"]
                        # saves the Ingrediente db
                        ingredient_to_change.save()
                    return Response(True)
                except ObjectDoesNotExist:
                    return Response(False)


@api_view(["POST"])
@login_required
def producao_estoque_update(request):
    if request.method == "POST":
        # gets id and new estoque value from EstoqueSerializer
        serializer = website.serializer.ProdutoSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            # gets the object that matches the produto selection
            product_id = models.Produto.objects.get(id=serializer.validated_data["id"])
            product_id.estoque = serializer.validated_data["estoque"]
            product_id.variacao_estoque = serializer.validated_data["estoque"] - product_id.estoque
            product_id.save()
            return Response("update")


@api_view(["POST"])
@login_required
def producao_estoque(request):
    filtered = []
    filtered_json = []
    if request.method == "POST":
        # gets tipo, produto and data_field from ProducaoData serializer
        serializer = website.serializer.ProdutoSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            # if the user provided the produto
            if serializer.validated_data["produto"]:
                # filters from the Producao model by produto
                filtered = models.Produto.objects.filter(nome=serializer.validated_data["produto"]).order_by("nome")
            # if the user provided only the tipo
            elif serializer.validated_data["tipo"]:
                # filters from the Producao model by tip
                filtered = models.Produto.objects.filter(tipo=serializer.validated_data["tipo"]).order_by("nome")
            if filtered:
                for i in filtered:
                    filtered_json.append({"estoque": float(i.estoque), "id": i.id, "produto": i.nome})
                s = website.serializer.ProdutoSerializer(filtered_json, many=True)
                return Response(s.data)
            else:
                return Response("empty")


@api_view(["POST"])
@login_required
def estoque_add_finish(request):
    if request.method == "POST":
        serializer = website.serializer.ConfirmSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            # gets id, tipo, ingrediente, quantidade, valor, data and action from EstoqueSerializer
            for item in request.session["cart"]:
                # gets the object that matches the ingrediente selection
                ingredient_id = models.Ingrediente.objects.get(nome=item["ingrediente"])
                # updates quantidada in estoque
                ingredient_id.estoque += Decimal(item["quantidade"]) * Decimal(item["por_unidade"])
                # updates quantidade in total_comprado
                ingredient_id.total_comprado += Decimal(item["quantidade"]) * Decimal(item["por_unidade"])
                # updates the date in ultima_compra
                ingredient_id.ultima_compra = date.today()
                # updates valor in valor_comprado
                ingredient_id.valor_comprado += round(Decimal(item["valor"]) * Decimal(request.session["ratio"]), 2)
                # updates the calculation of preco_medio
                try:
                    ingredient_id.preco_medio = round(ingredient_id.valor_comprado / ingredient_id.total_comprado, 2)
                except ZeroDivisionError:
                    ingredient_id.preco_medio = 0
                ingredient_id.save()
            return Response("added")


@api_view(["POST"])
@login_required
def estoque_add(request):
    if request.method == "POST":
        # gets id, tipo, ingrediente, quantidade, valor, data and action from EstoqueSerializer
        serializer = website.serializer.EstoqueSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            # gets the object that matches the ingrediente selection
            request.session["cart"].append({"ingrediente": serializer.validated_data["ingrediente"],
                                            "quantidade": float(serializer.validated_data["quantidade"]),
                                            "valor": float(serializer.validated_data["valor"]),
                                            "total": round(float(serializer.validated_data["valor"]) *
                                                           float(serializer.validated_data["quantidade"]), 2),
                                            "por_unidade": float(serializer.validated_data["por_unidade"])
                                            })
            request.session.save()
            s = website.serializer.EstoqueSerializer(request.session["cart"], many=True)
            valor = 0
            for i in request.session["cart"]:
                valor += i["total"]
            valor = "{:.2f}".format(valor).replace(".", ",")
            return Response({"cart": s.data, "valor": valor})


@api_view(["POST"])
@login_required
def estoque_add_update(request):
    if request.method == "POST":
        # gets id, tipo, ingrediente, quantidade, valor, data and action from EstoqueSerializer
        serializer = website.serializer.EstoqueSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            # gets the object that matches the ingrediente selection
            for item in request.session["cart"]:
                if item["ingrediente"] == serializer.validated_data["ingrediente"]:
                    item["quantidade"] = float(serializer.validated_data["quantidade"])
                    item["valor"] = float(serializer.validated_data["valor"])
                    item["por_unidade"] = float(serializer.validated_data["por_unidade"])
                    item["total"] = round(float(serializer.validated_data["valor"]) *
                                          float(serializer.validated_data["quantidade"]), 2)
                    break
            request.session.save()
            s = website.serializer.EstoqueSerializer(request.session["cart"], many=True)
            valor = 0
            for i in request.session["cart"]:
                valor += i["total"]
            valor = "{:.2f}".format(valor).replace(".", ",")
            return Response({"cart": s.data, "valor": valor})


@api_view(["POST"])
@login_required
def estoque_add_delete(request):
    if request.method == "POST":
        # gets id, tipo, ingrediente, quantidade, valor, data and action from EstoqueSerializer
        serializer = website.serializer.EstoqueSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            # gets the object that matches the ingrediente selection
            for item in request.session["cart"]:
                if item["ingrediente"] == serializer.validated_data["ingrediente"]:
                    request.session["cart"].remove(item)
                    break
            request.session.save()
            s = website.serializer.EstoqueSerializer(request.session["cart"], many=True)
            valor = 0
            for i in request.session["cart"]:
                valor += i["total"]
            valor = "{:.2f}".format(valor).replace(".", ",")
            return Response({"cart": s.data, "valor": valor})


# to be completed
@api_view(["POST"])
@login_required
def estoque_filter(request):
    # handling forms
    filtered = []
    filtered_json = []
    if request.method == "POST":
        serializer = website.serializer.EstoqueSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            # if the user filters by date
            if serializer.validated_data["data_field"] > date(1900, 1, 1):
                # if the user also filters by ingrediente
                if serializer.validated_data["ingrediente"]:
                    # filters from the Ingrediente model by date and ingrediente
                    filtered = models.Ingrediente.objects.filter(
                        ultima_compra__gte=serializer.validated_data["data_field"],
                        nome=serializer.validated_data["ingrediente"]).order_by("-ultima_compra")
                # if the user also filters by tipo
                elif serializer.validated_data["tipo"]:
                    # filters from the Ingrediente model by date and tipo
                    filtered = models.Ingrediente.objects.filter(
                        ultima_compra__gte=serializer.validated_data["data_field"],
                        tipo=serializer.validated_data["tipo"]).order_by("-ultima_compra")
                # if the user only filtered by date
                else:
                    filtered = models.Ingrediente.objects.filter(
                        ultima_compra__gte=serializer.validated_data["data_field"]).order_by("-ultima_compra")
            # if the user doesn't provide the date
            else:
                # if the user filtered by ingrediente
                if serializer.validated_data["ingrediente"]:
                    # filters from the Ingrediente model by ingrediente
                    filtered = models.Ingrediente.objects.filter(
                        nome=serializer.validated_data["ingrediente"]).order_by("nome")
                # if the user filtered by tipo
                elif serializer.validated_data["tipo"]:
                    # filters from the Ingrediente model by tipo
                    filtered = models.Ingrediente.objects.filter(
                        tipo=serializer.validated_data["tipo"]).order_by("nome")
            if filtered:
                for i in filtered:
                    filtered_json.append({"estoque": i.estoque, "id": i.id, "ingrediente": i.nome,
                                          "data_output": i.ultima_compra, "unidade": i.unidade})
                s = website.serializer.EstoqueSerializer(filtered_json, many=True)
                return Response(s.data)
            else:
                return Response("empty")


@api_view(["POST"])
@login_required
def estoque_update(request):
    if request.method == "POST":
        # gets id and new estoque value from EstoqueSerializer
        serializer = website.serializer.EstoqueSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            # gets the object that matches the ingrediente selection
            ingredient_id = models.Ingrediente.objects.get(id=serializer.validated_data["id"])
            # calculates and updates the net estoque
            ingredient_id.variacao_estoque = serializer.validated_data["estoque"] - ingredient_id.estoque
            # updates quantidade in estoque
            ingredient_id.estoque = serializer.validated_data["estoque"]
            ingredient_id.save()
            return Response("update")


@api_view(["POST"])
@login_required
def cliente_update(request):
    if request.method == "POST":
        serializer = website.serializer.ClienteSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            cliente = models.Cliente.objects.get(id=serializer.validated_data["id"])
            cliente.nome = serializer.validated_data["nome"].lower()
            cliente.telefone = serializer.validated_data["telefone"]
            cliente.endereco = serializer.validated_data["endereco"].lower()
            cliente.bairro = serializer.validated_data["bairro"]
            cliente.cidade = serializer.validated_data["cidade"].lower()
            cliente.save()
            return Response(True)


@api_view(["POST"])
@login_required
def fornecedor_update(request):
    if request.method == "POST":
        serializer = website.serializer.FornecedorSearchSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            fornecedor = models.Fornecedor.objects.get(id=serializer.validated_data["id"])
            fornecedor.nome = serializer.validated_data["nome"].lower()
            fornecedor.telefone = serializer.validated_data["telefone"]
            fornecedor.endereco = serializer.validated_data["endereco"].lower()
            fornecedor.estado = serializer.validated_data["estado"].lower()
            fornecedor.cidade = serializer.validated_data["cidade"].lower()
            fornecedor.contato = serializer.validated_data["contato"].lower()
            fornecedor.save()
            return Response(True)


@api_view(["POST"])
@login_required
def novo_pedido_add(request):
    if request.method == "POST":
        # gets tipo, produto and quantidade from ProducaoData form
        serializer = website.serializer.PedidoSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            produto = models.Produto.objects.get(nome=serializer.validated_data["produto"])
            request.session["cart_serializer"].append(
                {"produto": serializer.validated_data["produto"],
                 "quantidade": "{:.1f}".format(serializer.validated_data["quantidade"]).replace(".", ","),
                 "valor": "{:.2f}".format(produto.valor).replace(".", ","),
                 "total": "{:.2f}".format(produto.valor * serializer.validated_data["quantidade"]).replace(".", ",")})
            request.session["cart"].append({
                "produto": serializer.validated_data["produto"],
                "quantidade": float(serializer.validated_data["quantidade"]),
                "valor": float(produto.valor),
                "total": float(produto.valor * serializer.validated_data["quantidade"])
                                            })
            request.session["cart_total"] += float(produto.valor * serializer.validated_data["quantidade"])
            serialized_session = website.serializer.ListPedidoSerializer({
                "cart": request.session["cart_serializer"], "total": request.session["cart_total"]})
            request.session.save()
            return Response(serialized_session.data)
        else:
            # request was invalid. displays message to the user
            return Response("fail")


@api_view(["POST"])
@login_required
def novo_pedido_delete(request):
    if request.method == "POST":
        serializer = website.serializer.PedidoSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serialized_session = website.serializer.ListPedidoSerializer({"cart": request.session["cart"]})
            for i in range(len(request.session["cart"])):
                if request.session["cart"][i]["produto"] == serializer.validated_data["produto"]:
                    produto = models.Produto.objects.get(nome=serializer.validated_data["produto"])
                    request.session["cart"].remove(request.session["cart"][i])
                    request.session["cart_serializer"].remove(request.session["cart_serializer"][i])
                    request.session["cart_total"] -= float(produto.valor * serializer.validated_data["quantidade"])
                    request.session.save()
                    serialized_session = website.serializer.ListPedidoSerializer({
                        "cart": request.session["cart_serializer"], "total": request.session["cart_total"]})
                    return Response(serialized_session.data)
            return Response(serialized_session.data)


@api_view(["POST"])
@login_required
def novo_pedido_update(request):
    if request.method == "POST":
        serializer = website.serializer.PedidoSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serialized_session = website.serializer.ListPedidoSerializer({"cart": request.session["cart"]})
            for i in range(len(request.session["cart"])):
                if request.session["cart"][i]["produto"] == serializer.validated_data["produto"]:
                    produto = models.Produto.objects.get(nome=serializer.validated_data["produto"])
                    request.session["cart_total"] -= float(produto.valor) * request.session["cart"][i]["quantidade"]
                    request.session["cart"][i]["quantidade"] = float(serializer.validated_data["quantidade"])
                    request.session["cart_serializer"][i]["quantidade"] = "{:.1f}".format(
                        serializer.validated_data["quantidade"]).replace(".", ",")
                    request.session["cart"][i]["total"] = float(produto.valor * serializer.validated_data["quantidade"])
                    request.session["cart_serializer"][i]["total"] = "{:.2f}".format(
                        produto.valor * serializer.validated_data["quantidade"]).replace(".", ",")
                    request.session["cart_total"] += float(produto.valor * serializer.validated_data["quantidade"])
                    request.session.save()
                    serialized_session = website.serializer.ListPedidoSerializer({
                        "cart": request.session["cart_serializer"], "total": request.session["cart_total"]})
                    return Response(serialized_session.data)
            return Response(serialized_session.data)


@api_view(["POST"])
@login_required
def cart_user(request):
    if request.method == "POST":
        serializer = website.serializer.IdSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = models.Cliente.objects.get(id=serializer.validated_data["user_id"])
            user_json = {"id": user.id, "nome": user.nome.title()}
            request.session["cart_user"] = user_json
            request.session.save()
            return Response(True)


@api_view(["POST"])
@login_required
def nova_compra_add(request):
    if request.method == "POST":
        serializer=website.serializer.CompraSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            fornecedor = models.Fornecedor.objects.get(id=serializer.validated_data["id"])
            models.Compra.objects.create(fornecedor=fornecedor,
                                         nota=serializer.validated_data["nota"],
                                         desconto=serializer.validated_data["desconto"],
                                         imposto=serializer.validated_data["imposto"],
                                         total=serializer.validated_data["nota"] -
                                               serializer.validated_data["desconto"] +
                                               serializer.validated_data["imposto"],
                                         usuario=request.user,
                                         )
            ratio = (serializer.validated_data["nota"] +
                     serializer.validated_data["imposto"] -
                     serializer.validated_data["desconto"]) / serializer.validated_data["nota"]
            request.session["ratio"] = float(ratio)
            request.session["nota"] = "{:.2f}".format(serializer.validated_data["nota"]).replace(".", ",")
            request.session.save()
            return Response(ratio)


@api_view(["POST"])
@login_required
def finalizar_pedido_init(request):
    if request.method == "POST":
        serialized_session = website.serializer.ListPedidoSerializer({
            "cart": request.session["cart_serializer"], "total": request.session["cart_total"]})
        s = website.serializer.PedidosFilterSerializer({"data_output": date.today()})
        return Response({"bulk": serialized_session.data, "date": s.data})


@api_view(["POST"])
@login_required
def estoque_add_init(request):
    if request.method == "POST":
        s = website.serializer.EstoqueSerializer(request.session["cart"], many=True)
        valor = 0
        for i in request.session["cart"]:
            valor += i["total"]
        valor = "{:.2f}".format(valor).replace(".", ",")
        return Response({"cart": s.data, "valor": valor})


@api_view(["POST"])
@login_required
def pedidos_filter(request):
    filtered_temp = []
    filtered_json = []
    if request.method == "POST":
        serializer = website.serializer.PedidosFilterSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            filtered = models.Pedido.objects.filter(data__gte=serializer.validated_data["data_field"]).order_by("-data")
            if filtered:
                for i in filtered:
                    filtered_temp.append(i)
                    if serializer.validated_data["nome"]:
                        if serializer.validated_data["nome"].lower() not in models.Cliente.objects.get(id=i.cliente_id).nome:
                            filtered_temp.remove(i)
                            continue
                    if serializer.validated_data["telefone"]:
                        if serializer.validated_data["telefone"] != models.Cliente.objects.get(id=i.cliente_id).telefone:
                            filtered_temp.remove(i)
                            continue
                    if serializer.validated_data["status"] == "True":
                        if not i.entregue:
                            filtered_temp.remove(i)
                            continue
                    elif serializer.validated_data["status"] == "False":
                        if i.entregue:
                            filtered_temp.remove(i)
                            continue
                    if serializer.validated_data["pagamento"] == "True":
                        if not i.pago:
                            filtered_temp.remove(i)
                            continue
                    elif serializer.validated_data["pagamento"] == "False":
                        if i.pago:
                            filtered_temp.remove(i)
                            continue
            for i in filtered_temp:
                if i.entregue:
                    status = "Entregue"
                else:
                    status = "Não Entregue"
                if i.pago:
                    pagamento = "Pago"
                else:
                    pagamento = "Não Pago"
                nome = models.Cliente.objects.get(id=i.cliente_id).nome
                filtered_json.append({"id": i.id, "nome": nome.title(), "data_output": i.data, "status": status,
                                      "pagamento": pagamento})
            s = website.serializer.PedidosFilterSerializer(filtered_json, many=True)
            return Response(s.data)


@api_view(["POST"])
@login_required
def pedidos_filter_delete(request):
    if request.method == "POST":
        serializer = website.serializer.PedidosFilterSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            pedido = models.Pedido.objects.get(id=serializer.validated_data["id"])
            cliente = models.Cliente.objects.get(id=pedido.cliente.id)
            cliente.credito += pedido.total
            cliente.save()
            pedido.delete()
            models.PedidoDetalhe.objects.filter(pedido=serializer.validated_data["id"]).delete()
            return Response("delete")


@api_view(["POST"])
@login_required
def pedidos_filter_done(request):
    if request.method == "POST":
        serializer = website.serializer.PedidosFilterSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            pedido = models.Pedido.objects.get(id=serializer.validated_data["id"])
            pedido.debito = 0
            pedido.entregue = True
            pedido.pago = True
            cliente = models.Cliente.objects.get(id=pedido.cliente.id)
            cliente.credito += pedido.total
            cliente.save()
            pedido.save()
            return Response("success")

@api_view(["POST"])
@login_required
def pedidos_detalhe_list(request):
    if request.method == "POST":
        pedidos_detalhe = []
        serializer = website.serializer.PedidosFilterSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            filtered = models.PedidoDetalhe.objects.filter(pedido=serializer.validated_data["id"])
            if filtered:
                for item in filtered:
                    pedidos_detalhe.append(
                        {"id": item.id, "produto": item.produto.nome, "quantidade": item.quantidade,
                         "valor": item.valor_unitario, "total": item.total})
            s = website.serializer.PedidoSerializer(pedidos_detalhe, many=True)
            pedido = models.Pedido.objects.get(id=serializer.validated_data["id"])
            if pedido.entregue:
                status = "Entregue"
            else:
                status = "Não Entregue"
            info = {"debito": pedido.debito, "status": status, "boolean": pedido.entregue, "id": pedido.id}
            d = website.serializer.PedidosFilterSerializer(info)
            return Response({"list": s.data, "info": d.data})


@api_view(["POST"])
@login_required
def pedidos_detalhe_pedido(request):
    if request.method == "POST":
        pedidos_detalhe = []
        serializer = website.serializer.PedidosFilterSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            filtered = models.PedidoDetalhe.objects.filter(pedido=serializer.validated_data["id"])
            if filtered:
                for item in filtered:
                    pedidos_detalhe.append(
                        {"id": item.id, "produto": item.produto.nome, "quantidade": item.quantidade,
                         "valor": item.valor_unitario, "total": item.total})
            s = website.serializer.PedidoSerializer(pedidos_detalhe, many=True)
            pedido = models.Pedido.objects.get(id=serializer.validated_data["id"])
            pedido.entregue = serializer.validated_data["boolean"]
            if pedido.entregue:
                status = "Entregue"
            else:
                status = "Não Entregue"
            if pedido.debito - serializer.validated_data["debito"] <= 0:
                pedido.debito = 0
                pedido.pago = True
            else:
                pedido.debito -= serializer.validated_data["debito"]
            pedido.cliente.credito += serializer.validated_data["debito"]
            pedido.cliente.save()
            pedido.save()
            info = {"id": pedido.id, "debito": pedido.debito, "status": status, "boolean": pedido.entregue}
            d = website.serializer.PedidosFilterSerializer(info)
            return Response({"list": s.data, "info": d.data})


@api_view(["POST"])
@login_required
def pedidos_detalhe_delete(request):
    if request.method == "POST":
        pedidos_detalhe = []
        serializer = website.serializer.PedidosFilterSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            item = models.PedidoDetalhe.objects.get(id=serializer.validated_data["id"])
            if item.pedido.debito < item.total:
                item.pedido.debito = 0
                item.pedido.pago = True
            else:
                item.pedido.debito -= item.total
            item.pedido.total -= item.total
            item.pedido.cliente.credito += item.total
            item.produto.estoque += item.quantidade
            id = item.pedido.id
            item.delete()
            item.pedido.save()
            item.pedido.cliente.save()
            item.produto.save()
            filtered = models.PedidoDetalhe.objects.filter(pedido=id)
            if filtered:
                for item in filtered:
                    pedidos_detalhe.append(
                        {"id": item.id, "produto": item.produto.nome, "quantidade": item.quantidade,
                         "valor": item.valor_unitario,
                         "total": item.total})
            s = website.serializer.PedidoSerializer(pedidos_detalhe, many=True)
            if not s.data and item.pedido.delivery_valor > 0:
                item.pedido.cliente.credito += item.pedido.delivery_valor
                item.pedido.delivery_valor = 0
                item.pedido.debito = 0
                item.pedido.pago = True
                item.pedido.cliente.save()
                item.pedido.save()
            pedido = models.Pedido.objects.get(id=id)
            info = {"id": pedido.id, "debito": pedido.debito, "status": status, "boolean": pedido.entregue,
                    "valor": pedido.total}
            d = website.serializer.PedidosFilterSerializer(info)
            return Response({"list": s.data, "info": d.data})


@api_view(["POST"])
@login_required
def pedidos_detalhe_update(request):
    if request.method == "POST":
        pedidos_detalhe = []
        serializer = website.serializer.PedidosFilterSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            item = models.PedidoDetalhe.objects.get(id=serializer.validated_data["id"])
            id = item.pedido.id
            message = "failure"
            if serializer.validated_data["quantidade"] > 0:
                net = item.valor_unitario * (serializer.validated_data["quantidade"] - item.quantidade)
                if item.pedido.debito < -net:
                    item.pedido.debito = 0
                    item.pedido.pago = True
                else:
                    item.pedido.debito += net
                    if item.pedido.debito == 0:
                        item.pedido.pago = True
                item.quantidade = serializer.validated_data["quantidade"]
                item.pedido.total += net
                item.pedido.cliente.credito -= net
                item.produto.estoque += serializer.validated_data["quantidade"] - item.quantidade
                item.pedido.save()
                item.pedido.cliente.save()
                item.produto.save()
                item.save()
                message = "update"
            filtered = models.PedidoDetalhe.objects.filter(pedido=id)
            if filtered:
                for item in filtered:
                    pedidos_detalhe.append(
                        {"id": item.id, "produto": item.produto.nome, "quantidade": item.quantidade,
                         "valor": item.valor_unitario,
                         "total": item.total})
            s = website.serializer.PedidoSerializer(pedidos_detalhe, many=True)
            pedido = models.Pedido.objects.get(id=id)
            info = {"id": pedido.id, "debito": pedido.debito, "status": status, "boolean": pedido.entregue,
                    "valor": pedido.total}
            d = website.serializer.PedidosFilterSerializer(info)
            return Response({"list": s.data, "info": d.data, "message": message})

