from django.urls import path
from .views import home, rel_lancamentos, rel_origens


urlpatterns = [
    path('', home),
    path('home', home),
    path('rel-lctos', rel_lancamentos),
    path('origens', rel_origens),
]
