
import requests

BASE_URL = "https://encantariadigital.com.br/api/v1"

# Três testes independentes
testes = [
    {
        "nome": "A - Listagem sem filtro",
        "url": f"{BASE_URL}/lendas",
        "params": {
            "perPage": 3,
            "lang": "pt-br"
        }
    },
    {
        "nome": "B - Listagem com filtro Nordeste",
        "url": f"{BASE_URL}/lendas",
        "params": {
            "regiao": "nordeste",
            "perPage": 3,
            "lang": "pt-br"
        }
    },
    {
        "nome": "C - Facetas",
        "url": f"{BASE_URL}/facetas",
        "params": {
            "lang": "pt-br"
        }
    }
]

for teste in testes:

    print("\n" + "=" * 55)
    print(teste["nome"])
    print("=" * 55)

    try:
        resposta = requests.get(
            teste["url"],
            params=teste["params"],
            timeout=30
        )

        print("URL solicitada:", resposta.url)
        print("Status HTTP:", resposta.status_code)
        print("Content-Type:", resposta.headers.get("Content-Type"))

        resposta.raise_for_status()

        dados = resposta.json()

        print("\nStatus da API:", dados.get("status"))

        meta = dados.get("meta", {})
        print("Metadados:", meta)

        registros = dados.get("data")

        if isinstance(registros, list):
            print("Quantidade retornada:", len(registros))

            for item in registros[:3]:
                print(
                    "Nome:", item.get("nome"),
                    "| Estados:", item.get("estados")
                )

        elif isinstance(registros, dict):
            print("Campos retornados:", list(registros.keys()))

        else:
            print("Formato de data:", type(registros).__name__)

    except requests.exceptions.RequestException as erro:
        print("Erro na requisição:", erro)

    except ValueError:
        print("A resposta não é um JSON válido.")
        print(resposta.text[:500])
