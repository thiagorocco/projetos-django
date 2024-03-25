from decimal import Decimal
from django.db import IntegrityError
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from financeiro.models import Lancamento, Origem, Categoria, Orcamento
from financeiro.services import Services
import locale
import requests
from datetime import datetime
from django.db.models import Q


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
        try:
            novo_lcto.data = request.POST.get('data')
            novo_lcto.tipo_operacao = request.POST.get('tipo_operacao')
            novo_lcto.valor = Decimal(request.POST.get('valor', 0.0))
            novo_lcto.categoria_id = int(request.POST.get('categoria', 0))
            novo_lcto.origem_id = int(request.POST.get('origem', 0))

            descricao = str(request.POST.get('descricao'))
            descricao = descricao.strip()
            if descricao != '':
                novo_lcto.descricao = descricao
            else:
                messages.error(request, "Descrição inválida!")
                return redirect(reverse('lancamentos'))                     
            if novo_lcto.valor <= 0:
                messages.error(request, "Valor do lançamento não pode ser zero ou negativo!")
                return redirect(reverse('lancamentos'))
            if novo_lcto.tipo_operacao == 's':
                for saldo in saldos:
                    if saldo['origem__nome'] == novo_lcto.origem.nome:
                        if saldo['diferenca'] >= novo_lcto.valor:
                            novo_lcto.save()
                            messages.success(request, "Lançamento cadastrado com sucesso!")
                            return redirect(reverse('lancamentos'))
                        else:
                            messages.error(request, f"Saldo insuficiente em {saldo['origem__nome']}")
                            return redirect(reverse('lancamentos'))
            else:
                novo_lcto.save()
                messages.success(request, "Lançamento cadastrado com sucesso!")
                return redirect(reverse('lancamentos'))
        except:
            messages.error(request, "Preencha os dados corretamente!")
            return redirect(reverse('lancamentos'))


def update_lcto(request, id):
    novo_lcto = Lancamento.objects.get(id=id)
    saldos = Services.calcular_diferencaORM()
    campos_obrigatorios = ['data', 'descricao', 'tipo_operacao', 'valor',
                           'categoria', 'origem']
    if all(campo in request.POST for campo in campos_obrigatorios):
        try:
            novo_lcto.data = request.POST.get('data')
            novo_lcto.tipo_operacao = request.POST.get('tipo_operacao')
            novo_lcto.valor = Decimal(request.POST.get('valor', 0.0))
            novo_lcto.categoria_id = int(request.POST.get('categoria', 0))
            novo_lcto.origem_id = int(request.POST.get('origem', 0))

            descricao = str(request.POST.get('descricao'))
            descricao = descricao.strip()
            if descricao != '':
                novo_lcto.descricao = descricao
            else:
                messages.error(request, "Descrição inválida!")
                return redirect(reverse('update_get_lcto',
                                        kwargs={'id': novo_lcto.id}))

            if novo_lcto.valor <= 0:
                messages.error(request, "Valor do lançamento não pode ser zero\
                               ou negativo!")
                return redirect(reverse('update_get_lcto',
                                        kwargs={'id': novo_lcto.id}))

            if novo_lcto.tipo_operacao == 's':
                for saldo in saldos:
                    if saldo['origem__nome'] == novo_lcto.origem.nome:
                        if saldo['diferenca'] >= novo_lcto.valor:
                            novo_lcto.save()
                            return redirect(reverse('rel_lancamentos'))
                        else:
                            messages.error(request, f"Saldo insuficiente em\
                                           {saldo['origem__nome']}")
                            return redirect(reverse('update_get_lcto',
                                            kwargs={'id': novo_lcto.id}))
            else:
                novo_lcto.save()
                messages.success(request, "Lançamento alterado com sucesso!")
                return redirect(reverse('update_get_lcto',
                                    kwargs={'id': novo_lcto.id}))
        except:
            messages.error(request, "Preencha os dados corretamente!")
            return redirect(reverse('update_get_lcto',
                                    kwargs={'id': novo_lcto.id}))


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


