# lipu lawa LBTAS — sona pi jan li toki awen, li nanpa ala (toki pona)

> **toki lili pi lipu ni:** lipu ni li lipu pi kulupu, li tan nasin NTARI "P2-002". lipu suli li lipu Inli "SPEC.md" (tenpo pi 2026-10-05). ilo sona li pali e lipu ni; kulupu li wile lukin e ona kepeken nasin "P2-002" kipisi "3.1".
>
> **Note:** This is a community rendering under NTARI policy P2-002. The complete document is the English original SPEC.md (snapshot 2026-10-05). Machine-assisted draft pending community review per P2-002 section 3.1.
>
> sina lukin e pakala lon toki ni la o pona e ona: o pali e "fork" lon
> https://github.com/NTARI-RAND/Leveson-Based-Trade-Assessment-Scale, o pana e
> "pull request". pana sina li pona tawa mi mute.
>
> **lipu Inli li lawa.** lipu ni li tawa lukin, li tawa ala sona pi nasin lawa: lipu ni li ante tan `SPEC.md` la lipu Inli li lawa. nimi lawa (MUST, MUST NOT, SHOULD, SHOULD NOT, MAY), nimi pi poki sona, nimi sitelen en nimi ilo li awen lon toki Inli, tan ni: ona li lipu lawa pi nasin sama.

---

**kulupu Network Theory Applied Research Institute**
nimi lipu: P3-014 · nanpa: 0.1 (lipu pi pini ala) · mun nanpa 6 pi tenpo 2026
*lipu lawa pi nasin Leveson-Based Trade Assessment Scale. ona li poka e lipu
P3-011 v2 (Janus Facing Applications), e lipu P3-012 (Agrinet Protocol Specification), e lipu
P3-013 (Mycelium). ona li awen lon nasin pi lipu* Janus-Facing Architecture *(lipu pi jan pali, v2.0) en lipu*
Building JFA Software *(v1.0).*

nimi lawa **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT**, en **MAY** li kepeken
sama lipu RFC 2119.

---

## 0. nasin LBTAS li seme

nasin LBTAS li **kipisi pi jan sama / pi sona jan** lon kulupu ilo pi nasin Janus-Facing Architecture. ona li
**toki awen** — toki pi tenpo ale pi ni: "mi ike ala e sina" — **ona li nanpa ala**. nasin sona ona li nasin pi
jan sona pi awen jan (jan Nancy Leveson): tomo waso li pakala tu lon tawa 73 la tomo waso ale pi kulupu ni li awen lon ma.
mute li toki e sona, taso pana pona li mute seme la, ona li ken ala weka e ike wan, li ken ala ante e ona tawa nanpa meso pona.

lon ni, sona pi jan li jo e nasin tu taso lon ijo suli: jan kulupu li **lon nasin pona** anu **lon pakala pi
toki awen**. pana nanpa anpa pi nasin nanpa, `−1`, **li pakala sama** — ona li weka lili ala tan nanpa ale pi
tenpo ale.

lipu ni li toki e nasin nanpa, e nasin lukin (read model), e nasin awen pi ante ala: ilo pali ale pi nasin sama
li MUST awen e ona. lipu README li jo e tan; lipu ni li jo e wile. ilo pi lipu lawa (reference implementations: `lbtas.py`, `.ts`, `.go`, `.rs`) li awen lon
lipu ni.

---

## 1. nasin nanpa

pana nanpa li nanpa ale (integer) lon **nasin nanpa pi nanpa 6**, tan `−1` tawa `+4`:

| nanpa | nimi | kon |
|---|---|---|
| `+4` | Delight | ona li sona lon tenpo open e ante kama pi nasin pali en pilin pi jan kepeken, lon tenpo kama pi esun pini. |
| `+3` | No Negative Consequences | jan li pali e ona tawa ni: jan li weka ala e ijo; pona ona li suli tawa pona open. |
| `+2` | Basic Satisfaction | nasin pona pi kulupu li suli tawa wile toki; ona li pona tawa nasin ni. |
| `+1` | Basic Promise | ona li pana e wile toki ale, li pana ala e ijo ante. |
| `0` | Cynical Satisfaction | ona li pali e toki pana lili, taso ona li pali lili anu pali ala tawa pilin pona. |
| `−1` | No Trust | jan kepeken li kama ike, anu jan li kepeken ike e ona, anu ona li kama jo e ijo/pali pi pali pona ala anu pi wile ike. |

