from pathlib import Path
from rdflib import Graph, Namespace

# ============================================================
# 1. CARREGAR A ONTOLOGIA
# ============================================================

PASTA = Path(__file__).resolve().parent
ARQUIVO_TTL = PASTA / "folclore_paraibano.ttl"

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
# 2. FUNÇÃO PARA EXECUTAR E EXIBIR CONSULTAS
# ============================================================

def executar_consulta(titulo, consulta):

    print("\n" + "=" * 60)
    print(titulo)
    print("=" * 60)

    resultados = g.query(consulta)

    for resultado in resultados:
        valores = [
            str(valor) if valor is not None else "Não informado"
            for valor in resultado
        ]

        print(" | ".join(valores))


# ============================================================
# 3. CONSULTA 1 - ENTIDADES E CLASSIFICAÇÕES
# ============================================================

consulta_1 = """
PREFIX ex: <https://w3id.org/folclore-paraibano/ontology#>

SELECT ?nome ?classificacao
WHERE {
    ?entidade ex:possuiNome ?nome .
    ?entidade ex:possuiClassificacaoOriginal ?classificacao .
}
ORDER BY ?nome
"""

executar_consulta(
    "CONSULTA 1 - ENTIDADES E CLASSIFICAÇÕES",
    consulta_1
)


# ============================================================
# 4. CONSULTA 2 - FILTRO POR NÍVEL DE AMEAÇA
# ============================================================

consulta_2 = """
PREFIX ex: <https://w3id.org/folclore-paraibano/ontology#>

SELECT ?nome ?ameaca
WHERE {
    ?entidade ex:possuiNome ?nome .
    ?entidade ex:possuiNivelAmeaca ?ameaca .

    FILTER(?ameaca = "baixo")
}
"""

executar_consulta(
    "CONSULTA 2 - ENTIDADES COM AMEAÇA BAIXA",
    consulta_2
)


# ============================================================
# 5. CONSULTA 3 - ORDEM ALFABÉTICA INVERSA
# ============================================================

consulta_3 = """
PREFIX ex: <https://w3id.org/folclore-paraibano/ontology#>

SELECT ?nome
WHERE {
    ?entidade ex:possuiNome ?nome .
    ?entidade ex:possuiClassificacaoOriginal ?classificacao .
}
ORDER BY DESC(?nome)
"""

executar_consulta(
    "CONSULTA 3 - ENTIDADES EM ORDEM DECRESCENTE",
    consulta_3
)


# ============================================================
# 6. CONSULTA 4 - CONTAGEM POR CLASSIFICAÇÃO
# ============================================================

consulta_4 = """
PREFIX ex: <https://w3id.org/folclore-paraibano/ontology#>

SELECT ?classificacao (COUNT(?entidade) AS ?quantidade)
WHERE {
    ?entidade ex:possuiClassificacaoOriginal ?classificacao .
}
GROUP BY ?classificacao
ORDER BY DESC(?quantidade)
"""

executar_consulta(
    "CONSULTA 4 - QUANTIDADE POR CLASSIFICAÇÃO",
    consulta_4
)
# ============================================================
# 7. CONSULTA 5 - ASK: VERIFICAR ASSOCIAÇÃO COM A PARAÍBA
# ============================================================

consulta_5 = """
PREFIX ex: <https://w3id.org/folclore-paraibano/ontology#>

ASK {
    ex:aipo-e-tambia ex:possuiEstado ex:Estado_pb .
}
"""

resultado_5 = g.query(consulta_5)

print("\n" + "=" * 60)
print("CONSULTA 5 - AIPÓ E TAMBIÁ ESTÁ ASSOCIADA À PARAÍBA?")
print("=" * 60)

print(bool(resultado_5))


# ============================================================
# 8. CONSULTA 6 - ASK: EXISTE ENTIDADE ASSOCIADA À CAATINGA?
# ============================================================

consulta_6 = """
PREFIX ex: <https://w3id.org/folclore-paraibano/ontology#>

ASK {
    ?entidade ex:associadaABioma ex:Bioma_caatinga .
}
"""

resultado_6 = g.query(consulta_6)

print("\n" + "=" * 60)
print("CONSULTA 6 - EXISTE ENTIDADE ASSOCIADA À CAATINGA?")
print("=" * 60)

