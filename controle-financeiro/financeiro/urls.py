from django.urls import path
from .views import home, rel_lancamentos, rel_origens, rel_categorias


urlpatterns = [
    path('', home),
    path('home', home),
    path('rel-lctos', rel_lancamentos),
    path('origens', rel_origens),
    path('categorias', rel_categorias),
]
