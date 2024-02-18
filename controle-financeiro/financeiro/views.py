from django.shortcuts import render
from financeiro.models import Lancamento, Origem, Categoria
from financeiro.services import Services

import locale


# Create your views here.
def home(request):
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
    diferenca = Services.calcular_diferencaORM()
    return render(request, 'financeiro/home.html', {"diferenca": diferenca})


def lancamentos(request):
    lctos = Lancamento.objects.all()
    cats = Categoria.objects.all()
    origens = Origem.objects.all()
    return render(request, 'financeiro/lancamentos.html', {"lctos": lctos,
                                                           "cats": cats,
                                                           "origens": origens})


def lancamentos_save(request):
    novo_lcto = Lancamento()
    if 'nome' in request.POST:
        novo_lcto.data = request.POST.get('data')
        novo_lcto.descricao = request.POST.get('descricao')
        novo_lcto.valor = request.POST.get('valor')
        novo_lcto.tipo_operacao = request.POST.get('tipo_operacao')
        novo_lcto.categoria_id = request.POST.get('categoria')
        novo_lcto.origem_id = request.POST.get('origem')
        novo_lcto.save()
    return render(request, 'financeiro/rel_lancamentos.html')


def rel_lancamentos(request):
    lctos = Lancamento.objects.all()
    for lcto in lctos:
        lcto.nome_origem = lcto.origem.nome
        lcto.nome_categoria = lcto.categoria.nome
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
