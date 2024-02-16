from django.shortcuts import render
from financeiro.models import Lancamento, Origem, Categoria
from financeiro.services import Services

import locale


# Create your views here.
def home(request):
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
    diferenca = Services.calcular_diferencaORM()
    return render(request, 'financeiro/home.html', {"diferenca": diferenca})


def rel_lancamentos(request):
    lctos = Lancamento.objects.all()
    return render(request, 'financeiro/rel_lancamentos.html', {"lctos": lctos})


def rel_origens(request):
    nova_origem = Origem()
    if 'nome' in request.POST:
        nova_origem.nome = request.POST.get('nome')
        nova_origem.save()
    origens = Origem.objects.all()
    return render(request, 'financeiro/origens.html', {"origens": origens})


def rel_categorias(request):
    nova_categoria = Categoria()
    if 'nome' in request.POST:
        nova_categoria.nome = request.POST.get('nome')
        nova_categoria.save()
    categorias = Categoria.objects.all()
    return render(request, 'financeiro/categorias.html',
                  {"categorias": categorias})
