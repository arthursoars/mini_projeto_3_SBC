from pathlib import Path

from rdflib import Graph, Namespace
from rdflib.namespace import RDF, RDFS, OWL


# ============================================================
# 1. CARREGAR A ONTOLOGIA
# ============================================================

PASTA = Path(__file__).resolve().parent
ARQUIVO_TTL = PASTA / "folclore_paraibano.ttl"

if not ARQUIVO_TTL.exists():
    raise FileNotFoundError(
        "Arquivo folclore_paraibano.ttl não encontrado."
    )

g = Graph()
g.parse(ARQUIVO_TTL, format="turtle")

EX = Namespace(
    "https://w3id.org/folclore-paraibano/ontology#"
)

print("=" * 60)
print("ONTOLOGIA CARREGADA")
print("=" * 60)

print(f"Total de triplas: {len(g)}")


# ============================================================
# 2. VALIDAÇÃO DA ESTRUTURA
# ============================================================

print("\n" + "=" * 60)
print("VALIDAÇÃO DA ESTRUTURA")
print("=" * 60)

total_classes = len(
    list(g.triples((None, RDF.type, OWL.Class)))
)

total_object_properties = len(
    list(g.triples((None, RDF.type, OWL.ObjectProperty)))
)

total_datatype_properties = len(
    list(g.triples((None, RDF.type, OWL.DatatypeProperty)))
)

total_entidades = len(
    list(g.triples((None, EX.possuiSlug, None)))
)

total_variacoes = len(
    list(g.triples((None, RDF.type, EX.Variacao)))
)

total_fontes = len(
    list(g.triples((None, RDF.type, EX.Fonte)))
)

total_citacoes = len(
    list(g.triples((None, RDF.type, EX.Citacao)))
)

total_relacoes = len(
    list(g.triples((None, RDF.type, EX.RelacaoEntreEntidades)))
)

print(f"Classes: {total_classes}")
print(f"ObjectProperties: {total_object_properties}")
print(f"DatatypeProperties: {total_datatype_properties}")
print(f"Entidades com slug: {total_entidades}")
print(f"Variações: {total_variacoes}")
print(f"Fontes: {total_fontes}")
print(f"Citações: {total_citacoes}")
print(f"Relações registradas: {total_relacoes}")


# Verificar se todas as propriedades têm domínio e alcance.

propriedades = list(
    g.subjects(RDF.type, OWL.ObjectProperty)
)

propriedades += list(
    g.subjects(RDF.type, OWL.DatatypeProperty)
)

propriedades_sem_dominio = []
propriedades_sem_alcance = []

for propriedade in propriedades:

    if not list(g.objects(propriedade, RDFS.domain)):
        propriedades_sem_dominio.append(propriedade)

    if not list(g.objects(propriedade, RDFS.range)):
        propriedades_sem_alcance.append(propriedade)

print("\nVerificação de domínio e alcance:")

print(
    "Propriedades sem domínio:",
    len(propriedades_sem_dominio)
)

print(
    "Propriedades sem alcance:",
    len(propriedades_sem_alcance)
)


# Verificar construções OWL.

print("\nConstruções OWL:")

print(
    "FunctionalProperty:",
    len(list(g.triples((None, RDF.type, OWL.FunctionalProperty))))
)

print(
    "Relações inverseOf:",
    len(list(g.triples((None, OWL.inverseOf, None))))
)

print(
    "AllDisjointClasses:",
    len(list(g.triples((None, RDF.type, OWL.AllDisjointClasses)))
    )
)

print(
    "hasKey:",
    len(list(g.triples((None, OWL.hasKey, None)))
    )
)


# ============================================================
# 3. FUNÇÃO AUXILIAR PARA MOSTRAR NOMES
# ============================================================

def obter_nome(individuo):

    nomes = list(
        g.objects(individuo, EX.possuiNome)
    )

    if nomes:
        return str(nomes[0])

    etiquetas = list(
        g.objects(individuo, RDFS.label)
    )

    if etiquetas:
        return str(etiquetas[0])

    return str(individuo).split("#")[-1]


