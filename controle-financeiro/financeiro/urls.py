from django.urls import path
from .views import home, lancamentos, rel_lancamentos, rel_origens
from .views import lancamentos_save, rel_orcamentos, orcamentos_save
from .views import rel_categorias, orcamentos


urlpatterns = [
    path('', home),
    path('home/', home, name='home'),
    path('rel-lctos/', rel_lancamentos, name='rel_lancamentos'),
    path('rel-orctos/', rel_orcamentos, name='rel_orcamentos'),
    path('lancamentos_save/', lancamentos_save, name='lancamentos_save'),
    path('lancamentos/', lancamentos, name='lancamentos'),
    path('orcamentos/', orcamentos, name='orcamentos'),
    path('orcamentos_save/', orcamentos_save, name='orcamentos_save'),
    path('origens/', rel_origens, name='rel_origens'),
    path('categorias/', rel_categorias, name='rel_categorias'),
]
