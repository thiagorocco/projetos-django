from django.shortcuts import render
from financeiro.models import Lancamento
from financeiro.services import Services


# Create your views here.
def home(request):
    lctos = Lancamento.objects.all()
    diferenca = Services.calcular_diferencaORM()
    return render(request, 'financeiro/index.html', {"lctos": lctos,
                                                     "diferenca": diferenca})
