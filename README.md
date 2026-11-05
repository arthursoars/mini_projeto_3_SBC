# Ontologia do Folclore Paraibano

Mini-Projeto 3 — modelagem de uma base de conhecimento com **RDF, RDFS e OWL** (Turtle), consultada com **rdflib** (`g.triples()`) e **SPARQL**.

**Autor:** José Artur Soares Afreu — UFPB

---

## 1. Resumo da base

A base reúne **32 entidades do folclore brasileiro associadas ao estado da Paraíba** (assombrações, encantados, guardiões, metamorfos, maldições e lendas de origem), com suas fontes, citações, variações regionais e relações com outras entidades.

Os dados vêm da API pública **Encantaria Digital** (`https://encantariadigital.com.br/api/v1/lendas`). A coleta percorreu todas as páginas da listagem, ficou com as entidades cujo campo `estados` contém `PB` e depois baixou a ficha completa de cada uma.

| Item | Quantidade | Mínimo exigido |
|---|---:|---:|
| Classes (`owl:Class`) | 19 | 8 |
| Propriedades de objeto | 15 | 5 |
| Propriedades de dados | 24 | 5 |
| Indivíduos (instâncias) | 407 | 25 |
| Triplas no arquivo `.ttl` | 2.845 | 50 |
| Construções OWL | 5 tipos (8 usos) | 5 |

### Sobre as 78 entidades e as 46 "referências"

Cada ficha cita outras entidades relacionadas (rivais, companheiras, variantes). Algumas delas **não são da Paraíba** e, portanto, não tiveram a ficha coletada. Para não perder as relações registradas pela API, e sem inventar informação, essas **46 entidades foram criadas como referências**: têm apenas tipo `ex:EntidadeFolclorica`, `possuiSlug` e `possuiNome`, sem classificação, bioma ou origem.

| Grupo | Quantidade | O que possui |
|---|---:|---|
| Entidades principais (fichas completas) | 32 | Classificação, nível de ameaça, biomas, fontes, citações etc. |
| Referências externas | 46 | Somente slug e nome |
| **Total de entidades** | **78** | |

As consultas que falam de "as entidades da Paraíba" filtram pelas 32 fichas completas (usando `possuiClassificacaoOriginal`).

---

## 2. Taxonomia (hierarquia de classes)

```
RecursoFolclorico
├── EntidadeFolclorica
│   ├── Assombracao
│   ├── Encantado
│   ├── Guardiao
│   ├── Metamorfo
│   ├── Maldicao
│   └── Origem
└── RecursoDocumental
    ├── Fonte
    └── Citacao
```

Há três níveis (raiz → `EntidadeFolclorica` → subclasses de classificação), atendendo ao requisito de pelo menos 2 níveis abaixo da raiz.

Classes fora da árvore, sem subclasses: `Estado`, `Regiao`, `Bioma`, `MatrizCultural`, `Povo`, `Elemento`, `Variacao` e `RelacaoEntreEntidades`.

### Subclasses de `EntidadeFolclorica`

A classificação segue a taxonomia da própria API (campo `classification`), e as seis subclasses são **disjuntas** (cada ficha tem exatamente uma).

| Subclasse | Entidades principais | Instâncias |
|---|---|---:|
| `Assombracao` | A Botija, Babau, Boi da Cara Preta, Branca Dias (A Senhora do Engenho), Cabeça Satânica, Cabra-Cabriola, Cangaceiros Fantasmas, Carro de Boi Assombrado, Fogo Corredor (Batatão), Homem do Saco, João Sem Braços, Mulher de Branco, Papa-Figo, Rasga-Mortalha | 14 |
| `Encantado` | A Lagoa Encantada potiguara, Boi Espácio, Caboclo Boiadeiro, Os Três São Miguel, Pedro Malasartes, Sopinha e Cu de Fogo, Sumé | 7 |
| `Guardiao` | Bicho de Sete Cabeças, Comadre Fulozinha, Flor-do-Mato, O Pai do Mangue, Pai Mateus, Pai-do-Mato | 6 |
| `Metamorfo` | Alma-de-Gato, Bruxa (Bruxas de Florianópolis) | 2 |
| `Maldicao` | Besta Fera, Mula Sem Cabeça | 2 |
| `Origem` | Aipó e Tambiá | 1 |
| **Total** | | **32** |

As 46 referências externas ficam apenas como `EntidadeFolclorica`.

### Demais classes e suas instâncias

