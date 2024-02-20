import requests


class CotacaoDolarMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        url = 'https://economia.awesomeapi.com.br/json/last/USD-BRL'
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            cotacao_dolar = data['USDBRL']['bid']
        else:
            cotacao_dolar = None
        request.cotacao_dolar = cotacao_dolar
        response = self.get_response(request)
        return response
