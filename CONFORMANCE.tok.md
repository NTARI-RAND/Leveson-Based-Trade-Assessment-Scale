# lipu pi nasin sama — Janus-Facing Architecture (toki pona)

> **toki lili pi lipu ni:** lipu ni li lipu pi kulupu, li tan nasin NTARI "P2-002". lipu suli li lipu Inli "CONFORMANCE.md" (tenpo pi 2026-10-05). ilo sona li pali e lipu ni; kulupu li wile lukin e ona kepeken nasin "P2-002" kipisi "3.1".
>
> **Note:** This is a community rendering under NTARI policy P2-002. The complete document is the English original CONFORMANCE.md (snapshot 2026-10-05). Machine-assisted draft pending community review per P2-002 section 3.1.
>
> sina lukin e pakala lon toki ni la o pona e ona: o pali e "fork" lon
> https://github.com/NTARI-RAND/Leveson-Based-Trade-Assessment-Scale, o pana e
> "pull request". pana sina li pona tawa mi mute.
>
> **lipu Inli li lawa.** lipu ni li tawa lukin, li tawa ala sona pi nasin lawa: lipu ni li ante tan `CONFORMANCE.md` la lipu Inli li lawa. nimi lawa (MUST, MUST NOT, SHOULD, SHOULD NOT, MAY), nimi pi poki sona, nimi sitelen en nimi ilo li awen lon toki Inli, tan ni: ona li lipu lawa pi nasin sama.

---

lipu ni la poki lipu li toki e ona sama kepeken nimi pi nasin JFA. ona li toki e ni **lon open**, li toki ala e ijo pi ilo ni taso lon open, tan nasin pi nanpa toki pi nasin JFA. toki ale pi nasin sama li linja tawa ilo en lukin ni: ilo en lukin li wawa e toki ni. linja li lon ala la sitelen li toki e ni: toki ni li ijo pi tenpo lili (stand-in). toki pi linja ala li toki esun taso.

nasin ni li **Janus-Facing Architecture (JFA)** — lipu wan pi nasin ilo pi kulupu NTARI. ona li lipu pi jan ale, li lon poki pi jan ale pi poki ni (nasin AGPL-3.0).

## toki pi pali

ilo LBTAS li **nasin nanpa pi lukin esun** lon **kipisi pi toki awen** (Covenant layer) pi nasin JFA: sona pi jan li toki awen pi ni: "mi ike ala e sina." sona ni li awen kepeken mute ale pi pana — ona li nanpa wan ala lon tenpo ale. nasin sona ona li nasin pi jan sona pi awen jan (jan Leveson): ike li ijo wan pi tenpo wan, li ijo ala pi mute: jan o pana e ona tawa lukin, o lili ala e ona kepeken nanpa meso. tomo waso li pakala tu lon tawa 73 la tomo waso ale pi kulupu ni li awen lon ma. nasin nanpa ni li tawa ma esun ale: esun pi kepeken li kama jo e ona, li sona e kon ona lon ma pi esun ni.

| nimi pi poki ni | pali lon nasin JFA |
|---|---|
| nasin nanpa pi sewi anpa, li jo e nanpa 6 (−1..+4) | nimi pi pana nanpa lon kipisi pi toki awen; nimi ale li jo e kon suli; **−1 li pakala sama pi toki awen** |
| `{distribution, total}` | sona pi jan li awen kepeken nasin ni, tan wile pi nasin JFA: mute lon nanpa ale li lon poka pi mute ale |
| pana tawa poka tu (Bidirectional rating) | toki awen li sama tawa jan tu pi esun |
| mute ale pi pana pi kulupu wan wan (Per-category) | lukin lon linja jan wan (relation-scoped) — ona li kama ala nanpa wan lon tenpo ale |

## nasin awen en linja ona — lon `main` (v2.0.0)

