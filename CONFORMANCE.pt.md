> Tradução comunitária (rascunho) — Política NTARI P2-002, Transmissão Multilíngue Global (Global Multilingual Broadcast). Fonte: CONFORMANCE.md (original em inglês, snapshot de 2026-10-05). Rascunho comunitário assistido por máquina, pendente de revisão por mantenedor regional conforme P2-002 §3.1. As especificações técnicas centrais permanecem em inglês conforme §2.2.
>
> Notou algum erro nesta tradução? Correções de tradução são contribuições
> valiosas e muito bem-vindas: faça um fork do repositório e abra um pull
> request em https://github.com/NTARI-RAND/Leveson-Based-Trade-Assessment-Scale.

> O original em inglês é normativo. Esta tradução é oferecida para leitura, não para interpretação: onde ela divergir de `CONFORMANCE.md`, prevalece o inglês. As palavras-chave normativas (MUST, MUST NOT, SHOULD, SHOULD NOT, MAY), os nomes de campos, os rótulos e os identificadores são mantidos em inglês porque constituem o contrato de conformidade.

# Conformidade — Arquitetura de Dupla Face (Janus-Facing Architecture)

A autodescrição do repositório nos próprios termos da arquitetura, apresentada **antes** de qualquer coisa específica do produto, conforme a regra de ordenação da arquitetura. Toda alegação de conformidade está vinculada ao mecanismo e à verificação que a fazem cumprir, ou então é rotulada como provisória (stand-in). Prosa sem vínculo é marketing.

A arquitetura é a **Arquitetura de Dupla Face (Janus-Facing Architecture, JFA)** — o documento de arquitetura unificada da NTARI, documentação livre sob o commons AGPL-3.0 do projeto.

## Declaração de papel

O LBTAS é a **escala de avaliação** da **camada de Pacto** da JFA: a reputação como uma promessa permanente de não causar dano, carregada como uma distribuição completa — nunca uma pontuação. A lógica é a do engenheiro de segurança (Leveson): o dano é um evento discreto a ser revelado, não uma quantidade a ser suavizada; dois acidentes em setenta e três voos mantêm a frota em terra. A escala é de domínio geral: uma economia consumidora a adota e a interpreta em contexto.

| Termo deste repositório | Papel na arquitetura |
|---|---|
| A escala ordinal de 6 níveis (−1..+4) | o vocabulário de avaliação carregado de significado do pacto; **−1 é a própria violação** |
| `{distribution, total}` | a reputação carregada como a arquitetura exige: a contagem em cada nível ao lado do total |
| Avaliação bidirecional | simetria do pacto entre contrapartes |
| Distribuições por categoria | leituras com escopo de relação (nunca reduzidas a um único número) |

## Invariantes e seus vínculos — conforme `main` (v2.0.0)

| Invariante (arquitetura) | Mecanismo aqui | Verificação |
|---|---|---|
| A reputação MUST NOT ser reduzida a uma pontuação por média | A API de leitura da v2.0.0 retorna `{distribution, total}` por categoria; `system_average`, `category_averages` e as listas de participantes classificadas por média foram **removidos** | CHANGELOG 2.0.0 (incompatível); o comentário sobre a unidade de reputação no código; não existe nenhum caminho de cálculo de média para chamar |
| A **avaliação mais baixa é a própria violação** | −1 ("No Trust") é um evento de dano discreto, mantido permanentemente visível na distribuição ao lado de qualquer volume | Forma da distribuição; não existe nenhuma aritmética de compensação |
| O pacto é **simétrico** entre contrapartes | Bidirecional por design: uma única troca pode produzir duas avaliações, produtor↔consumidor, com a mesma escala nos dois sentidos | Definição da escala; API |
| A escala é **carregada de significado e ordinal** — não um eixo contínuo | Cada nível carrega uma definição específica; inteiros −1..+4 | Tabela canônica do CLAUDE.md; validação |
| A reputação controla **se**, nunca **quanto** | A biblioteca não deriva da distribuição nenhum limite de crédito, peso ou teto — não existe nenhuma API desse tipo | Superfície da API |
| **Não portável por padrão** | Dados por plataforma; nenhuma identidade entre plataformas nem caminho de importação na biblioteca | Superfície da API |
| **Diversidade observacional entre implementações** | Quatro implementações de referência (Go, Python, Rust, TypeScript) que devem permanecer em paridade — codificações independentes de um mesmo comportamento | Regra de paridade do CLAUDE.md; ver provisórias |

## Deliberadamente fora do escopo

A mecânica de contestação — registro de alegações, adjudicação, arquivamento como anotação, o selo — pertence às **camadas de Registro e de disputa** da plataforma consumidora, não a esta biblioteca. O LBTAS fornece o vocabulário e a distribuição; o registro fornece a responsabilização. Uma plataforma consumidora que adota a escala sem um fluxo de alegações passíveis de resposta não implementou o pacto.

## Provisórias e resíduos em aberto

- **Os vetores de referência (golden vectors) entre implementações são uma meta, ainda não um bloqueio.** A paridade entre as quatro implementações é uma regra declarada, imposta por revisão; um conjunto de vetores compartilhado que faça o CI falhar diante de deriva (o padrão do repositório do protocolo) é a verificação assumida como compromisso. Até que ele exista, a paridade é imposta por revisão e rotulada como tal.
- **A responsabilização do adjudicador** é a violação de simetria nomeada pela arquitetura — uma parte avaliada sem resposta. Ela vincula as camadas de disputa das plataformas consumidoras; esta biblioteca não deve encobri-la expondo qualquer caminho de avaliação sem resposta.
- **A tipagem de relações** (comércio / conduta de adjudicação / satisfação com o veredicto) é carregada aqui apenas como distribuições por categoria; a disciplina completa de relações tipadas vincula na camada de Registro das plataformas consumidoras.

## Declaração de dependências

Uma biblioteca folha: nenhuma dependência de qualquer coordenador, frontend ou implementação de registro. As economias consumidoras dependem dela; ela não depende de nenhuma delas.

## Notas específicas do produto (por último, conforme a regra de ordenação)

Adotada por economia, no nível econômico. As plataformas consumidoras fixam uma versão publicada; o modelo de distribuição da v2 é o piso para qualquer nova adoção.
