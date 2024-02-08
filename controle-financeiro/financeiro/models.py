from django.db import models
from django.db import connection
from django.db.models import Sum, F, Case, When


# Create your models here.
class Origem(models.Model):
    nome = models.CharField(max_length=255)

    def __str__(self):
        return self.nome


class Categoria(models.Model):
    nome = models.CharField(max_length=255)

    def __str__(self):
        return self.nome


class Orcamento(models.Model):
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    data = models.DateField()
    valor = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.nome


class Lancamento(models.Model):
    ENTRADA = 'e'
    SAIDA = 's'
    TIPO_OPERACAO_CHOICES = [(ENTRADA, 'Entrada'), (SAIDA, 'Saída'),]
    data = models.DateField()
    descricao = models.CharField(max_length=255)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    origem = models.ForeignKey(Origem, on_delete=models.CASCADE)
    tipo_operacao = models.CharField(max_length=1,
                                     choices=TIPO_OPERACAO_CHOICES)

    def __str__(self):
        return f"{self.data} | {self.descricao} | {self.valor} |" \
            f"{self.categoria} | {self.origem} | {self.tipo_operacao}"

    @staticmethod
    def calcular_diferenca1SQL():
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
            resultado = [dict(zip(columns, row)) for row in cursor.fetchall()]
        return resultado

    @staticmethod
    def calcular_diferencaORM():
        diferenca = (
            Lancamento.objects
            .values('origem__nome')
            .annotate(diferenca=Sum(
                Case(
                    When(tipo_operacao='e', then=F('valor')),
                    default=-F('valor'))))
        )
        return diferenca