`−1` li ante mute tan `0…+4`: kipisi pona li lukin e *pona pi ijo*; `−1` li awen e sona pi
*ike*. ilo pali li MUST lukin e `−1` sama pakala pi toki awen, li lukin ala e ona sama "wan anpa ala" lon tenpo ale.

---

## 2. mute ale pi pana, li nanpa meso ala lon tenpo ale

sona pi jan li **mute ale pi pana**: mute pi pana nanpa lon nanpa ale (`−1, 0, +1, +2,
+3, +4`) lon poka pi mute ale.

- ilo pali li **MUST NOT** pali anu pana e nanpa meso (average, mean), e nanpa meso pi suli ante (weighted score),
  e nasin ante ale pi ante e pana nanpa tawa nanpa wan taso, lon ma ale: lon lukin, lon lipu pana, lon sitelen lili (badge), lon API.
- mute li lon *poka* pi ike; ona li weka ala e ike lon tenpo ale. ike li awen lon lukin lon tenpo ale, lon poka
  pi mute.
- lukin li **SHOULD** pana kin e **nanpa esun** e **tenpo lon** (tenpo pi pana nanpa nanpa wan / pini):
  nanpa en tenpo lon li toki kin e sona pi pilin pona.

lukin pi nasin sama: o alasa lon ilo pali e ni: nanpa ale pi pana nanpa li kipisi kepeken nanpa mute anu seme? poki sona
pi nimi `score`/`average`/`rating` li wan e mute ale pi pana anu seme? ilo pali pona li jo ala e ona.
(ilo pi lipu lawa li pana e pakala (throwing error) lon ma ni: ilo ante li pali e nanpa wan lon ma ni.)

---

## 3. kipisi tan pali jan

sona pi jan li awen **kipisi tan pali jan** — ni li pali pi jan pi kama jo e pana nanpa lon esun
(sama `market_seller`/`market_buyer`, `service_provider`/`service_client`,
`plan_producer`/`plan_backer`), li kama tan nasin pi esun en tan poka pi jan ni.
`−1` lon pali wan li **MUST NOT** jaki e mute ale pi pana pi pali ante. jan wan li ken jo e sona jan
mute pi kipisi tan pali jan lon tenpo sama.

---

## 4. ike li jo e toki; ike li len ala lon tenpo ale

- `−1` li **MUST** jo e **toki pi nimi ≤ 500**, li toki e tan ona. `−1` li jo ala e
  toki la ona li pona ala, la ilo li MUST weka e ona.
- toki li **lon ma ilo pi kepeken taso**: ona li awen lon lupa lukin; lipu pi nasin insa li toki e nimi ona
  (li jo ala e ona); ona li lon **ala** lon lipu suli pi jan ale lon tenpo ale; ona li tawa **ala** ma ilo ante lon tenpo ale;
  jan pi lipu ni taso en jan lawa pi utala pi ma ilo pi kepeken li ken lukin e ona (P3-013 §6).
- **ijo** pi pana nanpa li **ante ala, li kama sin taso**. ante li lon ala, weka li lon ala.
- **weka li pana e toki poka, li weka ala e ijo** (§6): ona li weka e ijo tan mute ale pi pana *lon tenpo ni*,
  taso ijo li awen lon lukin lon monsi, li jo e toki poka pi **jan seme li weka e ona, li weka tan seme**.
  lupa lukin li **MAY** weka e pilin ike tan ike; ona li **MUST NOT** ken len e ike.

---

## 5. sama tawa poka tu — jan pi poka tu li ken utala

toki awen li **tawa poka tu**. jan pali li pana e `−1` tawa jan kepeken la jan li **ken utala e ona sama**
nasin ante.

- jan ale pi kama jo e pana nanpa li **MAY** utala e pana nanpa tawa ona, lon poka **wan anu poka ante**.
- ilo li **MUST NOT** toki e ni: kulupu wan (sama jan esun) li pona tawa pilin, kulupu ante (sama jan kama jo) li ken ike.
  poka pi wawa suli li lon ala.
