> Tradução comunitária (rascunho) — Política NTARI P2-002, Transmissão Multilíngue Global (Global Multilingual Broadcast). Fonte: SPEC.md (original em inglês, snapshot de 2026-10-05). Rascunho comunitário assistido por máquina, pendente de revisão por mantenedor regional conforme P2-002 §3.1. As especificações técnicas centrais permanecem em inglês conforme §2.2.
>
> Notou algum erro nesta tradução? Correções de tradução são contribuições
> valiosas e muito bem-vindas: faça um fork do repositório e abra um pull
> request em https://github.com/NTARI-RAND/Leveson-Based-Trade-Assessment-Scale.

> O original em inglês é normativo. Esta tradução é oferecida para leitura, não para interpretação: onde divergir de `SPEC.md`, prevalece o inglês. As palavras-chave normativas (MUST, MUST NOT, SHOULD, SHOULD NOT, MAY), os nomes de campos, os rótulos e os identificadores são mantidos em inglês porque constituem o contrato de conformidade.

# Especificação do LBTAS — reputação como pacto, não como pontuação

**Network Theory Applied Research Institute**
ID do documento: P3-014 · Versão: 0.1 (Rascunho) · Junho de 2026
*Especificação normativa da Leveson-Based Trade Assessment Scale. Complemento de
P3-011 v2 (Janus Facing Applications), P3-012 (Agrinet Protocol Specification) e
P3-013 (Mycelium). Vinculada à* Janus-Facing Architecture *(guia do construtor, v2.0) e a*
Building JFA Software *(v1.0).*

As palavras-chave **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT** e **MAY** são usadas
conforme a RFC 2119.

---

## 0. O que é o LBTAS

O LBTAS é a **camada de pares / reputação** de uma rede da Janus-Facing Architecture. Ele é um
**pacto** — uma promessa permanente de não causar dano — **e não uma pontuação**. Sua lógica é a do
engenheiro de segurança (Nancy Leveson): dois acidentes em setenta e três voos deixam a frota em solo.
O volume é um sinal, mas nenhuma quantidade de boas avaliações dilui um dano em uma média
confortável.

Aqui, a reputação é binária onde importa: um membro está **em situação regular** ou **em
violação**. A avaliação mais baixa da escala, um `−1`, **é a própria violação** — e não um débito
contra um total acumulado.

Este documento define a escala, o modelo de leitura e as invariantes que qualquer implementação
conforme MUST manter. O README traz a justificativa; este arquivo traz os
requisitos. As implementações de referência (`lbtas.py`, `.ts`, `.go`, `.rs`) estão vinculadas a
ele.

---

## 1. A escala

Uma avaliação é um número inteiro em uma **escala de seis pontos**, de `−1` a `+4`:

| Valor | Rótulo | Significado |
|---|---|---|
| `+4` | Delight | Antecipa a evolução das práticas e preocupações do usuário após a transação. |
| `+3` | No Negative Consequences | Projetado para evitar perdas; supera a qualidade básica. |
| `+2` | Basic Satisfaction | Atende a padrões socialmente aceitáveis que excedem as demandas articuladas. |
| `+1` | Basic Promise | Atende a todas as demandas articuladas, nada mais. |
| `0` | Cynical Satisfaction | Cumpre uma promessa básica com pouca ou nenhuma disciplina voltada à satisfação. |
| `−1` | No Trust | O usuário foi prejudicado, explorado ou recebeu um produto/serviço sem disciplina ou com intenção maliciosa. |

`−1` é categoricamente distinto de `0…+4`: a faixa positiva gradua a *qualidade*; `−1`
registra o *dano*. As implementações MUST tratar `−1` como uma violação, nunca como "um abaixo de zero".

---

## 2. Distribuição, nunca uma média

Uma reputação é uma **distribuição**: a contagem de avaliações em cada nível (`−1, 0, +1, +2,
+3, +4`) ao lado do total.

- Uma implementação **MUST NOT** calcular nem expor uma média, média aritmética, pontuação ponderada ou
  qualquer redução das avaliações a um único número, em nenhuma leitura, relatório, selo ou API.
- O volume fica *ao lado* do dano; ele nunca o cancela. Um dano permanece visível para sempre ao lado
  do volume.
- As leituras **SHOULD** expor também a **contagem de transações** e o **tempo de permanência** (carimbos de
  data/hora da primeira e da última avaliação): a contagem e o tempo de permanência são, eles mesmos, sinais de confiança.

