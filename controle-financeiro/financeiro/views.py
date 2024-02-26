from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from financeiro.models import Lancamento, Origem, Categoria, Orcamento
from financeiro.services import Services
import locale
import requests


def get_cotacao_dolar(request):
    url = 'https://economia.awesomeapi.com.br/json/last/USD-BRL'

    # Faz a requisição à API
    response = requests.get(url)

    # Verifica se a requisição foi bem-sucedida (código 200)
    if response.status_code == 200:
        # Extrai os dados do JSON retornado pela API
        data = response.json()
        # Extraindo os campos desejados
        cotacao_dolar = data['USDBRL']['bid']
        create_date = data['USDBRL']['create_date']
    else:
        cotacao_dolar = create_date = None
    # Renderiza o template com os dados
    return render(request, 'fragments/navbar.html', {
        'cotacao_dolar': cotacao_dolar,
        'create_date': create_date,
    })


def home(request):
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
    page = 'home'
    diferenca = Services.calcular_diferencaORM()
    return render(request, 'financeiro/home.html', {"diferenca": diferenca,
                                                    "page": page})


def lancamentos(request):
    cats = Categoria.objects.all()
    origens = Origem.objects.all()
    return render(request, 'financeiro/lancamentos.html', {"cats": cats,
                                                           "origens": origens})


def lancamentos_save(request):
    novo_lcto = Lancamento()
    saldos = Services.calcular_diferencaORM()
    campos_obrigatorios = ['data', 'descricao', 'tipo_operacao', 'valor',
                           'categoria', 'origem']
    if all(campo in request.POST for campo in campos_obrigatorios):
        novo_lcto.data = request.POST.get('data')
        novo_lcto.descricao = request.POST.get('descricao')
        novo_lcto.tipo_operacao = request.POST.get('tipo_operacao')
        novo_lcto.valor = Decimal(request.POST.get('valor', 0.0))
        novo_lcto.categoria_id = int(request.POST.get('categoria', 0))
        novo_lcto.origem_id = int(request.POST.get('origem', 0))
        cats = Categoria.objects.all()
        origens = Origem.objects.all()

        if novo_lcto.valor <= 0:
            msn = "Valor do lançamento não pode ser zero ou negativo!"
            return render(request, 'financeiro/lancamentos.html',
                          {"msn": msn,
                           "cats": cats,
                           "origens": origens})

        if novo_lcto.tipo_operacao == 's':
            for saldo in saldos:
                if saldo['origem__nome'] == novo_lcto.origem.nome:
                    if saldo['diferenca'] >= novo_lcto.valor:
                        novo_lcto.save()
                        return redirect(reverse('rel_lancamentos'))
                    else:
                        print('Saldo: ', saldo['diferenca'])
                        print('Valor lcto: ', novo_lcto.valor)
                        msn = f"Saldo insuficiente em {saldo['origem__nome']}"
                        return render(request,
                                      'financeiro/lancamentos.html',
                                      {"msn": msn,
                                       "cats": cats,
                                       "origens": origens})
        else:
            novo_lcto.save()
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
    # pega a string vvalor e substitui a vírgula pelo ponto.
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


def delete_orcamento(request, id):
    orc = Orcamento.objects.get(id=id)
    orc.delete()
    return redirect(reverse('rel_orcamentos'))


def rel_origens(request):
    nova_origem = Origem()
    if 'nome' in request.POST:
        nova_origem.nome = request.POST.get('nome')
        nova_origem.save()
    origens = Origem.objects.all()
    return render(request, 'financeiro/origens.html', {"origens": origens})


def delete_origem(request, id):
    # origem = Origem.objects.get(id=id)
    origem = get_object_or_404(Origem, id=id)
    # Verificar se existem lançamentos associados a esta origem
    if origem.lancamento_set.exists():
        messages.error(request, "Impossível excluir esta origem. "
                                "Existem lançamentos associados.")
    else:
        origem.delete()
        messages.success(request, "Origem excluída com sucesso.")

    return redirect(reverse('rel_origens'))


def rel_categorias(request):
    nova_categoria = Categoria()
    if 'nome' in request.POST:
        nova_categoria.nome = request.POST.get('nome')
        nova_categoria.save()
    categorias = Categoria.objects.all()
    return render(request, 'financeiro/categorias.html',
                  {"categorias": categorias})


def del_categorias(request, id):
    categoria = get_object_or_404(Categoria, id=id)
    # Verificar se existem lançamentos associados a esta categoria
    if categoria.lancamento_set.exists():
        messages.error(request, "Impossível excluir esta categoria. "
                                "Existem lançamentos associados.")
    else:
        categoria.delete()
        messages.success(request, "Categoria excluída com sucesso.")

    return redirect(reverse('rel_origens'))


def rel_orcado_realizado(request):
    return render(request, 'financeiro/orcado-realizado.html')
