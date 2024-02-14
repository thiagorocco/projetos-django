from django.urls import path
from .views import home, rel_lancamentos


urlpatterns = [
    path('', home),
    path('rel-lctos', rel_lancamentos)
]
