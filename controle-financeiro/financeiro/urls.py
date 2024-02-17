from django.urls import path
from .views import home, lancamentos, rel_lancamentos, rel_origens
from .views import rel_categorias


urlpatterns = [
    path('', home),
    path('home/', home, name='home'),
    path('rel-lctos/', rel_lancamentos, name='rel_lancamentos'),
    path('lctos/', lancamentos, name='lancamentos'),
    path('origens/', rel_origens, name='rel_origens'),
    path('categorias/', rel_categorias, name='rel_categorias'),
]