def rel_lancamentos(request):
    lctos = Lancamento.objects.all().order_by('data')
    categorias = Categoria.objects.all().order_by('nome')
    origens = Origem.objects.all().order_by('nome')

    get_dt_ini = request.GET.get('data-inicio')
    get_dt_fim = request.GET.get('data-fim')
    get_cat = request.GET.get('categoria')
    get_op = request.GET.get('operacao')
    get_or = request.GET.get('origem')
    imprimir = False
    sem_resultados = False
    cat_sel = -1
    op_sel = 't'
    or_sel = -1

    if get_dt_ini and get_dt_fim and get_cat:
        # print('operação: ', get_op)
        data1 = datetime.strptime(get_dt_ini, '%Y-%m-%d')
        data2 = datetime.strptime(get_dt_fim, '%Y-%m-%d')
        cat_sel = int(get_cat)
        or_sel = int(get_or)
        op_sel = get_op

        if data1 > data2:
            messages.error(request, "Data inicial deve ser menor que a data final")
            return redirect(reverse('rel_lancamentos'))
        try:
            # Criando um filtro base
            filtro = Q(data__range=[get_dt_ini, get_dt_fim])
            
            # Adicionando condições ao filtro conforme os parâmetros passados
            if cat_sel != -1:
                filtro &= Q(categoria__id=cat_sel)
            if or_sel != -1:
                filtro &= Q(origem__id=or_sel)
            if op_sel != 't':
                filtro &= Q(tipo_operacao=op_sel)

            # Aplicando o filtro e ordenando por data
            lctos = Lancamento.objects.filter(filtro).order_by('data')
            
            # Verificando se há resultados
            sem_resultados = not lctos.exists()
            imprimir = True
        except:
            messages.error(request, "Preencha o formulário corretamente")
            return redirect(reverse('rel_lancamentos'))   

    for lcto in lctos:
        lcto.nome_origem = lcto.origem.nome
        lcto.nome_categoria = lcto.categoria.nome
    lancamentos = Services.paginacao(request, lctos)
    return render(request, 'financeiro/rel_lancamentos.html',
                  {"lctos": lancamentos,
                   "imprimir": imprimir,
                   "dtini": get_dt_ini,
                   "dtfim": get_dt_fim,
                   "cat": cat_sel,
                   "op": op_sel,
                   "orig": or_sel,
                   "sem_resultados": sem_resultados,
                   "categorias": categorias,
                   "origens": origens
                   })


def delete_lcto(request, id):
    lcto = Lancamento.objects.get(id=id)
    lcto.delete()
    return redirect(reverse('rel_lancamentos'))


def orcamentos(request):
    cats = Categoria.objects.all()
    return render(request, 'financeiro/orcamentos.html', {"cats": cats})


def orcamentos_save(request):
    novo_orcamento = Orcamento()
    campos_obrigatorios = ['data', 'categoria', 'valor']
    if all(campo in request.POST for campo in campos_obrigatorios):
        try:
            novo_orcamento.data = request.POST.get('data')
            novo_orcamento.categoria_id = int(request.POST.get('categoria', 0))
            novo_orcamento.valor = Decimal(request.POST.get('valor', 0.0))
         
            if novo_orcamento.valor <= 0:
                messages.error(request, "Valor do orçamento não pode ser zero ou negativo!")
                return redirect(reverse('orcamentos'))
           
            novo_orcamento.save()
            messages.success(request, "Orçamento cadastrado com sucesso!")
            return redirect(reverse('orcamentos'))
        except:
            messages.error(request, "Preencha os dados corretamente!")
            return redirect(reverse('orcamentos'))


