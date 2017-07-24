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
    url(r'^producao/estoque/update/$', website.views_api.producao_estoque_update, name="producao_estoque_update"),
    url(r'^producao/estoque/$', website.views_api.producao_estoque, name="producao_estoque"),
    url(r'^estoque/add/$', website.views_api.estoque_add, name="estoque_add"),
    url(r'^estoque/add/update/$', website.views_api.estoque_add_update, name="estoque_add_update"),
    url(r'^estoque/add/delete/$', website.views_api.estoque_add_delete, name="estoque_add_delete"),
    url(r'^estoque/add/finish/$', website.views_api.estoque_add_finish, name="estoque_add_finish"),
    url(r'^estoque/add/init/$', website.views_api.estoque_add_init, name="estoque_add_init"),
    url(r'^estoque/filter/$', website.views_api.estoque_filter, name="estoque_filter"),
    url(r'^estoque/update/$', website.views_api.estoque_update, name="estqoue_update"),
    url(r'^producao/$', website.views.producao, name="producao"),
    url(r'^producao_selection/$', website.views.producao_selection, name="producao_selection"),
    url(r'^estoque/$', website.views.estoque, name="estoque"),
    url(r'^estoque_selection/$', website.views.estoque_selection, name="estoque_selection"),
    url(r'^escolher_fornecedor/$', website.views.escolher_fornecedor, name="escolher_fornecedor"),
    url(r'^escolher_fornecedor/filter/$', website.views_api.escolher_fornecedor_filter, name="escolher_fornecedor_filter"),
    url(r'^adicionar_cliente/$', website.views.adicionar_cliente, name="adicionar_cliente"),
    url(r'^novo_pedido/$', website.views.novo_pedido, name="novo_pedido"),
    url(r'^novo_pedido/add/$', website.views_api.novo_pedido_add, name="novo_pedido_add"),
    url(r'^novo_pedido/delete/$', website.views_api.novo_pedido_delete, name="novo_pedido_delete"),
    url(r'^novo_pedido/update/$', website.views_api.novo_pedido_update, name="novo_pedido_update"),
    url(r'^escolher_cliente/$', website.views.escolher_cliente, name="escolher_cliente"),
    url(r'^escolher_cliente/filter/$', website.views_api.escolher_cliente_filter, name="escolher_cliente_filter"),
    url(r'^cliente/update/$', website.views_api.cliente_update, name="cliente_update"),
    url(r'^cliente/add/$', website.views_api.cliente_add, name="cliente_add"),
    url(r'^finalizar_pedido/delivery/add/$', website.views_api.finalizar_pedido_delivery_add, name="finalizar_pedido_delivery_add"),
    url(r'^finalizar_pedido/$', website.views.finalizar_pedido, name="finalizar_pedido"),
    url(r'^finalizar_pedido/init/$', website.views_api.finalizar_pedido_init, name="finalizar_pedido_init"),
    url(r'^cart_user/$', website.views_api.cart_user, name="cart_user"),
    url(r'^adicionar_fornecedor/$', website.views.adicionar_fornecedor, name="adicionar_fornecedor"),
    url(r'^fornecedor/add/$', website.views_api.fornecedor_add, name="fornecedor_add"),
    url(r'^fornecedor/update/$', website.views_api.fornecedor_update, name="fornecedor_update"),
    url(r'^nova_compra/$', website.views.nova_compra, name="nova_compra"),
    url(r'^nova_compra/add/$', website.views_api.nova_compra_add, name="nova_compra_add"),


]
