from django.db import models


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
