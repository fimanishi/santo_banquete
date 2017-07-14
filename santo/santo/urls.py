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
import website.views_api
import website.views



urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', website.views.index, name="index"),
    url(r'^logout/$', logout,{'next_page': '/'}),
    url(r'^authenticated/$', website.views.authenticated, name="authenticated"),
    url(r'^pedidos/$', website.views.pedidos, name="pedidos"),
    url(r'^producao/add/$', website.views_api.producao_add, name="producao_add"),
    url(r'^producao/filter/$', website.views_api.producao_filter, name="producao_filter"),
    url(r'^producao/delete/$', website.views_api.producao_delete, name="producao_delete"),
    url(r'^estoque/add/$', website.views_api.estoque_add, name="estoque_add"),
    url(r'^estoque/filter/$', website.views_api.estoque_filter, name="estoque_filter"),
    url(r'^estoque/update/$', website.views_api.estoque_update, name="estqoue_update"),
    url(r'^producao/$', website.views.producao, name="producao"),
    url(r'^estoque/$', website.views.estoque, name="estoque"),
    url(r'^estoque_selection/$', website.views.estoque_selection, name="estoque_selection"),
    url(r'^escolher_fornecedor/', website.views.escolher_fornecedor, name="escolher_fornecedor"),
    url(r'^adicionar_cliente/$', website.views.adicionar_cliente, name="adicionar_cliente"),
    url(r'^novo_pedido/$', website.views.novo_pedido, name="novo_pedido"),
    url(r'^escolher_cliente/$', website.views.escolher_cliente, name="escolher_cliente"),
    url(r'^escolher_cliente/filter/$', website.views_api.escolher_cliente_filter, name="escolher_cliente_filter"),
    url(r'^cliente/update/$', website.views_api.cliente_update, name="cliente_update"),
    url(r'^finalizar_pedido/delivery/$', website.views_api.finalizar_pedido_delivery, name="finalizar_pedido_delivery"),
    url(r'^finalizar_pedido/$', website.views.finalizar_pedido, name="finalizar_pedido"),



]
