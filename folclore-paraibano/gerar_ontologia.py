import json
import re
import unicodedata
from pathlib import Path

from rdflib import Graph, Namespace, URIRef, Literal, BNode
from rdflib.namespace import RDF, RDFS, OWL, XSD
from rdflib.collection import Collection

# ------------------------------------------------------------
# 1. Arquivos e namespaces
# ------------------------------------------------------------
PASTA = Path(__file__).resolve().parent
ARQUIVO_JSON = PASTA / "entidades_paraiba_completo.json"
ARQUIVO_TTL = PASTA / "folclore_paraibano.ttl"

EX = Namespace("https://w3id.org/folclore-paraibano/ontology#")

# ------------------------------------------------------------
# 2. Funções auxiliares
# ------------------------------------------------------------
def normalizar_id(valor):
    """Transforma um texto em identificador simples para URI."""
    texto = str(valor).strip().lower()
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    texto = re.sub(r"[^a-z0-9]+", "-", texto).strip("-")
    return texto or "sem-identificador"


def adicionar_literal(grafo, sujeito, propriedade, valor, tipo=XSD.string):
    """Adiciona literal somente quando o valor existe e não está vazio."""
    if valor is None or valor == "":
        return

    if tipo == XSD.boolean:
        literal = Literal(bool(valor), datatype=XSD.boolean)
    elif tipo == XSD.integer:
        literal = Literal(int(valor), datatype=XSD.integer)
    else:
        literal = Literal(str(valor), datatype=tipo)

    grafo.add((sujeito, propriedade, literal))


def obter_individuo(classe, identificador):
    return EX[f"{classe}_{normalizar_id(identificador)}"]


# ------------------------------------------------------------
# 3. Carregar os dados
# ------------------------------------------------------------
if not ARQUIVO_JSON.exists():
    raise FileNotFoundError(
        f"Não encontrei {ARQUIVO_JSON.name}. "
        "Coloque o JSON na mesma pasta deste script."
    )

with ARQUIVO_JSON.open("r", encoding="utf-8") as arquivo:
    entidades = json.load(arquivo)

if not isinstance(entidades, list):
    raise ValueError("O JSON deveria conter uma lista de entidades.")


# ------------------------------------------------------------
# 4. Criar o grafo e registrar namespaces
# ------------------------------------------------------------
g = Graph()

g.bind("ex", EX)
g.bind("rdf", RDF)
g.bind("rdfs", RDFS)
g.bind("owl", OWL)
g.bind("xsd", XSD)

# Cabeçalho da ontologia (owl:Ontology)
ontologia = URIRef("https://w3id.org/folclore-paraibano/ontology")

g.add((ontologia, RDF.type, OWL.Ontology))
g.add((
    ontologia,
    RDFS.label,
    Literal("Ontologia do Folclore Paraibano", lang="pt-br")
))
g.add((
    ontologia,
    RDFS.comment,
    Literal(
        "Ontologia sobre entidades do folclore associadas à Paraíba, "
        "construída a partir da API Encantaria Digital.",
        lang="pt-br"
    )
))
g.add((ontologia, OWL.versionInfo, Literal("1.0")))


# ------------------------------------------------------------
# 5. Declarar classes
# ------------------------------------------------------------
classes = [
    "RecursoFolclorico",
    "EntidadeFolclorica",
    "Assombracao",
    "Encantado",
    "Guardiao",
    "Metamorfo",
    "Maldicao",
    "Origem",
    "RecursoDocumental",
    "Fonte",
    "Citacao",
    "Estado",
    "Regiao",
    "Bioma",
    "MatrizCultural",
    "Povo",
    "Elemento",
    "Variacao",
    "RelacaoEntreEntidades"
]

for nome_classe in classes:
    g.add((EX[nome_classe], RDF.type, OWL.Class))
    g.add((
        EX[nome_classe],
        RDFS.label,
        Literal(nome_classe, lang="pt-br")
    ))

