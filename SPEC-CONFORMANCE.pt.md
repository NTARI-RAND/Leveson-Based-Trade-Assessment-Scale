> Tradução comunitária (rascunho) — Política NTARI P2-002, Transmissão Multilíngue Global (Global Multilingual Broadcast). Fonte: SPEC-CONFORMANCE.md (original em inglês, snapshot de 2026-10-05). Rascunho comunitário assistido por máquina, pendente de revisão por mantenedor regional conforme P2-002 §3.1. As especificações técnicas centrais permanecem em inglês conforme §2.2.
>
> Notou algum erro nesta tradução? Correções de tradução são contribuições
> valiosas e muito bem-vindas: faça um fork do repositório e abra um pull
> request em https://github.com/NTARI-RAND/Leveson-Based-Trade-Assessment-Scale.

> O original em inglês é normativo. Esta tradução é oferecida para leitura, não para interpretação: onde divergir de `SPEC-CONFORMANCE.md`, prevalece o inglês. As palavras-chave normativas (MUST, MUST NOT, SHOULD, SHOULD NOT, MAY), os nomes de campos, os rótulos e os identificadores são mantidos em inglês porque constituem o contrato de conformidade.

# Registro de Conformidade do LBTAS

Situação de cada implementação em relação a [`SPEC.md`](SPEC.md) (P3-014). Conforme o
método da JFA, este registro apresenta a situação às claras, em vez de encenar a ausência de lacunas.

**Auditado:** 2026-07-01 em relação à SPEC v0.1. **Resultado:** nenhuma violação — nenhuma média
em parte alguma, nenhuma deriva de rótulos, nenhum limite derivado da distribuição de danos.

Legenda: **yes** = implementado · **no** = ainda não (nível de código) · **app** = questão do
aplicativo do operador, documentada mas não implementada em uma implementação de referência autônoma.

## Matriz

| # | Invariante (SPEC §) | py | ts | go | rs | Agrinet¹ |
|---|---|:--:|:--:|:--:|:--:|:--:|
| 1 | Escala −1..+4 com rótulos exatos (§1) | yes | yes | yes | yes | yes |
| 2 | Distribuição, nunca uma média (§2) | yes | yes | yes | yes | yes² |
| 3 | Reputação delimitada por papel (§3) | no | no | no | no | yes |
| 4 | −1 traz uma narrativa ≤500 palavras, local ao operador (§4) | app | app | app | app | yes |
| 5 | Somente acréscimo (append-only); o indeferimento anota, nunca apaga (§4, §6) | app | app | app | app | yes |
| 6 | Simétrico — contestável nos dois sentidos (§5) | app | app | app | app | yes |
| 7 | Padrão de timeout +2, atribuído ao sistema e marcado (§7) | app | app | app | app | yes |
| 8 | Decide se, não quanto (§8) | yes | yes | yes | yes | yes |

¹ Agrinet = `services/lbtas.js` + `repositories/ratingRepository.js` em `NTARI-RAND/Agrinet`.
² O Agrinet, além disso, **lança uma exceção** se uma pontuação de reputação de número único for solicitada em algum momento (`utils/reputation.js`).

## Pelo que cada camada é responsável

A escala e o modelo de leitura da distribuição são o **núcleo do algoritmo** — toda implementação
de referência os contém, e todas as cinco concordam quanto aos seis rótulos (Delight, No Negative
Consequences, Basic Satisfaction, Basic Promise, Cynical Satisfaction, No Trust), sem
deriva.

O restante do ciclo de vida do pacto divide-se por camada:

- **Nível de código, pertence a uma implementação de referência:** a escala e a distribuição (§1, §2),
  e a **delimitação por papel** (§3). A delimitação por papel — indexar a distribuição pelo papel
  da parte avaliada — é a única invariante de nível de código que ainda não está nas implementações
  de referência autônomas; ela está plenamente implementada no Agrinet e é a melhoria rastreada para py/ts/go/rs.
- **Questões do aplicativo do operador, corretamente *documentadas* mas não implementadas em uma implementação de referência:**
  a narrativa de ≤500 palavras e seu armazenamento local ao operador (§4), eventos append-only com
  indeferimento como anotação (§4, §6), contestação bidirecional (§5) e o padrão de timeout da
  janela de avaliação (§7). Estas exigem um armazenamento de dados, um papel de adjudicador e um relógio —
  elas residem no operador (Agrinet), que implementa todas elas.

## Lacunas declaradas com honestidade

- **Delimitação por papel em py/ts/go/rs** — ainda não implementada (rastreada). As leituras centrais são
  agnósticas quanto ao papel; um operador que precise de distribuições por papel faz como o Agrinet faz.
- Nenhuma implementação calcula médias, expõe uma pontuação única ou deriva um limite da distribuição
  de danos — as invariantes cuja violação reconstruiria o birô de crédito são todas mantidas.
