from django.db import connection
from django.db.models import Sum, F, Case, When, DecimalField
from django.db.models.functions import Concat, Extract
from financeiro.models import Lancamento, Orcamento


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
    
    def calcular_diferenca_orcamento():
        diferenca = (
            Orcamento.objects
            .annotate(mes=Concat(Extract('data_orcamento', 'month'), '/', Extract('data_orcamento', 'year')))
            .values('mes', 'categoria__nome')
            .annotate(
                valor_orcado=Sum('valor'),
                valor_realizado=Sum('lancamento__valor'),
                saldo=F('valor_orcado') - F('valor_realizado')
            )
        )
        return diferenca