# Hierarquia principal
g.add((
    EX.EntidadeFolclorica,
    RDFS.subClassOf,
    EX.RecursoFolclorico
))

g.add((
    EX.RecursoDocumental,
    RDFS.subClassOf,
    EX.RecursoFolclorico
))

subclasses_classificacao = {
    "Assombração": EX.Assombracao,
    "Encantado": EX.Encantado,
    "Guardião": EX.Guardiao,
    "Metamorfo": EX.Metamorfo,
    "Maldição": EX.Maldicao,
    "Origem": EX.Origem,
}

for classe in subclasses_classificacao.values():
    g.add((
        classe,
        RDFS.subClassOf,
        EX.EntidadeFolclorica
    ))

g.add((EX.Fonte, RDFS.subClassOf, EX.RecursoDocumental))
g.add((EX.Citacao, RDFS.subClassOf, EX.RecursoDocumental))


# ------------------------------------------------------------
# 6. Declarar ObjectProperties com domain e range
# ------------------------------------------------------------
object_properties = {
    "possuiEstado": (EX.EntidadeFolclorica, EX.Estado),
    "associadaARegiao": (EX.EntidadeFolclorica, EX.Regiao),
    "associadaABioma": (EX.EntidadeFolclorica, EX.Bioma),
    "associadaARegiaoPrincipal": (EX.EntidadeFolclorica, EX.Regiao),
    "associadaABiomaPrincipal": (EX.EntidadeFolclorica, EX.Bioma),
    "possuiMatrizCultural": (EX.EntidadeFolclorica, EX.MatrizCultural),
    "associadaAoPovo": (EX.EntidadeFolclorica, EX.Povo),
    "possuiElemento": (EX.EntidadeFolclorica, EX.Elemento),
    "possuiVariacao": (EX.EntidadeFolclorica, EX.Variacao),
    "variaDe": (EX.Variacao, EX.EntidadeFolclorica),
    "possuiFonte": (EX.EntidadeFolclorica, EX.Fonte),
    "possuiCitacao": (EX.EntidadeFolclorica, EX.Citacao),
    "possuiRelacaoRegistrada": (
        EX.EntidadeFolclorica,
        EX.RelacaoEntreEntidades
    ),
    "entidadeOrigem": (
        EX.RelacaoEntreEntidades,
        EX.EntidadeFolclorica
    ),
    "entidadeDestino": (
        EX.RelacaoEntreEntidades,
        EX.EntidadeFolclorica
    ),
}

for nome, (dominio, alcance) in object_properties.items():
    prop = EX[nome]

    g.add((prop, RDF.type, OWL.ObjectProperty))
    g.add((prop, RDFS.domain, dominio))
    g.add((prop, RDFS.range, alcance))
    g.add((prop, RDFS.label, Literal(nome, lang="pt-br")))

# Propriedades inversas
g.add((EX.possuiVariacao, OWL.inverseOf, EX.variaDe))

g.add((
    EX.possuiRelacaoRegistrada,
    OWL.inverseOf,
    EX.entidadeOrigem
))


