from django.template.response import TemplateResponse
import website.forms
from django import forms
from django import http
from django.core.mail import send_mail
from django.core.mail import EmailMessage
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth import logout, login

# Create your views here.



def index(request):
    form = website.forms.UserForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            user = authenticate(request, username=form.cleaned_data["user_name"], password=form.cleaned_data["user_password"])
            if user is not None:
                login(request, user)
                return http.HttpResponseRedirect("/authenticated")
    context = {}
    return TemplateResponse(request, "index.html", context)


def authenticated(request):
    context = {}
    return TemplateResponse(request, "authenticated.html", context)

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
