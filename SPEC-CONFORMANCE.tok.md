# lipu LBTAS — lipu awen pi nasin sama (toki pona)

> **toki lili pi lipu ni:** lipu ni li lipu pi kulupu, li tan nasin NTARI "P2-002". lipu suli li lipu Inli "SPEC-CONFORMANCE.md" (tenpo pi 2026-10-05). ilo sona li pali e lipu ni; kulupu li wile lukin e ona kepeken nasin "P2-002" kipisi "3.1".
>
> **Note:** This is a community rendering under NTARI policy P2-002. The complete document is the English original SPEC-CONFORMANCE.md (snapshot 2026-10-05). Machine-assisted draft pending community review per P2-002 section 3.1.
>
> sina lukin e pakala lon toki ni la o pona e ona: o pali e "fork" lon
> https://github.com/NTARI-RAND/Leveson-Based-Trade-Assessment-Scale, o pana e
> "pull request". pana sina li pona tawa mi mute.
>
> **lipu Inli li lawa.** lipu ni li tawa lukin, li tawa ala sona pi nasin lawa: lipu ni li ante tan `SPEC-CONFORMANCE.md` la lipu Inli li lawa. nimi lawa (MUST, MUST NOT, SHOULD, SHOULD NOT, MAY), nimi pi poki sona, nimi sitelen en nimi ilo li awen lon toki Inli, tan ni: ona li lipu lawa pi nasin sama.

---

lipu ni li toki e lon pi ilo pali ale tawa lipu [`SPEC.md`](SPEC.md) (P3-014). tan nasin
JFA la lipu ni li pana e lon ni lon open, li pali ala sama jan pi toki ni: "lupa li lon ala."

**lukin:** 2026-07-01, tawa SPEC v0.1. **pini:** pakala pi nasin lawa li lon ala — nanpa
meso li lon ala lon ma ale, nimi sitelen li tawa ala tan nasin ona, sewi pini li kama ala
tan mute ale pi pana ike (harm distribution).

sona pi sitelen: **yes** = ona li lon ilo · **no** = ona li lon ala lon tenpo ni (lon kipisi
pi sitelen ilo) · **app** = ijo pi ilo pi ma ilo pi kepeken (operator-app); lipu li toki e
ona, taso ona li lon ala ilo pi nasin lukin pi wan taso (standalone reference impl).

## leko nanpa

| # | nasin awen (SPEC §) | py | ts | go | rs | Agrinet¹ |
|---|---|:--:|:--:|:--:|:--:|:--:|
| 1 | nasin nanpa −1..+4, li jo e nimi sitelen pi ante ala (§1) | yes | yes | yes | yes | yes |
| 2 | mute ale pi pana, li nanpa meso ala lon tenpo ale (§2) | yes | yes | yes | yes | yes² |
| 3 | sona pi jan li kipisi tan pali jan (§3) | no | no | no | no | yes |
| 4 | −1 li jo e toki ≤500w, li awen lon ma ilo pi kepeken taso (§4) | app | app | app | app | yes |
| 5 | ijo sin taso li kama; weka li pana e toki poka, li weka ala e ijo lon tenpo ale (§4, §6) | app | app | app | app | yes |
| 6 | sama tawa poka tu — jan pi poka tu li ken utala (§5) | app | app | app | app | yes |
| 7 | tenpo li pini la nanpa open li +2; nimi ilo li lon ona, li sitelen e ni (§7) | app | app | app | app | yes |
| 8 | ona li toki e ken anu ken ala, li toki ala e mute (§8) | yes | yes | yes | yes | yes |

¹ ilo Agrinet = `services/lbtas.js` + `repositories/ratingRepository.js` lon `NTARI-RAND/Agrinet`.
² ilo Agrinet li **pana kin e pakala** (throws) lon tenpo ale pi wile ni: jan li wile e nanpa wan taso pi sona jan (`utils/reputation.js`).

## kipisi ale li jo e pali seme

nasin nanpa en nasin lukin pi mute ale pi pana (read-model) li **insa pi nasin pali**
(algorithm core) — ilo pi nasin lukin ale li jo e ona. ilo luka ale li sama lon nimi sitelen
luka wan (Delight, No Negative Consequences, Basic Satisfaction, Basic Promise, Cynical
Satisfaction, No Trust), li tawa ala tan nasin ona.

ijo ante pi tenpo ale pi toki awen (tan open tawa pini) li kipisi lon kipisi ale:

- **lon kipisi pi sitelen ilo, li wile lon ilo pi nasin lukin:** nasin nanpa en mute ale pi pana
  (§1, §2), en **kipisi tan pali jan** (§3). kipisi tan pali jan — ni li kipisi e mute ale
  pi pana tan pali pi jan ni: jan li kama jo e pana nanpa — li nasin awen wan taso pi kipisi
  pi sitelen ilo ni: ona li lon ala ilo pi nasin lukin pi wan taso lon tenpo ni. ona li lon ale lon
  ilo Agrinet, li pona sin ni tawa py/ts/go/rs: jan li lukin awen e ona (tracked).
- **ijo pi ilo pi ma ilo pi kepeken; ni li pona: lipu li *toki* e ona, li pali ala e ona lon
  ilo pi nasin lukin:** toki pi nimi ≤500 en awen ona lon ma ilo pi kepeken taso (§4), ijo pi kama
  sin taso en weka kepeken toki poka (§4, §6), utala tawa poka tu (§5), en nanpa open lon
  pini pi tenpo pana (§7). ijo ni li wile e poki sona, e pali pi jan lawa pi utala, e ilo
  tenpo — ona li lon ma ilo pi kepeken (ilo Agrinet); ma ni li pali e ona ale.

## lupa pi toki lon

- **kipisi tan pali jan lon py/ts/go/rs** — ona li lon ala lon tenpo ni (jan li lukin awen
  e ona). lukin insa li sona ala e pali jan; ma ilo pi kepeken li wile e mute ale pi
  pana tawa pali jan wan wan la ona li pali sama ilo Agrinet.
- ilo pali ale li pali ala e nanpa meso, li pana ala e nanpa wan taso, li kama jo ala e
  sewi pini tan mute ale pi pana ike — pakala pi nasin awen ni li ken pali sin e kulupu pi
  nanpa ken mani (credit bureau); nasin awen ale ni li awen.
