from django.shortcuts import render
from financeiro.models import Lancamento
from financeiro.services import Services

import locale


# Create your views here.
def home(request):
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
    lctos = Lancamento.objects.all()
    diferenca = Services.calcular_diferencaORM()
    return render(request, 'financeiro/index.html', {"lctos": lctos,
                                                     "diferenca": diferenca})
