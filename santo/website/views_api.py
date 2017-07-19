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
                                                      bairro=serializer.validated_data["bairro"],
                                                      cidade=serializer.validated_data["cidade"].lower(),
                                                      referencia=serializer.validated_data["referencia"].lower())
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
                                              bairro=serializer.validated_data["bairro"],
                                              cidade=serializer.validated_data["cidade"].lower(),
                                              referencia=serializer.validated_data["referencia"].lower())
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


@login_required
def pedidos(request):
    success = 1
    filtered = []
    if request.method == "GET":
        pass
    context = {}
    # request.session['cart'] = []
    # del request.session['cart']
    return TemplateResponse(request, "pedidos.html", context)


# need to create API to update subtotal based on delivery
@api_view(["GET"])
@login_required
def finalizar_pedido_delivery(request):
    try:
        referer = request.META['HTTP_REFERER']
    except KeyError:
        referer = ""
    check = re.search(r"finalizar_pedido", referer)
    if request.method == "POST" and check:
        pass
    elif request.method == "POST":
        pass
    context = {}
    context["cliente"] = request.session["cart_user"]
    context["cart"] = request.session["cart"]
    return TemplateResponse(request, "finalizar_pedido.html", context)


@api_view(["POST"])
@login_required
def escolher_cliente_filter(request):
    filtered = []
    filtered_json = []
    # if the current view was the referer
    if request.method == "POST":
        # gets cliente from ClienteSearch form
        serializer = website.serializer.ClienteSearchSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            # if the user inputs nome and telefone, filters for a match for both
            if serializer.validated_data["nome"] and serializer.validated_data["telefone"]:
                filtered = models.Cliente.objects.filter(nome__icontains=serializer.validated_data["nome"], telefone=serializer.validated_data["telefone"]).order_by("nome")
            # if the user inputs nome, filters for a match that contains nome
            elif serializer.validated_data["nome"]:
                filtered = models.Cliente.objects.filter(nome__icontains=serializer.validated_data["nome"]).order_by("nome")
            # if the user inputs telefone, filters for a match for the telefone
            elif serializer.validated_data["telefone"]:
                filtered = models.Cliente.objects.filter(telefone=serializer.validated_data["telefone"]).order_by("nome")
            if filtered:
                for i in filtered:
                    filtered_json.append({"id": i.id, "nome": i.nome.title(), "telefone": i.telefone, "endereco": i.endereco.title(), "bairro": i.bairro, "cidade": i.cidade.title()})
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
                                                            contato__icontains=serializer.validated_data["contato"]).order_by("nome")
            # if the user inputs nome, filters for a match that contains nome
            elif serializer.validated_data["nome"]:
                filtered = models.Fornecedor.objects.filter(nome__icontains=serializer.validated_data["nome"]).order_by("nome")
            # if the user inputs telefone, filters for a match for the telefone
            elif serializer.validated_data["contato"]:
                filtered = models.Fornecedor.objects.filter(contato__icontains=serializer.validated_data["contato"]).order_by("nome")
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
                ingredient_to_change.estoque -= quantidade_get.quantidade_unitaria * serializer.validated_data["quantidade"]
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
                models.Producao.objects.create(produto=product_id, quantidade=serializer.validated_data["quantidade"], usuario=request.user)
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
                    filtered = models.Producao.objects.filter(data__gte = serializer.validated_data["data_field"], produto_id__nome = serializer.validated_data["produto"]).order_by("-data")
                # if the user only added the tipo and date
                elif serializer.validated_data["tipo"]:
                    # filters from the Producao model by date and tip
                    filtered = models.Producao.objects.filter(data__gte = serializer.validated_data["data_field"], produto_id__tipo = serializer.validated_data["tipo"]).order_by("-data")
                # if the user only filtered by date
                else:
                    filtered = models.Producao.objects.filter(data__gte=serializer.validated_data["data_field"]).order_by("-data")
            # if the user doesn't provide the date
            elif not serializer.validated_data["data_field"]:
                # if the user provided the produto
                if serializer.validated_data["produto"]:
                    # filters from the Producao model by produto
                    filtered = models.Producao.objects.filter(produto_id__nome = serializer.validated_data["produto"]).order_by("-data")
                # if the user provided only the tipo
                elif serializer.validated_data["tipo"]:
                    # filters from the Producao model by tip
                    filtered = models.Producao.objects.filter(produto_id__tipo = serializer.validated_data["tipo"]).order_by("-data")
            if filtered:
                for i in filtered:
                    filtered_json.append({"quantidade": float(i.quantidade), "id": i.id, "produto": i.produto.nome, "data_output": i.data})
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
                        ingredient_to_change.estoque += quantidade_get.quantidade_unitaria * serializer.validated_data["quantidade"]
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
def estoque_add(request):
    if request.method == "POST":
        # gets id, tipo, ingrediente, quantidade, valor, data and action from EstoqueSerializer
        serializer = website.serializer.EstoqueSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            # gets the object that matches the ingrediente selection
            ingredient_id = models.Ingrediente.objects.get(nome=serializer.validated_data["ingrediente"])
            # updates quantidada in estoque
            ingredient_id.estoque += serializer.validated_data["quantidade"]
            # updates quantidade in total_comprado
            ingredient_id.total_comprado += serializer.validated_data["quantidade"]
            # updates the date in ultima_compra
            ingredient_id.ultima_compra = date.today()
            # updates valor in valor_comprado
            ingredient_id.valor_comprado += serializer.validated_data["valor"]
            # updates the calculation of preco_medio
            try:
                ingredient_id.preco_medio = ingredient_id.valor_comprado / ingredient_id.total_comprado
            except ZeroDivisionError:
                ingredient_id.preco_medio = 0

            ingredient_id.save()
            return Response("added")


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
            print(serializer.validated_data["data_field"])
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
                    filtered = models.Ingrediente.objects.filter(ultima_compra__gte=serializer.validated_data["data_field"], tipo = serializer.validated_data["tipo"]).order_by("-ultima_compra")
                # if the user only filtered by date
                else:
                    filtered = models.Ingrediente.objects.filter(ultima_compra__gte=serializer.validated_data["data_field"]).order_by("-ultima_compra")
            # if the user doesn't provide the date
            else:
                print("test")
                # if the user filtered by ingrediente
                if serializer.validated_data["ingrediente"]:
                    # filters from the Ingrediente model by ingrediente
                    filtered = models.Ingrediente.objects.filter(nome = serializer.validated_data["ingrediente"]).order_by("nome")
                # if the user filtered by tipo
                elif serializer.validated_data["tipo"]:
                    # filters from the Ingrediente model by tipo
                    filtered = models.Ingrediente.objects.filter(tipo = serializer.validated_data["tipo"]).order_by("nome")
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
            request.session["cart_serializer"].append({"produto": serializer.validated_data["produto"],
                                        "quantidade": str(serializer.validated_data["quantidade"]).replace(".", ",")})
            request.session["cart"].append({"produto": serializer.validated_data["produto"],
                                            "quantidade": float(serializer.validated_data["quantidade"])})
            serialized_session = website.serializer.ListPedidoSerializer({"cart": request.session["cart_serializer"]})
            print(request.session["cart"])
            print(request.session["cart_serializer"])
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
                    request.session["cart"].remove(request.session["cart"][i])
                    request.session["cart_serializer"].remove(request.session["cart_serializer"][i])
                    request.session.save()
                    serialized_session = website.serializer.ListPedidoSerializer({"cart": request.session["cart_serializer"]})
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
                    request.session["cart"][i]["quantidade"] = float(serializer.validated_data["quantidade"])
                    request.session["cart_serializer"][i]["quantidade"] = str(serializer.validated_data["quantidade"]).replace(".", ",")
                    request.session.save()
                    serialized_session = website.serializer.ListPedidoSerializer({"cart": request.session["cart_serializer"]})
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
            return Response(ratio)
