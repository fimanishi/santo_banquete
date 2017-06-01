"""santo URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth.views import logout

import website.views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', website.views.index, name="index"),
    url(r'^logout/$', logout,{'next_page': '/'}),
    url(r'^authenticated/$', website.views.authenticated, name="authenticated"),
    url(r'^test/$', website.views.test, name="test"),
    url(r'^pedidos/$', website.views.pedidos, name="pedidos"),
    url(r'^producao/$', website.views.producao, name="producao"),
    
    # url(r'^hello$', website.views.hello, name="hello"),
    # url(r'^contact_me$', website.views.contact_me, name="contact_me"),
    # url(r'^thanks$', website.views.thanks, name="thanks"),
]