| nasin awen (nasin JFA) | ilo lon ni | lukin |
|---|---|---|
| sona pi jan li MUST NOT kama nanpa wan kepeken nanpa meso | ilo lukin API pi v2.0.0 li pana e `{distribution, total}` tawa kulupu wan wan; `system_average`, `category_averages`, en lipu nimi pi jan pali lon nasin pi nanpa meso li **weka** | CHANGELOG 2.0.0 (ante pakala, breaking); toki lili lon lipu ilo li toki e wan pi sona jan; nasin pi nanpa meso li lon ala, la jan li ken ala kepeken ona |
| **pana anpa nanpa wan li pakala sama pi toki awen** | −1 ("No Trust") li ijo ike wan; ona li lon mute ale pi pana, li ken lukin lon tenpo ale, lon poka pi mute ante ale | sijelo pi mute ale pi pana; nasin nanpa pi weka e ike li lon ala |
| toki awen li **sama tawa poka tu** pi esun | poka tu tan nasin: esun wan li ken pana e pana nanpa tu, jan pali↔jan kepeken, nasin nanpa sama li lon poka tu | toki pi nasin nanpa; ilo API |
| nasin nanpa li **jo e kon, li nasin pi sewi anpa** — ona li linja nanpa ala pi kipisi ala | nanpa ale li jo e toki kon wan; nanpa pi kipisi ala −1..+4 | lipu leko lawa lon CLAUDE.md; lukin pi pona nanpa |
| sona pi jan li toki e **ken anu ken ala**, li toki ala e **mute** lon tenpo ale | poki ilo li kama ala jo e sewi pi mani pana, e nanpa wawa, e sewi pini tan mute ale pi pana — ilo API ni li lon ala | selo API |
| **ona li ken ala tawa ma ante, tan nasin open** | sona li lon ma ilo wan wan; poki ilo li jo ala e nimi jan pi ma ilo mute, li jo ala e nasin pi kama insa | selo API |
| **lukin mute ante lon ilo pali mute** | ilo pali tu tu pi nasin lukin (Go, Python, Rust, TypeScript) li wile awen sama — sitelen ilo ante li pali e nasin wan, li lawa ala e ona ante | lawa pi sama lon CLAUDE.md; o lukin e ijo pi tenpo lili |

## ijo li lon ala insa pi lipu ni tan wile

nasin pi utala toki — pana pi toki utala, lawa pi utala, weka kepeken toki poka (dismissal-as-annotation), pini awen (seal) — li ijo pi **kipisi sona en kipisi pi toki utala** lon ma ilo pi kepeken, li ijo ala pi poki ilo ni. ilo LBTAS li pana e nimi, e mute ale pi pana; kipisi sona li pana e ken pi toki sin. ma ilo pi kepeken li kama jo e nasin nanpa, taso ona li jo ala e linja pi toki utala pi ken toki sin la ona li pali ala e toki awen.

## ijo pi tenpo lili en wile sona pi pini ala

- **kulupu nanpa lukin pi ilo pali ale (golden vectors) li wile, li lupa awen ala lon tenpo ni.** sama pi ilo pali tu tu li lawa pi toki; lukin pi jan li wawa e ona. lukin ni li toki awen pi mi mute: kulupu nanpa lukin pi jan ale li pakala e ilo CI lon tenpo pi tawa ante (nasin pi poki lipu pi nasin insa). ona li lon ala la lukin pi jan taso li wawa e sama, la sitelen li toki e ni.
- **ken pi toki sin tawa jan lawa pi utala** li pakala pi poka tu sama (symmetry breach) pi nasin JFA, li jo e nimi — jan li kama jo e pana nanpa, taso ona li ken ala toki sin. ona li lawa e kipisi pi toki utala lon ma ilo pi kepeken; poki ilo ni o len ala e ona kepeken nasin pi pana nanpa pi ken ala toki sin.
- **nasin pi kule pi linja jan** (trade / adjudication-conduct / verdict-satisfaction) li lon ni kepeken mute ale pi pana pi kulupu wan wan taso; nasin ale pi linja jan pi kule li lawa lon kipisi sona pi ma ilo pi kepeken.

## toki pi ijo wile

poki ilo pi pini linja (leaf library): ona li wile ala e ilo insa (coordinator), e lupa lukin (front end), e ilo pali pi kipisi sona. esun pi kepeken li wile e ona; ona li wile ala e esun ni.

## toki pi ilo LBTAS taso (lon pini, tan nasin pi nanpa toki)

esun wan wan li kama jo e ona lon kipisi esun en sona. ma ilo pi kepeken li awen e nanpa pi ilo pana (released version); nasin v2 pi mute ale pi pana li nanpa anpa tawa kama jo sin ale.