# ------------------------------------------------------------
# 7. Declarar DatatypeProperties com domain e range
# ------------------------------------------------------------
datatype_properties = {
    "possuiSlug": (EX.EntidadeFolclorica, XSD.string),
    "possuiNome": (EX.EntidadeFolclorica, XSD.string),
    "possuiDescricao": (EX.EntidadeFolclorica, XSD.string),
    "possuiTagline": (EX.EntidadeFolclorica, XSD.string),
    "possuiCausoCompleto": (EX.EntidadeFolclorica, XSD.string),
    "possuiClassificacaoOriginal": (EX.EntidadeFolclorica, XSD.string),
    "possuiNivelAmeaca": (EX.EntidadeFolclorica, XSD.string),
    "possuiRaridade": (EX.EntidadeFolclorica, XSD.string),
    "possuiConfianca": (EX.EntidadeFolclorica, XSD.string),
    "possuiOrigemIncerta": (EX.EntidadeFolclorica, XSD.boolean),
    "possuiCultoVivo": (EX.EntidadeFolclorica, XSD.string),
    "possuiRegistro": (EX.Variacao, XSD.string),
    "possuiNomeLocal": (EX.Variacao, XSD.string),
    "possuiLocalidade": (EX.Variacao, XSD.string),
    "possuiConfiancaVariacao": (EX.Variacao, XSD.string),
    "possuiTipoFonte": (EX.Fonte, XSD.string),
    "possuiReferenciaFonte": (EX.Fonte, XSD.string),
    "possuiLicencaFonte": (EX.Fonte, XSD.string),
    "possuiTextoCitacao": (EX.Citacao, XSD.string),
    "possuiAutorCitacao": (EX.Citacao, XSD.string),
    "possuiObraCitacao": (EX.Citacao, XSD.string),
    "possuiAnoCitacao": (EX.Citacao, XSD.integer),
    "tipoRelacao": (EX.RelacaoEntreEntidades, XSD.string),
    "motivoRelacao": (EX.RelacaoEntreEntidades, XSD.string),
}

for nome, (dominio, alcance) in datatype_properties.items():
    prop = EX[nome]

    g.add((prop, RDF.type, OWL.DatatypeProperty))
    g.add((prop, RDFS.domain, dominio))
    g.add((prop, RDFS.range, alcance))
    g.add((prop, RDFS.label, Literal(nome, lang="pt-br")))


# ------------------------------------------------------------
# 8. Construções OWL: funcionalidade, chave e disjunção
# ------------------------------------------------------------

# FunctionalProperty
g.add((EX.possuiSlug, RDF.type, OWL.FunctionalProperty))

# owl:hasKey: o slug é a chave de identificação das entidades.
lista_chaves = BNode()
Collection(g, lista_chaves, [EX.possuiSlug])

g.add((
    EX.EntidadeFolclorica,
    OWL.hasKey,
    lista_chaves
))

# As classificações são disjuntas dentro da taxonomia adotada pela fonte.
no_disjuncao = BNode()
g.add((
    no_disjuncao,
    RDF.type,
    OWL.AllDisjointClasses
))

lista_classes = BNode()
Collection(
    g,
    lista_classes,
    list(subclasses_classificacao.values())
)

g.add((
    no_disjuncao,
    OWL.members,
    lista_classes
))


# ------------------------------------------------------------
# 9. Criar indivíduos e relações a partir das 32 fichas
# ------------------------------------------------------------
individuos_entidade = {}

