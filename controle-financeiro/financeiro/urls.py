from django.urls import path
from .views import home, lancamentos, rel_lancamentos, rel_origens
from .views import lancamentos_save, rel_orcamentos, orcamentos_save
from .views import rel_categorias, orcamentos, delete_lcto, update_get_lcto
from .views import update_lcto, get_cotacao_dolar


urlpatterns = [
    path('', home),
    path('home/', home, name='home'),
    path('home/', get_cotacao_dolar, name='get_cotacao_dolar'),
    path('rel-lctos/', rel_lancamentos, name='rel_lancamentos'),
    path('rel-orctos/', rel_orcamentos, name='rel_orcamentos'),
    path('lancamentos_save/', lancamentos_save, name='lancamentos_save'),
    path('lancamentos/', lancamentos, name='lancamentos'),
    path('orcamentos/', orcamentos, name='orcamentos'),
    path('orcamentos_save/', orcamentos_save, name='orcamentos_save'),
    path('origens/', rel_origens, name='rel_origens'),
    path('categorias/', rel_categorias, name='rel_categorias'),
    path('delete_lcto/<int:id>/', delete_lcto, name='delete'),
    path('update_get_lcto/<int:id>/', update_get_lcto, name='update_get_lcto'),
    path('update_lcto/<int:id>/', update_lcto, name='update_lcto'),
]