def rel_orcamentos(request):
    orcamentos = Orcamento.objects.all().order_by('data')
    categorias = Categoria.objects.all().order_by('nome')
    get_dt_ini = request.GET.get('data-inicio')
    get_dt_fim = request.GET.get('data-fim')
    get_cat = request.GET.get('categoria')
    imprimir = False
    sem_resultados = False
    cat = -1
    # Implemente os filtros aqui
    if get_dt_ini and get_dt_fim and get_cat:
        data1 = datetime.strptime(get_dt_ini, '%Y-%m-%d')
        data2 = datetime.strptime(get_dt_fim, '%Y-%m-%d')
        if data1 > data2:
            messages.error(request, "Data inicial deve ser menor que a data final")
            return redirect(reverse('rel_orcamentos'))
        try:
            cat = int(get_cat)
            if cat == -1:
                orcamentos = Orcamento.objects.filter(data__range=[get_dt_ini, get_dt_fim]).order_by('data')
                imprimir = True
                sem_resultados = True if not orcamentos.exists() else False
            else:
                orcamentos = Orcamento.objects.filter(
                    data__range=[get_dt_ini, get_dt_fim],
                    categoria__id=get_cat).order_by('data')
                imprimir = True
                sem_resultados = True if not orcamentos.exists() else False            
        except:
            messages.error(request, "Preencha o formulário corretamente")
            return redirect(reverse('rel_orcamentos'))
    for orcamento in orcamentos:
        orcamento.nome_categoria = orcamento.categoria.nome
    orcs = Services.paginacao(request, orcamentos)
    return render(request, 'financeiro/rel_orcamentos.html',
                  {"orcamentos": orcs,
                   "imprimir": imprimir,
                   "dtini": get_dt_ini,
                   "dtfim": get_dt_fim,
                   "cat": cat,
                   "sem_resultados": sem_resultados,
                   "categorias": categorias})


def delete_orcamento(request, id):
    orc = Orcamento.objects.get(id=id)
    orc.delete()
    return redirect(reverse('rel_orcamentos'))


def update_get_orcamento(request, id):
    orcamento = Orcamento.objects.get(id=id)
    # vvalor pega lcto.valor e converte em string
    vvalor = str(orcamento.valor)
    # pega a string vvalor e substitui a vírgula pelo ponto.
    pvalor = vvalor.replace(",", ".")
    cats = Categoria.objects.all()
    return render(request, 'financeiro/editar_orcamento.html',
                  {"orcamento": orcamento,
                   "cats": cats,
                   "pvalor": pvalor})


def update_orcamento(request, id):
    orcamento = Orcamento.objects.get(id=id)
    campos_obrigatorios = ['data', 'categoria', 'valor']
    if all(campo in request.POST for campo in campos_obrigatorios):
        try:
            orcamento.data = request.POST.get('data')
            orcamento.categoria_id = int(request.POST.get('categoria', 0))
            orcamento.valor = Decimal(request.POST.get('valor', 0.0))

            if orcamento.valor <= 0:
                messages.error(request, "Valor do lançamento não pode ser zero\
                               ou negativo!")
                return redirect(reverse('update_get_orcamento',
                                        kwargs={'id': orcamento.id}))
            else:
                orcamento.save()
                messages.success(request, "Orcamento alterado com sucesso!")
                return redirect(reverse('orcamentos'))
        except:
            messages.error(request, "Preencha os dados corretamente!")
            return redirect(reverse('update_get_orcamento',
                                    kwargs={'id': orcamento.id}))


def rel_origens(request):
    nova_origem = Origem()
    nome = str(request.POST.get('nome'))
    # Impede a inserção de dados em branco. Ex: "", " " ou "      "
    # Similar ao trim de outras linguagens
    nome = nome.strip()
    if 'nome' in request.POST:
        if nome != '':
            nova_origem.nome = nome
            try:
                nova_origem.save()
                messages.success(request, f"Origem {nova_origem} cadastrada \
                                com sucesso!")
            except IntegrityError:
                messages.error(request, f"A Origem {nova_origem} já existe!")
        else:
            messages.error(request, "Informe uma descrição válida!")
    origens = Origem.objects.all().order_by('nome')
    origs = Services.paginacao(request, origens)
    return render(request, 'financeiro/origens.html', {"origens": origs})


def update_get_origem(request, id):
    origem = Origem.objects.get(id=id)
    return render(request, 'financeiro/editar_origem.html',
                  {"origem": origem})


