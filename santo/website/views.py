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


# required inputs: nome completo and cidade
@login_required
def adicionar_cliente(request):
    # initializes an empty cart list in the session as the view will redirect to a new order
    request.session["cart"] = []
    request.session["cart_serializer"] = []
    # initializes an empty cart_user dictionary in the session as the view will redirect to a new order
    request.session["cart_user"] = {}

    return TemplateResponse(request, "adicionar_cliente.html")


@login_required
def adicionar_fornecedor(request):
    # initializes an empty cart list in the session as the view will redirect to a new order
    request.session["cart"] = []
    request.session["cart_serializer"] = []
    # initializes an empty cart_user dictionary in the session as the view will redirect to a new order
    request.session["cart_user"] = {}

    return TemplateResponse(request, "adicionar_fornecedor.html")


@login_required
def pedidos(request):
    return TemplateResponse(request, "pedidos.html")


@login_required
def finalizar_pedido(request):
    subtotal = 0
    for item in request.session["cart"]:
        subtotal += item["cost"] * item["quantity"]
    context = {}
    context["cliente"] = request.session["cart_user"]
    context["cart"] = request.session["cart"]
    context["subtotal"] = subtotal
    return TemplateResponse(request, "finalizar_pedido.html", context)


@login_required
def nova_compra(request):
    return TemplateResponse(request, "nova_compra.html")


@login_required
def novo_pedido(request):
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
    return TemplateResponse(request, "novo_pedido.html", context)


@login_required
def escolher_cliente(request):
    # initializes an empty cart list in the session as the view will redirect to a new order
    request.session["cart"] = []
    request.session["cart_serializer"] = []
    # initializes an empty cart_user dictionary in the session as the view will redirect to a new order
    request.session["cart_user"] = {}
    return TemplateResponse(request, "escolher_cliente.html")


@login_required
def producao(request):
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
    return TemplateResponse(request, "producao_react.html", context)


@login_required
def producao_selection(request):
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
    return TemplateResponse(request, "producao_selection.html", context)


@login_required
def estoque(request):
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

    return TemplateResponse(request, "estoque.html", context)


@login_required
def estoque_selection(request):
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

    return TemplateResponse(request, "estoque_selection.html", context)


@login_required
def escolher_fornecedor(request):
    # initializes an empty cart list in the session as the view will redirect to a new order
    request.session["cart"] = []
    # initializes an empty cart_user dictionary in the session as the view will redirect to a new order
    request.session["cart_supplier"] = {}
    # initializes an empty list that will receive filtered items from db
    filtered = []
    # if the current view was the referer
    if request.method == "GET":
        # gets cliente from ClienteSearch form
        form = website.forms.ClienteSearch(request.GET or None)
        if form.is_valid():
            # success = 2 means that the validation passed and matches to the filter were found
            success = 2
            # if the user inputs nome and telefone, filters for a match for both
            if form.cleaned_data["nome"] and form.cleaned_data["telefone"]:
                filtered = models.Cliente.objects.filter(nome__icontains=form.cleaned_data["nome"],
                                                         telefone=form.cleaned_data["telefone"])
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
    return TemplateResponse(request, "escolher_fornecedor.html")

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