- pana ala li ike kin, li lon toki awen (o lukin e §8 tan ijo pi lon *ala*).

---

## 6. jan lawa pi utala: weka = toki poka

jan lawa pi utala (pali **lon ma ilo pi kepeken taso** — ona li jan lawa pi ma ale ala lon poki pi jan ale lon tenpo ale)
li **MAY** weka e pana nanpa, ona li sona e ni: pana ni li tan wile ike.

- weka li awen sama **toki poka sin**, li ante ala, li weka ala (§4, P3-013
  §7). ijo weka en toki poka li awen lon tenpo ale, li lon lukin.
- lukin li pali e mute ale pi pana **lon tenpo ni**, *li weka e* ijo weka, taso ona li
  **pana kin e ijo weka ale** lon lukin, e jan pi weka ona, e tan ona; pana nanpa li kama utala, li awen la
  lukin li pana e ni: ona li awen.

---

## 7. nanpa open pi pini tenpo li jo e sitelen

esun li pini, taso jan li pana ala e nanpa lon **tenpo pana** ona la ilo li pana e **nanpa open `+2`**
("Basic Satisfaction"): kalama ala li sama esun pini pi toki ike ala — ona li toki pona **ala**, li ike **ala**.

- nanpa open pi pini tenpo li **MUST** tan **ilo** (`rater_role = system`), li **MUST** jo e sitelen pi
  **nanpa open pi pini tenpo**.
- ona li **MUST** ken **ante lon mute ale pi pana** tan pana nanpa pi jan toki, lon lukin
  ale (sama weka). ni la, sona jan li kama lili tan kalama ala la, jan li ken ala pakala, li ken ala pilin e ni: ona li kama tan toki lon.
  lukin li **SHOULD** pana e nanpa `defaulted`.
- `+2` li nanpa open pi awen (ona li suli ala e sona pi jan); `+3` li nasin ante pi lipu. ni taso li nanpa pi ken
  ante lon nasin nanpa.

---

## 8. ona li toki e ken anu ken ala, li toki ala e mute

nasin LBTAS li lawa e ni taso: jan kulupu li ken esun kepeken pilin pona **anu seme** — ona li lawa **ala e mute** lon tenpo ale.

- toki awen li awen e **toki lon, li awen ala e ken pali**: "mi ike ala e sina" li sama ala "mi
  ken pana e ijo pi toki mi."
- jan pi toki lon li ken kama jo e toki pana pi suli seme? **selo pi suli ni** li **sewi pini**, li lon **kipisi esun en sona**, li lon ala nasin LBTAS.
  sewi pini li **MUST** kama tan ijo *ante* tan mute ale pi pana ike (mute esun pona, ken pali pi toki jan, linja
  open sama).
- ilo pali li **MUST NOT** kama jo e sewi pini pi mani pana / mani pi kama jo (credit) tan mute ale pi pana
  LBTAS. nasin pona li ken esun e sewi pini suli la mute ale pi pana ike li kama nanpa ken mani (credit score)
  — tomo mani li kama insa kepeken lupa monsi. toki awen li lawa e lupa; sewi pini li lawa e suli pi tomo; o awen e ona tu lon kipisi ante.

---

## 9. linja tawa pini esun

nasin LBTAS li lawa e pana pi mani awen la (P3-012 §7): pana nanpa pi jan kepeken li open e pana mani.
`0…+4` li pana e mani awen; `−1` li pana **ala** — ona li awen e mani, li open e lukin pi lipu mani.
jan pali li pana e nanpa tawa jan kepeken lon monsi la mani li tawa ala. ni li nasin *pi pini esun*; ona li
kepeken nasin LBTAS, li kipisi ala pi nasin nanpa.

---

## 10. ijo awen en ijo awen ala

**ijo awen.** nasin LBTAS pi nasin sama li pana e ike lon lukin lon tenpo ale, li weka ala e ike kepeken nanpa meso,
li awen e ike lon kipisi tan pali jan, li ken e utala lon poka tu tawa toki ale, li ante e pana nanpa pi jan toki
tan kalama ala en tan weka.