print(bool(resultado_6))


# ============================================================
# 9. CONSULTA 7 - CONSTRUCT: CRIAR GRAFO REDUZIDO
# ============================================================

consulta_7 = """
PREFIX ex: <https://w3id.org/folclore-paraibano/ontology#>

CONSTRUCT {
    ?entidade ex:possuiNome ?nome .
    ?entidade ex:possuiEstado ex:Estado_pb .
}
WHERE {
    ?entidade ex:possuiNome ?nome .
    ?entidade ex:possuiEstado ex:Estado_pb .
}
"""

grafo_reduzido = g.query(consulta_7)

print("\n" + "=" * 60)
print("CONSULTA 7 - GRAFO REDUZIDO DAS ENTIDADES DA PARAÍBA")
print("=" * 60)

print(f"Total de triplas no novo grafo: {len(grafo_reduzido)}")

for sujeito, predicado, objeto in grafo_reduzido:
    print(sujeito, predicado, objeto)
# ============================================================
# 10. CONSULTA 8 - INSERT DATA: INSERIR DADOS TEMPORÁRIOS
# ============================================================

consulta_8 = """
PREFIX ex: <https://w3id.org/folclore-paraibano/ontology#>

INSERT DATA {
    ex:teste_sparql a ex:EntidadeFolclorica ;
        ex:possuiSlug "teste-sparql" ;
        ex:possuiConfianca "baixa" .
}
"""

g.update(consulta_8)

print("\n" + "=" * 60)
print("CONSULTA 8 - INSERT DATA")
print("=" * 60)

print("Indivíduo temporário inserido.")
print("Total de triplas após a inserção:", len(g))

for tripla in g.triples((EX.teste_sparql, None, None)):
    print(tripla)


# ============================================================
# 11. CONSULTA 9 - DELETE/INSERT WHERE: ALTERAR UM VALOR
# ============================================================

consulta_9 = """
PREFIX ex: <https://w3id.org/folclore-paraibano/ontology#>

DELETE {
    ex:teste_sparql ex:possuiConfianca ?confiancaAntiga .
}
INSERT {
    ex:teste_sparql ex:possuiConfianca "media" .
}
WHERE {
    ex:teste_sparql ex:possuiConfianca ?confiancaAntiga .
    FILTER(?confiancaAntiga = "baixa")
}
"""

g.update(consulta_9)

print("\n" + "=" * 60)
print("CONSULTA 9 - DELETE/INSERT WHERE")
print("=" * 60)

print("Confiança após atualização:")

for valor in g.objects(EX.teste_sparql, EX.possuiConfianca):
    print(valor)


# ============================================================
# 12. CONSULTA 10 - DELETE DATA: REMOVER DADOS TEMPORÁRIOS
# ============================================================

consulta_10 = """
PREFIX ex: <https://w3id.org/folclore-paraibano/ontology#>

DELETE DATA {
    ex:teste_sparql a ex:EntidadeFolclorica ;
        ex:possuiSlug "teste-sparql" ;
        ex:possuiConfianca "media" .
}
"""

g.update(consulta_10)

print("\n" + "=" * 60)
print("CONSULTA 10 - DELETE DATA")
print("=" * 60)

print("Triplas restantes do indivíduo temporário:")

for tripla in g.triples((EX.teste_sparql, None, None)):
    print(tripla)

print("Total de triplas após a remoção:", len(g))


# ============================================================
# 13. CONSULTA 11 - ASK: UMA PERGUNTA COM RESPOSTA FALSA
# ============================================================

consulta_11 = """
PREFIX ex: <https://w3id.org/folclore-paraibano/ontology#>

ASK {
    ex:aipo-e-tambia ex:possuiEstado ex:Estado_rs .
}
"""

resultado_11 = g.query(consulta_11)

print("\n" + "=" * 60)
print("CONSULTA 11 - AIPÓ E TAMBIÁ ESTÁ ASSOCIADA AO RIO GRANDE DO SUL?")
print("=" * 60)

print(bool(resultado_11))
# ============================================================
# FINALIZAÇÃO
# ============================================================

print("\n" + "=" * 60)
print("CONSULTAS SPARQL FINALIZADAS")
print("=" * 60)