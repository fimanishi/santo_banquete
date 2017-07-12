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


# login page, only accessible when the user is not logged in
def index(request):
    # gets the username and password from UserForm
    form = website.forms.UserForm(request.POST or None)
    if request.method == "POST":
        # checks if username and password are valid inputs
        if form.is_valid():
            # authenticates the username and password based on the records
            user = authenticate(request, username=form.cleaned_data["user_name"], password=form.cleaned_data["user_password"])
            # checks if the user passed authentication
            if user is not None:
                # logs in the user and redirects to the authenticated page
                login(request, user)
                return http.HttpResponseRedirect("/authenticated/")
    context = {}
    return TemplateResponse(request, "index.html", context)


# menu page that routes the user to a specific application
@login_required
def authenticated(request):
    context = {}
    return TemplateResponse(request, "authenticated.html", context)


# page to add a new client. does the verification of the fields and adds to the database
# required inputs: nome completo and cidade
@login_required
def adicionar_cliente(request):
    # initializes an empty cart list in the session as the view will redirect to a new order
    request.session["cart"] = []
    # initializes an empty cart_user dictionary in the session as the view will redirect to a new order
    request.session["cart_user"] = {}
    # success = 1 means that the user just entered the view and should render the initial page for that view
    success = 1
    # client_id will be passed to the new order page. If not assigned, it's an empty string
    client_id = ""
    if request.method == "POST":
        # gets nome, telefone, tipo, endereco, bairro, cidade e referencia from the ClientData form
        form = website.forms.ClienteData(request.POST or None)
        if form.is_valid():
            # checks against the Cliente database to see if a client with nome already exists
            exist_check = models.Cliente.objects.filter(nome=form.cleaned_data["nome"].lower())
            # if client exists
            if exist_check:
                # loops through all clients that have nome as nome
                for each in exist_check:
                    # if a client with nome and the telefone from the form already exists, display message
                    if each.telefone == form.cleaned_data["telefone"]:
                        # success = 4 means that the client already exists in the db and a message should be displayed
                        success = 4
                    else:
                        # if the client is in the db but has a different phone number, adds a new instance to the db
                        models.Cliente.objects.create(nome=form.cleaned_data["nome"].lower(),
                                                      telefone=form.cleaned_data["telefone"],
                                                      tipo=form.cleaned_data["tipo"],
                                                      endereco=form.cleaned_data["endereco"].lower(),
                                                      bairro=form.cleaned_data["bairro"],
                                                      cidade=form.cleaned_data["cidade"].lower(),
                                                      referencia=form.cleaned_data["referencia"].lower())
                        # success = 2 means that the new client was added successfully
                        success = 2
                        # gets the id from the new client. this id will be passed to next view
                        client_id = models.Cliente.objects.last()
            else:
                # if the client is not in the db, adds the client to the db
                models.Cliente.objects.create(nome=form.cleaned_data["nome"].lower(),
                                              telefone=form.cleaned_data["telefone"],
                                              tipo=form.cleaned_data["tipo"],
                                              endereco=form.cleaned_data["endereco"].lower(),
                                              bairro=form.cleaned_data["bairro"],
                                              cidade=form.cleaned_data["cidade"].lower(),
                                              referencia=form.cleaned_data["referencia"].lower())
                # success = 2 means that the new client was added successfully
                success = 2
                # gets the id from the new client. this id will be passed to next view
                client_id = models.Cliente.objects.last()
        else:
            # success = 3 means that the form is not valid. displays a message indicating it to the user
            success = 3
    # adds context with success and client_id to the django template
    context = {"success": success,
               }
    if client_id:
        context["id"] = client_id.id

    return TemplateResponse(request, "adicionar_cliente.html", context)


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


@login_required
def novo_pedido(request):
    # success = 1 means that the user just entered the view and should render the initial page for that view
    success = 1
    if request.method == "GET":
        # gets cliente from ClienteSelection form
        form = website.forms.ClienteSelection(request.GET or None)
        if form.is_valid():
            # assigns the cliente's values to cart_user in a dictionary
            request.session["cart_user"] = models.Cliente.objects.filter(id=form.cleaned_data["cliente"]).values()[0]
        else:
            # if the form is invalid(the cliente data was not passed), redirects to escolher_cliente view
            http.HttpResponseRedirect("/escolher_cliente/")
    elif request.method == "POST":
        # gets tipo, produto and quantidade from Pedido form
        form = website.forms.Pedido(request.POST or None)
        if form.is_valid():
            # appends to the cart list a dictionary with the produto_id, nome and quantidade
            request.session["cart"].append({"product_id": models.Produto.objects.get(nome=form.cleaned_data["produto"]).id, "produto": form.cleaned_data["produto"], "quantity": float(form.cleaned_data["quantidade"])})
        else:
            # success = 3 means that the Pedido form is invalid and displays a message to the user indicating it
            success = 3
    # checks to see if the cart has items on it and that the input form is not invalid
    if request.session["cart"] and success != 3:
        # success = 2 means that the cart has items and displays it
        success = 2
    # gets all the distinct types of food categories
    types = models.Produto.objects.filter(~Q(tipo="bebida")).distinct("tipo").order_by("tipo")
    # gets all products
    products = models.Produto.objects.all()
    # creates a dictionary to store all categories and products
    context = {'products': {}}
    # dynamically creates the dictionary containing categories and products
    for i in products:
        for j in types:
            context['products'][j.tipo] = models.Produto.objects.filter(tipo=j.tipo)
    # adds the categories to the django template
    context["types"] = types
    # adds the cliente values to the django template
    context["cliente"] = request.session["cart_user"]
    # adds the cart to the django template
    context["cart"] = request.session["cart"]
    # adds the success status to the django template
    context["success"] = success
    # saves the changes in the session
    request.session.save()
    # if the user refreshes the page, redirects it to the same view
    if request.method == "POST":
        return http.HttpResponseRedirect("/novo_pedido/")
    else:
        return TemplateResponse(request, "novo_pedido.html", context)