Um teste de conformidade: procure na implementação qualquer divisão de uma soma de avaliações por uma
contagem, ou qualquer campo chamado `score`/`average`/`rating` que reduza a distribuição. Uma
implementação correta não tem nenhum. (As implementações de referência lançam um erro onde, de outra forma, uma
pontuação seria calculada.)

---

## 3. Delimitada por papel

A reputação é mantida **separadamente por papel** — a capacidade em que a parte avaliada atuou
(por exemplo, `market_seller`/`market_buyer`, `service_provider`/`service_client`,
`plan_producer`/`plan_backer`), derivada do tipo de troca e do lado da parte
avaliada. Um `−1` obtido em um papel **MUST NOT** contaminar a distribuição de outro. A
mesma pessoa pode ter várias reputações delimitadas por papel ao mesmo tempo.

---

## 4. O dano traz uma narrativa; o dano nunca é ocultado

- Um `−1` **MUST** trazer uma **narrativa justificativa de ≤ 500 palavras**. Um `−1` sem
  narrativa é inválido e MUST ser rejeitado.
- A narrativa é **local ao operador**: mantida no frontend, referenciada (não transportada) pelo
  registro do protocolo, **nunca** ancorada no livro-razão do commons, **nunca** federada, e
  lida apenas pelas próprias partes do registro e pelo adjudicador do operador (P3-013 §6).
- O **evento** de avaliação é **imutável e somente acréscimo (append-only)**. Não há atualização nem exclusão.
- Um **indeferimento anota, nunca apaga** (§6): ele remove o evento da distribuição de confiança
  *ativa*, mas o evento permanece visível a jusante, anotado com **quem o
  indeferiu e por quê**. Um frontend **MAY** perdoar o dano; ele **MUST NOT** ser capaz de
  ocultá-lo.

---

## 5. Simétrico — contestável nos dois sentidos

O pacto vale **nos dois sentidos**. O `−1` dado por um produtor a um consumidor é **tão contestável quanto**
o inverso.

- Qualquer parte avaliada **MAY** contestar uma avaliação feita contra ela, em **qualquer** sentido.
- O sistema **MUST NOT** codificar que uma classe (por exemplo, vendedores) é confiável e a
  outra (por exemplo, compradores) é o risco. Não há sentido privilegiado.
- A não entrega é, ela mesma, um dano e pertence ao pacto (veja o §8 para o que *não* pertence).

---

## 6. Adjudicação: indeferir = anotar

Um adjudicador (um papel **local ao operador**, nunca uma autoridade global sobre o commons)
**MAY** indeferir uma avaliação considerada de má-fé.

- Um indeferimento é registrado como uma **nova anotação**, nunca como edição ou exclusão (§4, P3-013
  §7). O evento indeferido e a anotação são ambos permanentes e ambos visíveis.
- Uma leitura calcula a distribuição **ativa** *excluindo* os eventos indeferidos, enquanto ainda
  **apresenta cada evento indeferido** com a parte que o indeferiu e o motivo e, no caso de uma
  avaliação contestada mas mantida, o fato de ter sido mantida.

---

## 7. Os padrões de timeout são marcados

Quando uma troca é concluída, mas uma parte não avalia dentro de sua **janela de avaliação**, o
sistema atribui uma **avaliação padrão de `+2`** ("Basic Satisfaction"): o silêncio é lido como uma
troca que terminou sem reclamação — **não** como elogio, e **não** como dano.

- Um padrão de timeout **MUST** ser **atribuído ao sistema** (`rater_role = system`) e
  **marcado como padrão de timeout**.
- Ele **MUST** ser **distinguível na distribuição** de uma avaliação afirmada por uma parte em toda
  leitura (assim como um indeferimento), para que uma reputação construída em parte a partir do silêncio nunca seja confundida
  com uma construída a partir de afirmações. As leituras **SHOULD** apresentar uma contagem `defaulted`.
- `+2` é o padrão conservador (não infla a reputação); `+3` é a
  alternativa documentada. Esta é a única constante ajustável da escala.

---

## 8. Decide se, não quanto

O LBTAS decide **se** um membro chega a negociar com base em confiança — **nunca quanto**.

- O que o pacto assegura é **honestidade, não capacidade**: "Não vou prejudicar você" não é "Eu
  consigo entregar o que prometi".
- **Delimitar o tamanho** de um compromisso que um ator honesto pode assumir é um **limite**, que
  pertence à **camada econômica**, não ao LBTAS. O limite **MUST** ser derivado de
  algo *diferente* da distribuição de danos (volume limpo, capacidade declarada, uma linha de
  partida uniforme).
