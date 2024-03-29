from django.db import connection
from django.db.models import Sum, F, Case, When, DecimalField
from django.db.models.functions import TruncMonth
from financeiro.models import Lancamento, Orcamento, Categoria
from django.core.paginator import Paginator, InvalidPage, EmptyPage
import requests


class Services:

    def calcular_diferencaSQL():
        query = """
        SELECT origem_id, financeiro_origem.nome,
        SUM(CASE WHEN tipo_operacao='e'
        THEN valor ELSE -valor END) AS diferenca
        FROM financeiro_lancamento
        INNER JOIN financeiro_origem ON
        financeiro_lancamento.origem_id = financeiro_origem.id
        GROUP BY origem_id, financeiro_origem.nome
        """
        with connection.cursor() as cursor:
            cursor.execute(query)
            columns = [col[0] for col in cursor.description]
            diferenca = [dict(zip(columns, row)) for row in cursor.fetchall()]
        return diferenca

    def calcular_diferencaORM():
        diferenca = (
            Lancamento.objects
            .values('origem__nome')
            .annotate(diferenca=Sum(
                Case(
                    When(tipo_operacao='e', then=F('valor')),
                    default=-F('valor'),
                    output_field=DecimalField()
                    ))
                )
            )
        return diferenca

    def calcular_saldo_orc_realizado(data_ini, data_fim, categoria=None):

        # Filtrar por categoria, se fornecida
        orcamentos = Orcamento.objects.filter(data__range=(data_ini, data_fim))
        lancamentos = Lancamento.objects.filter(data__range=(data_ini, data_fim))
        if categoria:
            orcamentos = orcamentos.filter(categoria=categoria)
            lancamentos = lancamentos.filter(categoria=categoria)
                  
        # Agrupando os valores orçados por categoria e mês
        # ********* Alterado aqui *******
        orcamentos = orcamentos.annotate(
            mes=TruncMonth('data')
        ).values(
            'mes', 'categoria'
        ).annotate(
            valor_orcado=Sum('valor')
        )

        # Agrupando os valores lançados por categoria e mês
        # ********* Alterado aqui *******
        lancamentos = lancamentos.annotate(
            mes=TruncMonth('data')
        ).values(
            'mes', 'categoria'
        ).annotate(
            valor_realizado=Sum('valor')
        )

        # Juntando os dados dos orçamentos e lançamentos
        relatorio = []
        for orcamento in orcamentos:
            mes = orcamento['mes']
            categoria = orcamento['categoria']
            valor_orcado = orcamento['valor_orcado']
            valor_realizado = next((l['valor_realizado'] for l in lancamentos if l['mes'] == mes and l['categoria'] == categoria), 0)
            saldo = valor_orcado - valor_realizado
            relatorio.append({
                'mes': mes.strftime('%m/%Y'),
                'categoria': Categoria.objects.get(pk=categoria).nome,
                'valor_orcado': valor_orcado,
                'valor_realizado': valor_realizado,
                'saldo': saldo
                })

        return relatorio

    def paginacao(request, registros):
        # Paginação
        paginator = Paginator(registros, 10)
        try:
            page = int(request.GET.get('page', '1'))
        except ValueError:
            page = 1

        # Se o page request (9999) está fora da lista, mostre a última página.
        try:
            regs = paginator.page(page)
        except (EmptyPage, InvalidPage):
            regs = paginator.page(paginator.num_pages)
        return regs
    
    def registro_por_linha(request):
        reg_por_linha = None

        if 'page' in request.GET:
            reg_por_linha = request.GET.get('page')
            reg_por_linha = reg_por_linha + "0"
            reg_por_linha = int(reg_por_linha)
            reg_por_linha = reg_por_linha - 10
        
        return reg_por_linha