| Classe | O que representa | Instâncias |
|---|---|---:|
| `Estado` | Estados associados às entidades (ex.: `Estado_pb`) | 21 |
| `Regiao` | Regiões do Brasil | 5 |
| `Bioma` | Biomas (Caatinga, Mata Atlântica, Cerrado, Amazônia, Pampa) | 5 |
| `MatrizCultural` | Matriz de origem (africana, ibérica, indígena, moderna) | 4 |
| `Povo` | Povos associados (Potiguara, Tupi, Guarani, Tupinambá, Açorianos) | 5 |
| `Elemento` | Elemento primário/secundário (água, ar, fogo, terra, misticismo) | 5 |
| `Variacao` | Variação regional do nome ou da história | 81 |
| `Fonte` | Fonte documental de uma ficha | 59 |
| `Citacao` | Citação (texto, autor, obra, ano) | 49 |
| `RelacaoEntreEntidades` | Relação registrada entre duas entidades (tipo e motivo) | 95 |

---

## 3. Propriedades

### Propriedades de objeto (15)

| Propriedade | Domínio → Alcance |
|---|---|
| `possuiEstado` | `EntidadeFolclorica` → `Estado` |
| `associadaARegiao` / `associadaARegiaoPrincipal` | `EntidadeFolclorica` → `Regiao` |
| `associadaABioma` / `associadaABiomaPrincipal` | `EntidadeFolclorica` → `Bioma` |
| `possuiMatrizCultural` | `EntidadeFolclorica` → `MatrizCultural` |
| `associadaAoPovo` | `EntidadeFolclorica` → `Povo` |
| `possuiElemento` | `EntidadeFolclorica` → `Elemento` |
| `possuiVariacao` | `EntidadeFolclorica` → `Variacao` |
| `variaDe` | `Variacao` → `EntidadeFolclorica` |
| `possuiFonte` | `EntidadeFolclorica` → `Fonte` |
| `possuiCitacao` | `EntidadeFolclorica` → `Citacao` |
| `possuiRelacaoRegistrada` | `EntidadeFolclorica` → `RelacaoEntreEntidades` |
| `entidadeOrigem` / `entidadeDestino` | `RelacaoEntreEntidades` → `EntidadeFolclorica` |

### Propriedades de dados (24)

| Domínio | Propriedades (tipo do valor) |
|---|---|
| `EntidadeFolclorica` | `possuiSlug`, `possuiNome`, `possuiDescricao`, `possuiTagline`, `possuiCausoCompleto`, `possuiClassificacaoOriginal`, `possuiNivelAmeaca`, `possuiRaridade`, `possuiConfianca`, `possuiCultoVivo` (`xsd:string`); `possuiOrigemIncerta` (`xsd:boolean`) |
| `Variacao` | `possuiRegistro`, `possuiNomeLocal`, `possuiLocalidade`, `possuiConfiancaVariacao` (`xsd:string`) |
| `Fonte` | `possuiTipoFonte`, `possuiReferenciaFonte`, `possuiLicencaFonte` (`xsd:string`) |
| `Citacao` | `possuiTextoCitacao`, `possuiAutorCitacao`, `possuiObraCitacao` (`xsd:string`); `possuiAnoCitacao` (`xsd:integer`) |
| `RelacaoEntreEntidades` | `tipoRelacao`, `motivoRelacao` (`xsd:string`) |

Todas têm `rdfs:domain` e `rdfs:range` declarados.

---

## 4. Construções OWL

| Construção | Onde | Justificativa no domínio |
|---|---|---|
| `owl:FunctionalProperty` | `possuiSlug` | Cada entidade tem um único identificador (slug) na API. |
| `owl:FunctionalProperty` | `entidadeOrigem`, `entidadeDestino` | Cada relação registrada tem exatamente uma origem e um destino. |
| `owl:Restriction` (`owl:cardinality 1`) | `EntidadeFolclorica` sobre `possuiSlug` | Toda entidade, inclusive as referências externas, possui exatamente um slug. |
| `owl:hasKey` | `EntidadeFolclorica` → (`possuiSlug`) | O slug identifica univocamente uma entidade. |
| `owl:AllDisjointClasses` | As 6 subclasses de `EntidadeFolclorica` | A taxonomia da fonte classifica cada ficha em uma única categoria. |
| `owl:inverseOf` | `possuiVariacao` ↔ `variaDe` | Uma entidade tem variações e cada variação pertence a uma entidade. |
| `owl:inverseOf` | `possuiRelacaoRegistrada` ↔ `entidadeOrigem` | A entidade possui o registro da relação, e a relação aponta para a entidade de origem. |

A ontologia também tem o cabeçalho `owl:Ontology`, com título, descrição e versão.

---

## 5. Consultas

### Parte 1 — rdflib com `g.triples()` (`consultas_rdflib.py`)

Além de validar a estrutura (contagem de classes, propriedades, domínios/alcances e construções OWL), o script executa 7 consultas com padrões variados. Cada uma está comentada no código com o padrão, o que busca e o resultado esperado.

