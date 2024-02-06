from django.contrib import admin
from .models import Categoria, Lancamento, Orcamento, Origem

admin.site.register(Categoria)
admin.site.register(Lancamento)
admin.site.register(Orcamento)
admin.site.register(Origem)