for entidade in entidades:
    slug = entidade.get("slug")

    if not slug:
        continue

    sujeito = EX[normalizar_id(slug)]
    individuos_entidade[slug] = sujeito

    classificacao = entidade.get("classification")

    classe = subclasses_classificacao.get(
        classificacao,
        EX.EntidadeFolclorica
    )

    g.add((sujeito, RDF.type, classe))

    g.add((
        sujeito,
        EX.possuiSlug,
        Literal(slug, datatype=XSD.string)
    ))

    texto = entidade.get("texto") or {}

    adicionar_literal(
        g, sujeito, EX.possuiNome,
        texto.get("nome")
    )

    adicionar_literal(
        g, sujeito, EX.possuiDescricao,
        texto.get("descricao_curta")
    )

    adicionar_literal(
        g, sujeito, EX.possuiTagline,
        texto.get("tagline")
    )

    adicionar_literal(
        g, sujeito, EX.possuiCausoCompleto,
        texto.get("causo_completo")
    )

    adicionar_literal(
        g, sujeito, EX.possuiClassificacaoOriginal,
        classificacao
    )

    adicionar_literal(
        g, sujeito, EX.possuiNivelAmeaca,
        entidade.get("threat_level")
    )

    adicionar_literal(
        g, sujeito, EX.possuiRaridade,
        entidade.get("rarity_tier")
    )

    adicionar_literal(
        g, sujeito, EX.possuiConfianca,
        entidade.get("confianca")
    )

    adicionar_literal(
        g, sujeito, EX.possuiOrigemIncerta,
        entidade.get("origem_incerta"),
        XSD.boolean
    )

    adicionar_literal(
        g, sujeito, EX.possuiCultoVivo,
        entidade.get("culto_vivo")
    )

    # Estados
    for sigla in entidade.get("estados") or []:
        estado = obter_individuo("Estado", sigla)

        g.add((estado, RDF.type, EX.Estado))
        g.add((
            estado,
            RDFS.label,
            Literal(sigla, lang="pt-br")
        ))

        g.add((sujeito, EX.possuiEstado, estado))

    # Regiões e indicação da região principal
    for item in entidade.get("regioes") or []:
        nome_regiao = item.get("regiao")

        if not nome_regiao:
            continue

        regiao = obter_individuo("Regiao", nome_regiao)

        g.add((regiao, RDF.type, EX.Regiao))
        g.add((
            regiao,
            RDFS.label,
            Literal(nome_regiao, lang="pt-br")
        ))

        g.add((sujeito, EX.associadaARegiao, regiao))

        if item.get("principal") in (1, True, "1"):
            g.add((
                sujeito,
                EX.associadaARegiaoPrincipal,
                regiao
            ))

    # Biomas e indicação do bioma principal
    for item in entidade.get("biomas") or []:
        nome_bioma = item.get("bioma_id")

        if not nome_bioma:
            continue

        bioma = obter_individuo("Bioma", nome_bioma)

        g.add((bioma, RDF.type, EX.Bioma))
        g.add((
            bioma,
            RDFS.label,
            Literal(nome_bioma, lang="pt-br")
        ))

        g.add((sujeito, EX.associadaABioma, bioma))

        if item.get("principal") in (1, True, "1"):
            g.add((
                sujeito,
                EX.associadaABiomaPrincipal,
                bioma
            ))

    # Matrizes culturais e povos
    for item in entidade.get("origens") or []:
        matriz_nome = item.get("matriz")

        if matriz_nome:
            matriz = obter_individuo(
                "MatrizCultural",
                matriz_nome
            )

            g.add((matriz, RDF.type, EX.MatrizCultural))
            g.add((
                matriz,
                RDFS.label,
                Literal(matriz_nome, lang="pt-br")
            ))

            g.add((
                sujeito,
                EX.possuiMatrizCultural,
                matriz
            ))

        for povo_nome in item.get("povos") or []:
            povo = obter_individuo("Povo", povo_nome)

            g.add((povo, RDF.type, EX.Povo))
            g.add((
                povo,
                RDFS.label,
                Literal(povo_nome, lang="pt-br")
            ))

            g.add((sujeito, EX.associadaAoPovo, povo))

    # Elementos primário e secundário
    for valor_elemento in [
        entidade.get("element_primary"),
        entidade.get("element_secondary")
    ]:
        if valor_elemento:
            elemento = obter_individuo(
                "Elemento",
                valor_elemento
            )

            g.add((elemento, RDF.type, EX.Elemento))
            g.add((
                elemento,
                RDFS.label,
                Literal(valor_elemento, lang="pt-br")
            ))

            g.add((
                sujeito,
                EX.possuiElemento,
                elemento
            ))

    # Variações
    for indice, item in enumerate(
        entidade.get("variacoes") or [],
        start=1
    ):
        identificador = item.get("id") or f"registro-{indice}"

        variacao = EX[
            f"variacao_{normalizar_id(slug)}_"
            f"{normalizar_id(identificador)}"
        ]

        g.add((variacao, RDF.type, EX.Variacao))
        g.add((sujeito, EX.possuiVariacao, variacao))

        adicionar_literal(
            g, variacao, EX.possuiRegistro,
            item.get("registro")
        )

        adicionar_literal(
            g, variacao, EX.possuiNomeLocal,
            item.get("nome_local")
        )

        adicionar_literal(
            g, variacao, EX.possuiLocalidade,
            item.get("localidade")
        )

        adicionar_literal(
            g, variacao, EX.possuiConfiancaVariacao,
            item.get("confianca")
        )

    # Fontes: ficha + posição garante identificador mesmo quando ref é nulo.
    for indice, item in enumerate(
        entidade.get("fontes") or [],
        start=1
    ):
        fonte = EX[
            f"fonte_{normalizar_id(slug)}_{indice}"
        ]

        g.add((fonte, RDF.type, EX.Fonte))
        g.add((sujeito, EX.possuiFonte, fonte))

        adicionar_literal(
            g, fonte, EX.possuiTipoFonte,
            item.get("tipo")
        )

        adicionar_literal(
            g, fonte, EX.possuiReferenciaFonte,
            item.get("ref")
        )

        adicionar_literal(
            g, fonte, EX.possuiLicencaFonte,
            item.get("licenca")
        )

    # Citações: ficha + posição garante identificador próprio.
    for indice, item in enumerate(
        entidade.get("citacoes") or [],
        start=1
    ):
        citacao = EX[
            f"citacao_{normalizar_id(slug)}_{indice}"
        ]

        g.add((citacao, RDF.type, EX.Citacao))
        g.add((sujeito, EX.possuiCitacao, citacao))

        adicionar_literal(
            g, citacao, EX.possuiTextoCitacao,
            item.get("citacao")
        )

        adicionar_literal(
            g, citacao, EX.possuiAutorCitacao,
            item.get("autor")
        )

        adicionar_literal(
            g, citacao, EX.possuiObraCitacao,
            item.get("obra")
        )

        adicionar_literal(
            g, citacao, EX.possuiAnoCitacao,
            item.get("ano"),
            XSD.integer
        )