| # | Padrão | O que busca | Resultado |
|---|---|---|---|
| 1 | `(None, rdf:type, classe)` | Entidades folclóricas pelas 6 subclasses | 32 entidades |
| 2 | `(None, possuiEstado, Estado_pb)` | Entidades associadas à Paraíba | 32 entidades |
| 3 | `(None, associadaABioma, Bioma_caatinga)` | Entidades associadas à Caatinga | 21 entidades |
| 4 | `(None, tipoRelacao, None)` + sujeito e predicado fixos | Relações do tipo `rival`, com origem, destino e motivo | 8 relações |
| 5 | `(None, rdf:type, Citacao)` + sujeito e predicado fixos | Citações com autor, obra e texto | 49 citações |
| 6 | `(ex:mula-sem-cabeca, None, None)` | Tudo o que se sabe sobre a Mula Sem Cabeça (sujeito fixo) | Pares propriedade → valor |
| 7 | `(None, None, Bioma_caatinga)` | Quem aponta para a Caatinga, por qualquer propriedade (objeto fixo) | 21 por bioma + 15 por bioma principal |

### Parte 2 — SPARQL (`consultas_sparql.py`)

| # | Tipo | Propósito |
|---|---|---|
| 1 | `SELECT` + `ORDER BY` | Entidades e suas classificações em ordem alfabética |
| 2 | `SELECT` + `FILTER` | Entidades com nível de ameaça "baixo" |
| 3 | `SELECT` + `ORDER BY DESC` | Nomes das 32 entidades em ordem decrescente |
| 4 | `SELECT` + `COUNT`/`GROUP BY` | Quantidade de entidades por classificação |
| 5 | `ASK` | Aipó e Tambiá está associada à Paraíba? |
| 6 | `ASK` | Existe entidade associada à Caatinga? |
| 7 | `CONSTRUCT` | Grafo reduzido (nome e estado) das entidades da Paraíba |
| 8 | `INSERT DATA` | Insere um indivíduo temporário de teste (3 triplas) |
| 9 | `DELETE/INSERT WHERE` | Altera a confiança do indivíduo de "baixa" para "media" |
| 10 | `DELETE DATA` | Remove o indivíduo temporário |

As atualizações (8 a 10) alteram **apenas o grafo em memória**; o arquivo `.ttl` não é modificado. A saída mostra o indivíduo inserido, o total após a inserção (2.848), a mudança de valor e o total após a remoção, igual ao inicial (2.845).

---

## 6. Como executar

**Requisitos:** Python 3.9 ou superior.

```bash
pip install rdflib requests
```

Dentro da pasta `folclore-paraibano/`:

```bash
# 1. Consultas com g.triples()
python consultas_rdflib.py

# 2. Consultas SPARQL e atualizações
python consultas_sparql.py
```

No Windows, use `py` no lugar de `python`.

Os dois scripts carregam o arquivo `folclore_paraibano.ttl`, que já está no repositório. Eles não precisam de internet.

### Regenerar os dados (opcional)

Estas etapas refazem o `.ttl` desde a API e precisam de internet. Rode nesta ordem:

```bash
python coleta_entidades.py            # lista as entidades da PB  -> entidades_paraiba_resumo.json
python coletar_fichas_completas.py    # baixa as 32 fichas        -> entidades_paraiba_completo.json
python gerar_ontologia.py             # gera folclore_paraibano.ttl
```

`gerar_ontologia.py` usa só o JSON local, então pode ser executado sem internet.

---

## 7. Estrutura do repositório

```
folclore-paraibano/
├── folclore_paraibano.ttl            # base de conhecimento (Turtle)
├── gerar_ontologia.py                # JSON -> Turtle (classes, propriedades, indivíduos, OWL)
├── consultas_rdflib.py               # Parte 1: validação e consultas com g.triples()
├── consultas_sparql.py               # Parte 2: SELECT, ASK, CONSTRUCT e Update
├── coleta_entidades.py               # coleta a listagem da API e filtra por PB
├── coletar_fichas_completas.py       # coleta a ficha completa de cada entidade
├── diagnostico_api.py                # testes exploratórios da API
├── entidades_paraiba_resumo.json     # listagem filtrada
└── entidades_paraiba_completo.json   # 32 fichas completas
```

## 8. Observações

- O namespace `https://w3id.org/folclore-paraibano/ontology#` é um identificador de projeto e não está registrado no w3id.org.
- O `ORDER BY` do SPARQL compara os caracteres pelo código Unicode. Por isso, nomes com acento (como "Mãe-do-Ouro") podem aparecer fora da ordem alfabética esperada.
- Duas fichas (Pedro Malasartes e Sumé) não têm o campo `confianca` na API, então ficam sem a propriedade `possuiConfianca`.
- O conteúdo das fichas (descrições, causos, citações) pertence à API Encantaria Digital; cada fonte registra sua licença em `possuiLicencaFonte`.