def update_origem(request, id):
    origem = Origem.objects.get(id=id)
    nome = str(request.POST['nome'])
    nome = nome.strip()
    if 'nome' in request.POST:
        if nome != '':
            origem.nome = nome
            try:
                origem.save()
                messages.success(request, "Origem alterada  com sucesso!")
            except IntegrityError:
                messages.error(request, f"A Origem {origem} já existe! \
                               Alteração não realizada!")
        else:
            messages.error(request, "Informe uma descrição válida! \
                                    Alteração não realizada!")
    return redirect(reverse('rel_origens'))


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
    nome = str(request.POST.get('nome'))
    inc = None
    ant = None
    prox = None
    page = None
    if 'inc' in request.GET:
        inc = int(request.GET.get('inc'))
        ant = int(request.GET.get('ant'))
        prox = int(request.GET.get('prox'))
        page = request.GET.get('page')
        page = page + "0"
        page = int(page)
        page = page - 10
        
    # Impede a inserção de dados em branco. Ex: "", " " ou "      "
    # Similar ao trim de outras linguagens
    nome = nome.strip()
    if 'nome' in request.POST:
        if nome != '':
            nova_categoria.nome = nome
            try:
                nova_categoria.save()
                messages.success(request, f"Categoria {nova_categoria} cadastrada \
                                com sucesso!")
            except IntegrityError:
                messages.error(request, f"A Categoria {nova_categoria} já existe!")
        else:
            messages.error(request, "Informe uma descrição válida!")
    categorias = Categoria.objects.all().order_by('nome')
    cats = Services.paginacao(request, categorias)
    return render(request, 'financeiro/categorias.html',
                  {'cats': cats,
                   'inc': inc,
                   'ant': ant,
                   'prox': prox,
                   'page': page})


def update_get_categoria(request, id):
    categoria = Categoria.objects.get(id=id)
    return render(request, 'financeiro/editar_categoria.html',
                  {"categoria": categoria})


def update_categoria(request, id):
    categoria = Categoria.objects.get(id=id)
    nome = str(request.POST['nome'])
    nome = nome.strip()
    if 'nome' in request.POST:
        if nome != '':
            categoria.nome = nome
            try:
                categoria.save()
                messages.success(request, "Categoria alterada com sucesso!")
            except IntegrityError:
                messages.error(request, f"A Categoria {categoria} já existe! \
                               Alteração não realizada!")
        else:
            messages.error(request, "Informe uma descrição válida! \
                                    Alteração não realizada!")
    return redirect(reverse('rel_categorias'))


def delete_categoria(request, id):
    categoria = get_object_or_404(Categoria, id=id)
    # Verificar se existem lançamentos associados a esta categoria
    if categoria.lancamento_set.exists():
        messages.error(request, "Impossível excluir esta categoria. "
                                "Existem lançamentos associados.")
    else:
        categoria.delete()
        messages.success(request, "Categoria excluída com sucesso.")

    return redirect(reverse('rel_categorias'))


def rel_orcado_realizado(request):
    categorias = Categoria.objects.all().order_by('nome')
    get_dt_ini = request.GET.get('data-inicio')
    get_dt_fim = request.GET.get('data-fim')
    get_cat = request.GET.get('categoria')
    imprimir = False
    sem_resultados = False
    diferenca = None
    cat = -1
    difs = None
     
    if get_dt_ini and get_dt_fim and get_cat:
        data1 = datetime.strptime(get_dt_ini, '%Y-%m-%d')
        data2 = datetime.strptime(get_dt_fim, '%Y-%m-%d')
        if data1 > data2:
            messages.error(request, "Data inicial deve ser menor que a data final")
            return redirect(reverse('rel_orcado_realizado'))
        try:
            cat = int(get_cat)
            cat_str = str(cat)
            if get_cat == '-1':
                diferenca = Services.calcular_saldo_orc_realizado(get_dt_ini, get_dt_fim, None)
            else:
                diferenca = Services.calcular_saldo_orc_realizado(get_dt_ini, get_dt_fim, cat_str)           
            imprimir = True
            sem_resultados = True if len(diferenca) == 0 else False
        except TypeError as e:
            messages.error(request, f"Preencha o formulário corretamente. Tipo de exceção: {e}")
            return redirect(reverse('rel_orcado_realizado'))
        difs = Services.paginacao(request, diferenca)
    return render(request, 'financeiro/orcado-realizado.html', {
                                'categorias': categorias,
                                'cat': cat,
                                'diferenca': difs,
                                'dtini': get_dt_ini,
                                'dtfim': get_dt_fim,
                                'imprimir': imprimir,
                                'sem_resultados': sem_resultados
                                })
