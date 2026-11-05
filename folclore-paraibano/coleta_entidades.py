
import requests
import json

# Endereço da API
URL = "https://encantariadigital.com.br/api/v1/lendas"

# Parâmetros da consulta
parametros = {
    "perPage": 100,
    "lang": "pt-br"
}

# Lista das entidades associadas à Paraíba
entidades_paraiba = []

# 1. Consultar a primeira página para descobrir a paginação
resposta = requests.get(
    URL,
    params={**parametros, "page": 1},
    timeout=30
)

resposta.raise_for_status()
dados = resposta.json()

total_entidades = dados["meta"]["total"]
total_paginas = dados["meta"]["pages"]

print("=== INFORMAÇÕES DA API ===")
print(f"Total de entidades: {total_entidades}")
print(f"Total de páginas: {total_paginas}")

# 2. Percorrer todas as páginas
for pagina in range(1, total_paginas + 1):

    # Reutilizar a primeira resposta, evitando uma requisição repetida
    if pagina == 1:
        dados_pagina = dados

    else:
        resposta = requests.get(
            URL,
            params={**parametros, "page": pagina},
            timeout=30
        )

        resposta.raise_for_status()
        dados_pagina = resposta.json()

    entidades = dados_pagina["data"]

    # 3. Filtrar entidades associadas à Paraíba
    for entidade in entidades:

        estados = entidade.get("estados", [])

        if "PB" in estados:
            entidades_paraiba.append(entidade)

    print(f"Página {pagina}/{total_paginas} concluída.")

# 4. Salvar os registros em JSON
with open(
    "entidades_paraiba_resumo.json",
    "w",
    encoding="utf-8"
) as arquivo:

    json.dump(
        entidades_paraiba,
        arquivo,
        ensure_ascii=False,
        indent=4
    )

# 5. Exibir o resultado
print("\n=== RESULTADO DA COLETA ===")
print(f"Total consultado: {total_entidades}")
print(f"Entidades associadas à PB: {len(entidades_paraiba)}")

print("\n=== ENTIDADES ENCONTRADAS ===")

for entidade in entidades_paraiba:
    print(
        f"{entidade['nome']} | "
        f"Slug: {entidade['slug']} | "
        f"Estados: {entidade.get('estados', [])}"
    )

print("\nArquivo salvo: entidades_paraiba_resumo.json")
