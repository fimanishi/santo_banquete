from django.template.response import TemplateResponse
import website.forms
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


@login_required
def finalizar_pedido(request):
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


@login_required
def producao(request):
    # success = 1 means that the user just entered the view and should render the initial page for that view
    success = 1
    # initializes an empty list that will receive filtered items from db
    filtered = []
    if request.method == "POST":
        # gets tipo, produto and quantidade from ProducaoData form
        form = website.forms.ProducaoData(request.POST or None, request=request)
        if form.is_valid():
            print("test")
            # gets the id of the produto selected on the form
            product_id = models.Produto.objects.get(nome=form.cleaned_data["produto"])
            # filters the Quantidade model for items that have the id of the selected produto
            quantidades = models.Quantidade.objects.filter(produto_id=product_id.id)
            # loops through the filtererd elements
            for quantidade in quantidades:
                # gets that item from the db
                quantidade_get = models.Quantidade.objects.get(id=quantidade.id)
                # gets the item from the Ingrediente model using the relational quantidade_id
                ingredient_to_change = models.Ingrediente.objects.get(id=quantidade_get.ingrediente_id)
                # subtracts from the estoque of that item the quantidade_unitaria for the product times the quantidade
                ingredient_to_change.estoque -= quantidade_get.quantidade_unitaria * form.cleaned_data["quantidade"]
                # saves the Ingrediente db
                ingredient_to_change.save()
            # checks to see if the produto was already added to the producao today
            try:
                # gets the item
                check = models.Producao.objects.get(produto_id=product_id.id, data=date.today())
                # adds to the previous quantidade the quantidade input by the user
                check.quantidade += form.cleaned_data["quantidade"]
                # saves the Producao db
                check.save()
            # if this produto was not added to the producao today
            except ObjectDoesNotExist:
                # adds the produto produced to the Producao model
                models.Producao.objects.create(produto=product_id, quantidade=form.cleaned_data["quantidade"], usuario = request.user )
            # success = 2 means that the produto was either update or added successfully
            success = 2
        else:
            # success = 3 means that the form was invalid. displays message to the user
            success = 3
    elif request.method == "GET":
        # gets tipo, produto and data_field from ProducaoData form
        form = website.forms.ProducaoData(request.GET or None)
        if form.is_valid():
            # if the user adds a starting date
            if form.cleaned_data["data_field"]:
                # if the user also added a produto
                if form.cleaned_data["produto"]:
                    # filters from the Producao model by date and produto
                    filtered = models.Producao.objects.filter(data__gte = form.cleaned_data["data_field"], produto_id__nome = form.cleaned_data["produto"])
                # if the user only added the tipo and date
                elif form.cleaned_data["tipo"]:
                    # filters from the Producao model by date and tip
                    filtered = models.Producao.objects.filter(data__gte = form.cleaned_data["data_field"], produto_id__tipo = form.cleaned_data["tipo"])
            # if the user doesn't provide the date
            elif not form.cleaned_data["data_field"]:
                # if the user provided the produto
                if form.cleaned_data["produto"]:
                    # filters from the Producao model by produto
                    filtered = models.Producao.objects.filter(produto_id__nome = form.cleaned_data["produto"])
                # if the user provided only the tipo
                elif form.cleaned_data["tipo"]:
                    # filters from the Producao model by tip
                    filtered = models.Producao.objects.filter(produto_id__tipo = form.cleaned_data["tipo"])
            if filtered:
                success = 4
            else:
                success = 5
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
    # adds the categories
    context["types"] = types
    context["success"] = success
    context["filtered"] = filtered
    if request.method == "POST":
        return http.HttpResponseRedirect("/producao/")
    else:
        return TemplateResponse(request, "producao_new.html", context)


@login_required
def estoque(request):
    # handling forms
    success = 1
    filtered = []
    if request.method == "POST":
        form = website.forms.EstoqueData(request.POST or None)
        if form.is_valid():
            ingredient_id = models.Ingrediente.objects.get(nome=form.cleaned_data["ingrediente"])
            # function to update the stock
            ingredient_id.estoque += form.cleaned_data["quantidade"]
            ingredient_id.total_comprado += form.cleaned_data["quantidade"]
            ingredient_id.ultima_compra = date.today()
            ingredient_id.valor_comprado += form.cleaned_data["valor"]
            try:
                ingredient_id.preco_medio = ingredient_id.valor_comprado / ingredient_id.total_comprado
            except ZeroDivisionError:
                ingredient_id.preco_medio = 0

            ingredient_id.save()
            success = 2
        else:
            success = 3
    elif request.method == "GET":
        form = website.forms.EstoqueData(request.GET or None)
        if form.is_valid():
            if form.cleaned_data["data_field"]:
                if form.cleaned_data["ingrediente"]:
                    filtered = models.Ingrediente.objects.filter(ultima_compra__gte = form.cleaned_data["data_field"], nome = form.cleaned_data["ingrediente"])
                elif form.cleaned_data["tipo"]:
                    filtered = models.Ingrediente.objects.filter(ultima_compra__gte = form.cleaned_data["data_field"], tipo = form.cleaned_data["tipo"])
            elif not form.cleaned_data["data_field"]:
                if form.cleaned_data["ingrediente"]:
                    filtered = models.Ingrediente.objects.filter(nome = form.cleaned_data["ingrediente"])
                elif form.cleaned_data["tipo"]:
                    filtered = models.Ingrediente.objects.filter(tipo = form.cleaned_data["tipo"])
            if filtered:
                success = 4
            else:
                success = 5
    # gets all the distinct types of ingredient categories
    types = models.Ingrediente.objects.all().distinct("tipo").order_by("tipo")
    # gets all products
    ingredients = models.Ingrediente.objects.all()
    # creates a dictionary to store all categories and products
    context = {'ingredients': {}}
    # dynamically creates the dictionary containing categories and products
    for i in ingredients:
        for j in types:
            context['ingredients'][j.tipo] = models.Ingrediente.objects.filter(tipo=j.tipo)
    # adds the categories
    context["types"] = types
    context["success"] = success
    context["filtered"] = filtered

    return TemplateResponse(request, "estoque.html", context)


def test(request):
    produto = get_object_or_404(models.Ingrediente, id=1)
    print(produto.nome)
    print(produto.estoque)
    print(produto.estoque)
    context = {}
    return TemplateResponse(request, "index.html", context)
# def hello(request):
#     # form  = website.forms.NameForm(request.POST or None)
#     #
#     # if request.method == 'POST':
#     #     if form.is_valid():
#     #         print(form.cleaned_data['your_name'])
#     #         return http.HttpResponseRedirect('/thanks/')
#
#     context = {
#         'form': form,
#     }
#     return TemplateResponse(request, "hello.html", context)

# def contact_me(request):
#     form = website.forms.ClassForm(request.POST or None, request.FILES or None)
#
#     if request.method == "POST":
#         if form.is_valid():
#             print(form.cleaned_data)
#             email = EmailMessage(
#             form.cleaned_data["your_name"],
#             form.cleaned_data["your_question"],
#             form.cleaned_data["your_email"],
#             ["fimanishi@gmail.com"],
#             )
#             email.attach(form.cleaned_data["your_image"].name, form.cleaned_data["your_image"].read())
#             email.send(fail_silently=False)
#
#             return http.HttpResponseRedirect('/thanks')
#         else:
#             print(form.errors)
#
#     context = {}
#     return TemplateResponse(request, "contact_me.html", context)
#
# def thanks(request):
#     context = {}
#     return TemplateResponse(request, "thanks.html", context)