**ijo awen ala.** nasin LBTAS li toki e **toki lon, li toki ala e ken pali** (§8), li toki ala e toki lon pi
nasin nanpa (computation) pi pali esun (sama: jan li ike e kama wan pi esun anu e mani esun) — ni li lon ala pali
pi lipu ni; jan li lukin e ona kepeken ken lukin pona en weka pi pali lili taso (P3-013 §9).

---

## 11. nasin sama

ilo pali li lon nasin sama la ijo ni **ale** li lon (iff):

1. pana nanpa li nanpa ale `−1…+4`; jan li lukin e `−1` sama pakala pi toki awen, li lukin ala e ona sama nanpa lili (§1).
2. sona pi jan li lon lukin sama mute ale pi pana **taso** — nanpa meso li lon ala, nanpa wan taso li lon ala,
   lon ma ale (§2).
3. sona pi jan li **kipisi tan pali jan** (§3).
4. `−1` li wile e toki pi nimi ≤ 500; toki li lon ma ilo pi kepeken taso, li lon ala lon poki pi jan ale lon
   tenpo ale (§4).
5. ijo pi pana nanpa li kama sin taso; weka li **pana e toki poka, li weka ala e ijo**, li awen
   lon lukin (§4, §6).
6. toki awen li **sama tawa poka tu** — jan li ken utala lon poka tu, kulupu pi wawa suli li lon ala
   (§5).
7. nanpa open pi pini tenpo li `+2`, li **tan ilo, li jo e sitelen**, li ken ante lon mute ale pi
   pana (§7).
8. sewi pini ala li kama tan mute ale pi pana — ona li **toki e ken anu ken ala, li toki ala e
   mute** (§8).

---

## 12. lon pi ilo pali (sona taso, lawa ala)

| ijo | lon |
|---|---|
| nasin nanpa pi nanpa 6, nimi (§1) | **lon ilo** (`lbtas.py`/`.ts`/`.go`/`.rs`; README) |
| mute ale pi pana, li nanpa meso ala lon tenpo ale (§2) | **lon ilo** (ilo pi lipu lawa; ilo Agrinet `services/lbtas.js` + `utils/reputation.js` li pana e pakala (throws) lon tenpo pi wile nanpa) |
| kipisi tan pali jan (§3) | **lon ilo Agrinet** (`ratingRepository.getUserReputation` tawa pali wan wan); **ante (delta):** o pana e kipisi tan pali jan tawa ilo pi lipu lawa pi wan taso |
| toki `−1` pi nimi ≤ 500, lon ma ilo pi kepeken taso (§4) | **lon ilo Agrinet** (`rating_narratives`); **ante (delta):** o toki e ona lon ilo pi lipu lawa |
| kama sin taso; weka = toki poka (§4, §6) | **lon ilo Agrinet** (`voidById`/`upholdContest`, ijo weka li lon lukin); **ante (delta):** ilo pi lipu lawa |
| utala pi poka tu (§5) | **lon ilo Agrinet** (`contestRating` lon poka tu) |
| nanpa open pi pini tenpo `+2`, li jo e sitelen (§7) | **lon ilo Agrinet** (`applyRatingTimeouts`, nanpa `defaulted`) |
| toki e ken anu ken ala, li toki ala e mute (§8) | **sama nasin tan lon ala** — sewi pini tan pana nanpa li lon ala lon ma ale |

ilo pi lipu lawa pi wan taso lon ni li pana pona e nasin nanpa en mute ale pi pana; tenpo ale pi toki
awen (kipisi tan pali jan, toki, utala/weka, nanpa open pi pini tenpo) li pona nanpa wan lon ilo Agrinet insa
(backend) lon tenpo ni, li kama sama sin lon ilo pi lipu lawa. o lukin e [CONFORMANCE.md](CONFORMANCE.md) tawa leko pi ilo pali wan wan
(lukin li pini: pakala li lon ala; kipisi tan pali jan li lupa wan taso pi sitelen ilo lon ilo pi lipu lawa pi wan
taso).

---

*kulupu Network Theory Applied Research Institute, Inc. — 501(c)(3) — info@ntari.org*
*lipu ken pi poki AGPL-3.0 pi jan ale pi ilo ni — ona li tawa lukin, tawa pali sin, tawa utala.*
