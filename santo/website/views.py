from django.template.response import TemplateResponse
import website.forms
from django import forms
from django import http
from django.core.mail import send_mail
from django.core.mail import EmailMessage
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth import logout, login
import website.models as models
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from datetime import date
from django.core.exceptions import ObjectDoesNotExist

# Create your views here.



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

@login_required
def pedidos(request):
    context = {}
    return TemplateResponse(request, "pedidos.html", context)

@login_required
def producao(request):
    # handling forms
    success = 1
    filtered = []
    if request.method == "POST":
        form = website.forms.ProducaoData(request.POST or None)
        if form.is_valid():
            product_id = models.Produto.objects.get(nome=form.cleaned_data["produto"])
            try:
                check = models.Producao.objects.get(produto_id=product_id.id, data=date.today())
                check.quantidade += form.cleaned_data["quantidade"]
                check.save()
            except ObjectDoesNotExist:
                producao_add = models.Producao.objects.create(produto=product_id, quantidade=form.cleaned_data["quantidade"])
            success = 2
        else:
            success = 3
    elif request.method == "GET":
        form = website.forms.ProducaoData(request.GET or None)
        if form.is_valid():
            if (form.cleaned_data["data_field"]):
                if (form.cleaned_data["produto"]):
                    print(date.today())
                    filtered = models.Producao.objects.filter(data__gte = form.cleaned_data["data_field"], produto_id__nome = form.cleaned_data["produto"])
            if filtered:
                success = 4
            else:
                success = 5




    # gets all the distinct types of food categories
    types = models.Produto.objects.filter(~Q(tipo="bebida")).distinct("tipo")
    # gets all products
    products = models.Produto.objects.all()
    # creates a dictionary to store all categories and products
    context = {'products': {}}
    # dynamically creates the dictionary containg categories and products
    for i in products:
        for j in types:
            context['products'][j.tipo] = models.Produto.objects.filter(tipo=j.tipo)
    # adds the categories
    context["types"] = types
    context["success"] = success
    context["filtered"] = filtered

    return TemplateResponse(request, "producao.html", context)

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
