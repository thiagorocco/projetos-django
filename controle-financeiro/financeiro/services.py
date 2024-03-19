from django.db import connection
from django.db.models import Sum, F, Case, When, DecimalField
from django.db.models.functions import TruncMonth
from itertools import groupby
from financeiro.models import Lancamento, Orcamento, Categoria
from operator import itemgetter


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

    def calcular_saldo_orc_realizado(request):
        lancamentos = Lancamento.objects.annotate(mes=TruncMonth('data')).values('mes', 'categoria').annotate(total_lancado=Sum('valor'))
        orcamentos = Orcamento.objects.annotate(mes=TruncMonth('data')).values('mes', 'categoria').annotate(total_orcado=Sum('valor'))

        relatorio = []
        for key, group in groupby(sorted(list(lancamentos) + list(orcamentos), key=itemgetter('mes', 'categoria')), key=itemgetter('mes', 'categoria')):
            mes, categoria = key
            total_lancado = sum(item['total_lancado'] if item['total_lancado'] else 0 for item in group if item['mes'] == mes and item['categoria'] == categoria)
            total_orcado = sum(item['total_orcado'] if item['total_orcado'] else 0 for item in group if item['mes'] == mes and item['categoria'] == categoria)
            saldo = total_orcado - total_lancado
            relatorio.append({
                'mes': mes.strftime('%m/%Y'),
                'categoria': Categoria.objects.get(pk=categoria).nome,
                'valor_orcado': total_orcado,
                'valor_lancado': total_lancado,
                'saldo': saldo
            })

        return relatorio