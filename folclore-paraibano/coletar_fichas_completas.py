
import requests
import json
import time

# Endereço da API
URL = "https://encantariadigital.com.br/api/v1/lendas"

# Arquivos utilizados
ARQUIVO_ENTRADA = "entidades_paraiba_resumo.json"
ARQUIVO_SAIDA = "entidades_paraiba_completo.json"
ARQUIVO_FALHAS = "falhas_coleta.json"


# Função para consultar uma ficha completa
def consultar_ficha(slug, tentativas=5):

    for tentativa in range(1, tentativas + 1):

        resposta = requests.get(
            f"{URL}/{slug}",
            params={"lang": "pt-br"},
            timeout=30
        )

        # Verificar se a API limitou as requisições
        if resposta.status_code == 429:

            if tentativa == tentativas:
                resposta.raise_for_status()

            # Tentar respeitar o tempo indicado pela API
            tempo = resposta.headers.get("Retry-After")

            try:
                espera = float(tempo) if tempo else 5 * tentativa
            except ValueError:
                espera = 5 * tentativa

            print(
                f"Limite da API atingido. "
                f"Aguardando {espera} segundos..."
            )

            time.sleep(espera)
            continue

        resposta.raise_for_status()

        dados = resposta.json()
        ficha = dados.get("data", dados)

        if not isinstance(ficha, dict):
            raise ValueError("Formato inesperado na resposta da API")

        return ficha


# 1. Carregar as entidades resumidas
with open(ARQUIVO_ENTRADA, "r", encoding="utf-8") as arquivo:
    entidades = json.load(arquivo)


# 2. Carregar fichas completas já coletadas
try:
    with open(ARQUIVO_SAIDA, "r", encoding="utf-8") as arquivo:
        fichas_completas = json.load(arquivo)

except FileNotFoundError:
    fichas_completas = []


# 3. Identificar os slugs já coletados
slugs_coletados = {
    ficha.get("slug")
    for ficha in fichas_completas
}

print("=== INÍCIO DA COLETA ===")
print(f"Entidades previstas: {len(entidades)}")
print(f"Fichas já coletadas: {len(fichas_completas)}")


# 4. Lista para registrar possíveis erros
falhas = []


# 5. Consultar somente as entidades que faltam
for indice, entidade in enumerate(entidades, start=1):

    slug = entidade.get("slug")

    if not slug:
        print(f"[{indice}/{len(entidades)}] Entidade sem slug.")

        falhas.append({
            "nome": entidade.get("nome"),
            "erro": "Slug não encontrado"
        })

        continue

    # Pular entidades que já foram coletadas
    if slug in slugs_coletados:

        print(
            f"[{indice}/{len(entidades)}] "
            f"{entidade.get('nome')} - Já coletada"
        )

        continue

    try:
        ficha = consultar_ficha(slug)

        # Garantir que a ficha tenha o slug correspondente
        ficha.setdefault("slug", slug)

        fichas_completas.append(ficha)
        slugs_coletados.add(slug)

        # Salvar o progresso após cada sucesso
        with open(ARQUIVO_SAIDA, "w", encoding="utf-8") as arquivo:
            json.dump(
                fichas_completas,
                arquivo,
                ensure_ascii=False,
                indent=4
            )

        print(
            f"[{indice}/{len(entidades)}] "
            f"{entidade.get('nome')} - Coletada"
        )

    except (requests.RequestException, ValueError) as erro:

        print(
            f"[{indice}/{len(entidades)}] "
            f"{slug} - ERRO: {erro}"
        )

        falhas.append({
            "slug": slug,
            "nome": entidade.get("nome"),
            "erro": str(erro)
        })

    # Pausa entre as consultas
    time.sleep(2)


# 6. Salvar possíveis falhas
if falhas:

    with open(ARQUIVO_FALHAS, "w", encoding="utf-8") as arquivo:

        json.dump(
            falhas,
            arquivo,
            ensure_ascii=False,
            indent=4
        )


# 7. Resultado final
print("\n=== RESULTADO DA COLETA ===")
print(f"Entidades previstas: {len(entidades)}")
print(f"Fichas coletadas: {len(fichas_completas)}")
print(f"Fichas faltantes: {len(entidades) - len(slugs_coletados)}")
print(f"Falhas nesta execução: {len(falhas)}")

print(f"\nArquivo salvo: {ARQUIVO_SAIDA}")

if falhas:
    print(f"Arquivo de erros: {ARQUIVO_FALHAS}")