- Uma implementação **MUST NOT** derivar um limite ou teto de gastos/crédito da distribuição do
  LBTAS. Permitir que a situação regular compre um teto mais alto transforma a distribuição de danos
  em uma pontuação de crédito — o banco pela porta dos fundos. O pacto controla a porta; o
  limite dimensiona a sala; mantenha-os separados.

---

## 9. Relação com a liquidação

Onde o LBTAS controla a liberação de uma custódia (escrow) (P3-012 §7): a avaliação do consumidor é o gatilho
da liberação. Um `0…+4` libera os fundos retidos; um `−1` **não** libera — ele congela os fundos
e abre uma auditoria. A avaliação posterior que o produtor faz do consumidor não movimenta dinheiro algum. Esta é uma
regra de *liquidação* que consome o LBTAS; ela não faz parte da escala em si.

---

## 10. Garantias e não garantias

**Garantias.** Um LBTAS conforme apresenta o dano de forma permanente e visível, nunca o dilui
em uma média, mantém-no delimitado por papel, torna toda alegação passível de resposta nos dois sentidos e
distingue as avaliações afirmadas do silêncio e dos indeferimentos.

**Não garantias.** O LBTAS atesta **honestidade, não capacidade** (§8), e não atesta
a honestidade da computação que produziu uma troca (um pareamento ou um preço manipulados) — isso
está fora do escopo, verificado apenas pela legibilidade e pela saída barata (P3-013 §9).

---

## 11. Conformidade

Uma implementação é conforme se e somente se **todas** as condições a seguir forem atendidas:

1. As avaliações são inteiros `−1…+4`; `−1` é tratado como uma violação, não como uma pontuação baixa (§1).
2. A reputação é exposta **somente** como uma distribuição — nenhuma média, média aritmética ou pontuação única
   em parte alguma (§2).
3. A reputação é **delimitada por papel** (§3).
4. Um `−1` exige uma narrativa de ≤ 500 palavras; a narrativa é local ao operador e nunca fica
   no commons (§4).
5. Os eventos de avaliação são somente acréscimo (append-only); os indeferimentos **anotam, nunca apagam**, e permanecem
   visíveis (§4, §6).
6. O pacto é **simétrico** — contestável nos dois sentidos, sem classe privilegiada
   (§5).
7. Os padrões de timeout são `+2`, **atribuídos ao sistema e marcados**, distinguíveis na
   distribuição (§7).
8. Nenhum limite ou teto é derivado da distribuição — ele **decide se, não
   quanto** (§8).

---

## 12. Situação da implementação (informativo)

| Elemento | Situação |
|---|---|
| Escala de seis pontos, rótulos (§1) | **Implementado** (`lbtas.py`/`.ts`/`.go`/`.rs`; README) |
| Distribuição, nunca uma média (§2) | **Implementado** (implementações de referência; Agrinet `services/lbtas.js` + `utils/reputation.js` lança uma exceção se uma pontuação for solicitada) |
| Delimitada por papel (§3) | **Implementado no Agrinet** (`ratingRepository.getUserReputation` por papel); **delta:** incorporar a delimitação por papel às implementações de referência autônomas |
| Narrativa de `−1` ≤ 500 palavras, local ao operador (§4) | **Implementado no Agrinet** (`rating_narratives`); **delta:** documentar nas implementações de referência |
| Append-only; indeferir = anotar (§4, §6) | **Implementado no Agrinet** (`voidById`/`upholdContest`, indeferidos apresentados); **delta:** implementações de referência |
| Contestação simétrica (§5) | **Implementado no Agrinet** (`contestRating` nos dois sentidos) |
| Padrão de timeout `+2`, marcado (§7) | **Implementado no Agrinet** (`applyRatingTimeouts`, contagem `defaulted`) |
| Decide se, não quanto (§8) | **Conforme por ausência** — não existe em parte alguma um limite derivado de avaliações |

As implementações de referência autônomas aqui cobrem a escala e a distribuição
fielmente; o ciclo de vida do pacto (delimitação por papel, narrativa, contestação/indeferimento, padrão
de timeout) está atualmente mais completo no backend do Agrinet e está sendo reconciliado de volta
com as implementações de referência. Veja [CONFORMANCE.md](CONFORMANCE.md) para a matriz por implementação
(auditada: nenhuma violação; a delimitação por papel é a única lacuna no nível do código nas implementações
de referência autônomas).

---

*Network Theory Applied Research Institute, Inc. — 501(c)(3) — info@ntari.org*
*Documentação livre sob o commons AGPL-3.0 do projeto — feita para ser lida, reimplementada e contestada.*