# ------------------------------------------------------------
# 10. Criar relações entre entidades, incluindo referências externas
# ------------------------------------------------------------
for entidade in entidades:
    slug_origem = entidade.get("slug")

    if not slug_origem:
        continue

    origem = individuos_entidade[slug_origem]

    for indice, item in enumerate(
        entidade.get("relacionadas") or [],
        start=1
    ):
        slug_destino = item.get("relacionada_slug")

        if not slug_destino:
            continue

        destino = individuos_entidade.get(slug_destino)

        if destino is None:
            # Referência externa: criamos somente tipo, slug e nome disponível.
            destino = EX[normalizar_id(slug_destino)]
            individuos_entidade[slug_destino] = destino

            g.add((
                destino,
                RDF.type,
                EX.EntidadeFolclorica
            ))

            g.add((
                destino,
                EX.possuiSlug,
                Literal(slug_destino, datatype=XSD.string)
            ))

            adicionar_literal(
                g, destino, EX.possuiNome,
                item.get("nome")
            )

        relacao = EX[
            f"relacao_{normalizar_id(slug_origem)}_{indice}"
        ]

        g.add((
            relacao,
            RDF.type,
            EX.RelacaoEntreEntidades
        ))

        g.add((
            origem,
            EX.possuiRelacaoRegistrada,
            relacao
        ))

        g.add((
            relacao,
            EX.entidadeOrigem,
            origem
        ))

        g.add((
            relacao,
            EX.entidadeDestino,
            destino
        ))

        adicionar_literal(
            g, relacao, EX.tipoRelacao,
            item.get("tipo")
        )

        adicionar_literal(
            g, relacao, EX.motivoRelacao,
            item.get("motivo")
        )


# ------------------------------------------------------------
# 11. Exportar Turtle e apresentar resumo
# ------------------------------------------------------------
g.serialize(
    destination=str(ARQUIVO_TTL),
    format="turtle",
    encoding="utf-8"
)

print("=== ONTOLOGIA GERADA ===")
print(f"Fichas completas lidas: {len(entidades)}")
print(
    "Entidades (incluindo referências externas): "
    f"{len(individuos_entidade)}"
)
print(f"Total de triplas: {len(g)}")
print(f"Arquivo gerado: {ARQUIVO_TTL}")