def obter_literal(sujeito, propriedade):

    valores = list(
        g.objects(sujeito, propriedade)
    )

    if valores:
        return str(valores[0])

    return "Não informado"


# ============================================================
# 4. CONSULTA 1 - ENCONTRAR ENTIDADES FOLCLÓRICAS
# ============================================================

print("\n" + "=" * 60)
print("CONSULTA 1 - ENTIDADES FOLCLÓRICAS")
print("=" * 60)

classes_entidade = [
    EX.EntidadeFolclorica,
    EX.Assombracao,
    EX.Encantado,
    EX.Guardiao,
    EX.Metamorfo,
    EX.Maldicao,
    EX.Origem
]

entidades_encontradas = set()

for classe in classes_entidade:

    resultados = g.triples(
        (None, RDF.type, classe)
    )

    for sujeito, predicado, objeto in resultados:
        entidades_encontradas.add(sujeito)

for entidade in sorted(entidades_encontradas, key=str):

    print(
        "-", obter_nome(entidade)
    )

print(
    f"\nTotal encontrado: {len(entidades_encontradas)}"
)


# ============================================================
# 5. CONSULTA 2 - ENTIDADES ASSOCIADAS À PARAÍBA
# ============================================================

print("\n" + "=" * 60)
print("CONSULTA 2 - ENTIDADES ASSOCIADAS À PARAÍBA")
print("=" * 60)

resultados = g.triples(
    (None, EX.possuiEstado, EX.Estado_pb)
)

for sujeito, predicado, objeto in resultados:

    print(
        "-",
        obter_nome(sujeito)
    )


# ============================================================
# 6. CONSULTA 3 - ENTIDADES ASSOCIADAS À CAATINGA
# ============================================================

print("\n" + "=" * 60)
print("CONSULTA 3 - ENTIDADES ASSOCIADAS À CAATINGA")
print("=" * 60)

resultados = g.triples(
    (None, EX.associadaABioma, EX.Bioma_caatinga)
)

for sujeito, predicado, objeto in resultados:

    print(
        "-",
        obter_nome(sujeito)
    )


# ============================================================
# 7. CONSULTA 4 - RELAÇÕES DO TIPO RIVAL
# ============================================================

print("\n" + "=" * 60)
print("CONSULTA 4 - RELAÇÕES DO TIPO RIVAL")
print("=" * 60)

relacoes_rivais = g.triples(
    (None, EX.tipoRelacao, None)
)

for relacao, predicado, tipo in relacoes_rivais:

    if str(tipo) == "rival":

        origens = list(
            g.objects(relacao, EX.entidadeOrigem)
        )

        destinos = list(
            g.objects(relacao, EX.entidadeDestino)
        )

        motivo = obter_literal(
            relacao,
            EX.motivoRelacao
        )

        if origens and destinos:

            print(
                f"Origem: {obter_nome(origens[0])}"
            )

            print(
                f"Destino: {obter_nome(destinos[0])}"
            )

            print(
                f"Motivo: {motivo}"
            )

            print("-" * 40)


# ============================================================
# 8. CONSULTA 5 - CITAÇÕES E AUTORES
# ============================================================

print("\n" + "=" * 60)
print("CONSULTA 5 - CITAÇÕES E AUTORES")
print("=" * 60)

citacoes = g.triples(
    (None, RDF.type, EX.Citacao)
)

for citacao, predicado, objeto in citacoes:

    autor = obter_literal(
        citacao,
        EX.possuiAutorCitacao
    )

    obra = obter_literal(
        citacao,
        EX.possuiObraCitacao
    )

    texto = obter_literal(
        citacao,
        EX.possuiTextoCitacao
    )

    print(f"Autor: {autor}")
    print(f"Obra: {obra}")
    print(f"Citação: {texto}")
    print("-" * 40)


# ============================================================
# 9. FINALIZAÇÃO
# ============================================================

print("\n" + "=" * 60)
print("CONSULTAS FINALIZADAS")
print("=" * 60)