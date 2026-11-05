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

print(
    "Restrições de cardinalidade:",
    len(list(g.triples((None, OWL.cardinality, None))))
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
# ------------------------------------------------------------
# Padrão: (None, rdf:type, classe) -> objeto fixo, o resto livre,
#         repetido para cada subclasse de EntidadeFolclorica.
# Busca: todos os indivíduos que são de alguma das 6 subclasses
#        de classificação (Assombração, Encantado, Guardião...).
# Resultado esperado: as 32 entidades principais, em ordem
#        alfabética pelo identificador. As 46 referências externas
#        não aparecem, pois só têm o tipo EntidadeFolclorica.
# ============================================================

print("\n" + "=" * 60)
print("CONSULTA 1 - ENTIDADES FOLCLÓRICAS")
print("=" * 60)

# EntidadeFolclorica fica de fora de propósito: as 46 referências
# externas só têm esse tipo genérico, e aqui listamos as 32 fichas
# completas, que têm uma das subclasses abaixo.
classes_entidade = [
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
# ------------------------------------------------------------
# Padrão: (None, ex:possuiEstado, ex:Estado_pb) -> predicado e
#         objeto fixos; o sujeito é a incógnita.
# Busca: quem possui o estado Paraíba.
# Resultado esperado: 32 entidades (todas as fichas coletadas,
#        pois a coleta filtrou justamente por PB).
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
# ------------------------------------------------------------
# Padrão: (None, ex:associadaABioma, ex:Bioma_caatinga) ->
#         predicado e objeto fixos.
# Busca: entidades ligadas ao bioma Caatinga.
# Resultado esperado: 21 entidades (um subconjunto das 32).
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
# ------------------------------------------------------------
# Padrão: (None, ex:tipoRelacao, None) -> só o predicado fixo;
#         depois, para cada relação "rival", dois padrões com
#         sujeito e predicado fixos: (relacao, entidadeOrigem, None)
#         e (relacao, entidadeDestino, None).
# Busca: relações cujo tipo é "rival", com origem, destino e motivo.
# Resultado esperado: 8 relações, cada uma com origem, destino e
#        o motivo registrado pela API.
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
# ------------------------------------------------------------
# Padrão: (None, rdf:type, ex:Citacao) -> objeto fixo; depois,
#         para cada citação, padrões com sujeito e predicado
#         fixos (autor, obra e texto).
# Busca: todas as citações com autor, obra e texto.
# Resultado esperado: 49 citações. Campos ausentes aparecem
#        como "Não informado".
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
# 9. CONSULTA 6 - TUDO SOBRE UMA ENTIDADE (SUJEITO FIXO)
# ------------------------------------------------------------
# Padrão: (ex:mula-sem-cabeca, None, None) -> só o sujeito fixo;
#         predicado e objeto são as incógnitas.
# Busca: todas as informações registradas sobre a Mula Sem Cabeça.
# Resultado esperado: uma lista de pares propriedade -> valor
#        (nome, classificação, nível de ameaça, estados, biomas,
#        fontes etc.). Textos longos são cortados em 70 caracteres.
# ============================================================

print("\n" + "=" * 60)
print("CONSULTA 6 - TUDO SOBRE A MULA SEM CABEÇA")
print("=" * 60)

mula = EX["mula-sem-cabeca"]

for sujeito, predicado, objeto in sorted(
    g.triples((mula, None, None)),
    key=lambda tripla: (str(tripla[1]), str(tripla[2]))
):
    propriedade = str(predicado).split("#")[-1]
    valor = str(objeto).split("#")[-1].replace("\n", " ")

    if len(valor) > 70:
        valor = valor[:70] + "..."

    print(f"{propriedade}: {valor}")


# ============================================================
# 10. CONSULTA 7 - QUEM APONTA PARA A CAATINGA (OBJETO FIXO)
# ------------------------------------------------------------
# Padrão: (None, None, ex:Bioma_caatinga) -> só o objeto fixo;
#         sujeito e predicado são as incógnitas.
# Busca: qualquer entidade ligada à Caatinga, por qualquer
#        propriedade (bioma e bioma principal).
# Resultado esperado: 36 ligações, sendo 21 por associadaABioma e
#        15 por associadaABiomaPrincipal. Mostra a contagem por
#        propriedade e não repete as 36 linhas.
# ============================================================

print("\n" + "=" * 60)
print("CONSULTA 7 - QUEM APONTA PARA A CAATINGA?")
print("=" * 60)

contagem_por_propriedade = {}

for sujeito, predicado, objeto in g.triples(
    (None, None, EX.Bioma_caatinga)
):
    propriedade = str(predicado).split("#")[-1]
    contagem_por_propriedade[propriedade] = (
        contagem_por_propriedade.get(propriedade, 0) + 1
    )

for propriedade, total in sorted(contagem_por_propriedade.items()):
    print(f"{propriedade}: {total}")


# ============================================================
# 11. FINALIZAÇÃO
# ============================================================

print("\n" + "=" * 60)
print("CONSULTAS FINALIZADAS")
print("=" * 60)