@login_required
def escolher_cliente(request):
    # initializes an empty cart list in the session as the view will redirect to a new order
    request.session["cart"] = []
    # initializes an empty cart_user dictionary in the session as the view will redirect to a new order
    request.session["cart_user"] = {}
    # initializes an empty list that will receive filtered items from db
    filtered = []
    # success = 1 means that the user just entered the view and should render the initial page for that view
    success = 1
    # tries to assign to the variable referer the path that refered this view
    try:
        referer = request.META['HTTP_REFERER']
    # if there's no referer, assigns an empty string
    except KeyError:
        referer = ""
    # checks if the current view was the referer
    check = re.search(r"escolher_cliente", referer)
    # if the current view was the referer
    if request.method == "GET" and check:
        # gets cliente from ClienteSearch form
        form = website.forms.ClienteSearch(request.GET or None)
        if form.is_valid():
            # success = 2 means that the validation passed and matches to the filter were found
            success = 2
            # if the user inputs nome and telefone, filters for a match for both
            if form.cleaned_data["nome"] and form.cleaned_data["telefone"]:
                filtered = models.Cliente.objects.filter(nome__icontains=form.cleaned_data["nome"], telefone=form.cleaned_data["telefone"])
            # if the user inputs nome, filters for a match that contains nome
            elif form.cleaned_data["nome"]:
                filtered = models.Cliente.objects.filter(nome__icontains=form.cleaned_data["nome"])
            # if the user inputs telefone, filters for a match for the telefone
            elif form.cleaned_data["telefone"]:
                filtered = models.Cliente.objects.filter(telefone=form.cleaned_data["telefone"])
            # if no matches were found
            if not filtered:
                # success = 3 means that no matches were found and display a message indicating it
                success = 3
        else:
            # success = 4 means that the form ClienteSearch is not valid. displays a message indicating it to the user
            success = 4  
    # adds the filtered list and success status to the django template
    context = {"filtered": filtered, "success": success}
    return TemplateResponse(request, "escolher_cliente.html", context)


@api_view(["POST"])
@login_required
def producao_add(request):
    if request.method == "POST":
        # gets tipo, produto and quantidade from ProducaoData form
        serializer = website.serializer.ProducaoSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            # gets the id of the produto selected on the form
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
                print(serializer.validated_data["data_field"])
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
        else:
            return Response(3)


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
            if serializer.validated_data["data_field"]:
                # if the user also filters by ingrediente
                if serializer.validated_data["ingrediente"]:
                    # filters from the Ingrediente model by date and ingrediente
                    filtered = models.Ingrediente.objects.filter(ultima_compra__gte = serializer.validated_data["data_field"], nome = serializer.validated_data["ingrediente"]).order_by("-ultima_compra")
                # if the user also filters by tipo
                elif serializer.validated_data["tipo"]:
                    # filters from the Ingrediente model by date and tipo
                    filtered = models.Ingrediente.objects.filter(ultima_compra__gte = serializer.validated_data["data_field"], tipo = serializer.validated_data["tipo"]).order_by("-ultima_compra")
                # if the user only filtered by date
                else:
                    filtered = models.Ingrediente.objects.filter(ultima_compra__gte=serializer.validated_data["data_field"]).order_by("-ultima_compra")
            # if the user doesn't provide the date
            elif not serializer.validated_data["data_field"]:
                # if the user filtered by ingrediente
                if serializer.validated_data["ingrediente"]:
                    # filters from the Ingrediente model by ingrediente
                    filtered = models.Ingrediente.objects.filter(nome = serializer.validated_data["ingrediente"])
                # if the user filtered by tipo
                elif serializer.validated_data["tipo"]:
                    # filters from the Ingrediente model by tipo
                    filtered = models.Ingrediente.objects.filter(tipo = serializer.validated_data["tipo"])
            if filtered:
                for i in filtered:
                    filtered_json.append({"estoque": float(i.estoque), "id": i.id, "ingrediente": i.nome,
                                          "data_output": i.ultima_compra, "unidade": i.unidade})
                s = website.serializer.ProducaoSerializer(filtered_json, many=True)
                return Response(s.data)
            else:
                return Response("empty")


