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
    form = website.forms.UserForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            user = authenticate(request, username=form.cleaned_data["user_name"], password=form.cleaned_data["user_password"])
            if user is not None:
                login(request, user)
                return http.HttpResponseRedirect("/authenticated/")
    context = {}
    return TemplateResponse(request, "index.html", context)


@login_required
def authenticated(request):
    context = {}
    return TemplateResponse(request, "authenticated.html", context)


# page to add a new client. does the verification of the fields and adds to the database
# required inputs: nome completo and cidade
@login_required
def adicionar_cliente(request):
    request.session["cart"] = []
    request.session["cart_user"] = {}
    success = 1
    client_id = ""
    if request.method == "POST":
        form = website.forms.ClienteData(request.POST or None)
        if form.is_valid():
            exist_check = models.Cliente.objects.filter(nome=form.cleaned_data["nome"].lower())
            if exist_check:
                for each in exist_check:
                    if each.telefone == form.cleaned_data["telefone"]:
                        success = 4
                    else:
                        models.Cliente.objects.create(nome=form.cleaned_data["nome"].lower(),
                                                      telefone=form.cleaned_data["telefone"],
                                                      tipo=form.cleaned_data["tipo"],
                                                      endereco=form.cleaned_data["endereco"].lower(),
                                                      bairro=form.cleaned_data["bairro"],
                                                      cidade=form.cleaned_data["cidade"].lower(),
                                                      referencia=form.cleaned_data["referencia"].lower())
                        success = 2
                        client_id = models.Cliente.objects.latest()
            else:
                models.Cliente.objects.create(nome=form.cleaned_data["nome"].lower(),
                                              telefone=form.cleaned_data["telefone"],
                                              tipo=form.cleaned_data["tipo"],
                                              endereco=form.cleaned_data["endereco"].lower(),
                                              bairro=form.cleaned_data["bairro"],
                                              cidade=form.cleaned_data["cidade"].lower(),
                                              referencia=form.cleaned_data["referencia"].lower())
                success = 2
                client_id = models.Cliente.objects.last()
        else:
            success = 3

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



@login_required
def novo_pedido(request):
    success = 1
    if request.method == "GET":
        form = website.forms.ClienteSelection(request.GET or None)
        if form.is_valid():
            request.session["cart_user"] = models.Cliente.objects.filter(id=form.cleaned_data["cliente"]).values()[0]
        else:
            http.HttpResponseRedirect("/escolher_cliente/")
    elif request.method == "POST":
        form = website.forms.Pedido(request.POST or None)
        if form.is_valid():
            request.session["cart"].append({"product_id": models.Produto.objects.get(nome=form.cleaned_data["produto"]).id, "produto": form.cleaned_data["produto"], "quantity": float(form.cleaned_data["quantidade"])})
            success = 2
        else:
            success = 3
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
    context["cliente"] = request.session["cart_user"]
    context["cart"] = request.session["cart"]
    context["success"] = success
    request.session.save()
    return TemplateResponse(request, "novo_pedido.html", context)


@login_required
def escolher_cliente(request):
    request.session["cart"] = []
    request.session["cart_user"] = {}
    filtered = []
    success = 1
    try:
        referer = request.META['HTTP_REFERER']
    except KeyError:
        referer = ""
    check = re.search(r"escolher_cliente", referer)
    if request.method == "GET" and check:
        form = website.forms.ClienteSearch(request.GET or None)
        if form.is_valid():
            success = 2
            if form.cleaned_data["nome"] and form.cleaned_data["telefone"]:
                filtered = models.Cliente.objects.filter(nome__icontains=form.cleaned_data["nome"], telefone=form.cleaned_data["telefone"])
            elif form.cleaned_data["nome"]:
                filtered = models.Cliente.objects.filter(nome__icontains=form.cleaned_data["nome"])
            elif form.cleaned_data["telefone"]:
                filtered = models.Cliente.objects.filter(telefone=form.cleaned_data["telefone"])
            if not filtered:
                success = 3
        else:
            success = 4  

    context = {"filtered": filtered, "success": success}
    print(success)
    return TemplateResponse(request, "escolher_cliente.html", context)


@login_required
def producao(request):
    # handling forms
    success = 1
    filtered = []
    if request.method == "POST":
        form = website.forms.ProducaoData(request.POST or None)
        if form.is_valid():
            product_id = models.Produto.objects.get(nome=form.cleaned_data["produto"])
            # function to update the stock

            quantidades = models.Quantidade.objects.filter(produto_id=product_id.id)
            for quantidade in quantidades:
                quantidade_get = models.Quantidade.objects.get(id=quantidade.id)
                ingredient_to_change = models.Ingrediente.objects.get(id=quantidade_get.ingrediente_id)
                ingredient_to_change.estoque -= quantidade_get.quantidade_unitaria * form.cleaned_data["quantidade"]
                ingredient_to_change.save()


            try:
                check = models.Producao.objects.get(produto_id=product_id.id, data=date.today())
                check.quantidade += form.cleaned_data["quantidade"]
                check.save()
            except ObjectDoesNotExist:
                models.Producao.objects.create(produto=product_id, quantidade=form.cleaned_data["quantidade"], usuario = request.user )
            success = 2
        else:
            success = 3
    elif request.method == "GET":
        form = website.forms.ProducaoData(request.GET or None)
        if form.is_valid():
            if form.cleaned_data["data_field"]:
                if form.cleaned_data["produto"]:
                    filtered = models.Producao.objects.filter(data__gte = form.cleaned_data["data_field"], produto_id__nome = form.cleaned_data["produto"])
                elif form.cleaned_data["tipo"]:
                    filtered = models.Producao.objects.filter(data__gte = form.cleaned_data["data_field"], produto_id__tipo = form.cleaned_data["tipo"])
            elif not form.cleaned_data["data_field"]:
                if form.cleaned_data["produto"]:
                    filtered = models.Producao.objects.filter(produto_id__nome = form.cleaned_data["produto"])
                elif form.cleaned_data["tipo"]:
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

    return TemplateResponse(request, "producao.html", context)


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
