from decimal import Decimal
from django.shortcuts import render, redirect
from django.urls import reverse
from financeiro.models import Lancamento, Origem, Categoria, Orcamento
from financeiro.services import Services
import locale


# Create your views here.
def home(request):
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
    diferenca = Services.calcular_diferencaORM()
    return render(request, 'financeiro/home.html', {"diferenca": diferenca})


def lancamentos(request):
    cats = Categoria.objects.all()
    origens = Origem.objects.all()
    return render(request, 'financeiro/lancamentos.html', {"cats": cats,
                                                           "origens": origens})


def lancamentos_save(request):
    novo_lcto = Lancamento()
    campos_obrigatorios = ['data', 'descricao', 'tipo_operacao', 'valor',
                           'categoria', 'origem']
    if all(campo in request.POST for campo in campos_obrigatorios):
        novo_lcto.data = request.POST.get('data')
        novo_lcto.descricao = request.POST.get('descricao')
        novo_lcto.tipo_operacao = request.POST.get('tipo_operacao')
        novo_lcto.valor = Decimal(request.POST.get('valor', 0.0))
        novo_lcto.categoria_id = int(request.POST.get('categoria', 0))
        novo_lcto.origem_id = int(request.POST.get('origem', 0))
        novo_lcto.save()
    # Redirecionando para a view rel_lancamentos
    return redirect(reverse('rel_lancamentos'))


def rel_lancamentos(request):
    lctos = Lancamento.objects.all()
    for lcto in lctos:
        lcto.nome_origem = lcto.origem.nome
        lcto.nome_categoria = lcto.categoria.nome
    return render(request, 'financeiro/rel_lancamentos.html', {"lctos": lctos})


def delete_lcto(request, id):
    lcto = Lancamento.objects.get(id=id)
    lcto.delete()
    return redirect(reverse('rel_lancamentos'))


def update_get_lcto(request, id):
    lcto = Lancamento.objects.get(id=id)
    # vvalor pega lcto.valor e converte em string
    vvalor = str(lcto.valor)
    # pvalor pega a string vvalor e substitui a vírgula pelo ponto. Ex: 1,10 -> 1.10
    pvalor = vvalor.replace(",", ".")
    cats = Categoria.objects.all()
    origens = Origem.objects.all()
    return render(request, 'financeiro/editar_lancamento.html',
                  {"lcto": lcto,
                   "cats": cats,
                   "origens": origens,
                   "pvalor": pvalor})


def update_lcto(request, id):
    lcto = Lancamento.objects.get(id=id)
    lcto.data = request.POST['data']
    lcto.descricao = request.POST['descricao']
    lcto.valor = Decimal(request.POST.get('valor', 0.0))
    lcto.tipo_operacao = request.POST['tipo_operacao']
    lcto.categoria_id = int(request.POST.get('categoria', 0))
    lcto.origem_id = int(request.POST.get('origem', 0))
    lcto.save()
    return redirect(reverse('rel_lancamentos'))


def orcamentos(request):
    cats = Categoria.objects.all()
    return render(request, 'financeiro/orcamentos.html', {"cats": cats})


def orcamentos_save(request):
    novo_orcamento = Orcamento()
    campos_obrigatorios = ['data', 'categoria', 'valor']
    if all(campo in request.POST for campo in campos_obrigatorios):
        novo_orcamento.data = request.POST.get('data')
        novo_orcamento.categoria_id = int(request.POST.get('categoria', 0))
        novo_orcamento.valor = Decimal(request.POST.get('valor', 0.0))
        novo_orcamento.save()
    return redirect(reverse('rel_orcamentos'))


def rel_orcamentos(request):
    orcamentos = Orcamento.objects.all()
    for orcamento in orcamentos:
        orcamento.nome_categoria = orcamento.categoria.nome
    return render(request, 'financeiro/rel_orcamentos.html',
                  {"orcamentos": orcamentos})


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
