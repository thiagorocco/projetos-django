from django.shortcuts import render
from financeiro.models import Lancamento


# Create your views here.
def home(request):
    lctos = Lancamento.objects.all()
    diferenca = Lancamento.calcular_diferenca()
    return render(request, 'financeiro/index.html', {"lctos": lctos,
                                                     "diferenca": diferenca})
