> Traduction communautaire (brouillon) — politique NTARI P2-002, Diffusion multilingue mondiale. Source : SPEC.md (original anglais, instantané du 2026-10-05). Brouillon communautaire assisté par machine, en attente de relecture par le mainteneur régional conformément à P2-002 §3.1. Les spécifications techniques essentielles restent en anglais conformément au §2.2.
>
> Vous avez remarqué une erreur de traduction ? N'hésitez pas à la corriger
> vous-même : forkez le dépôt https://github.com/NTARI-RAND/Leveson-Based-Trade-Assessment-Scale et
> ouvrez une pull request. Les corrections de traduction sont des
> contributions précieuses, tout autant que le code.

> L'original anglais est normatif. Cette traduction est proposée pour la lecture, non pour l'interprétation : là où elle diverge de `SPEC.md`, l'anglais fait foi. Les mots-clés normatifs (MUST, MUST NOT, SHOULD, SHOULD NOT, MAY), les noms de champs, les libellés et les identifiants sont conservés en anglais, car ils constituent le contrat de conformité.

# Spécification LBTAS — la réputation comme pacte, non comme score

**Network Theory Applied Research Institute**
Identifiant du document : P3-014 · Version : 0.1 (brouillon) · Juin 2026
*Spécification normative de la Leveson-Based Trade Assessment Scale. Document compagnon de
P3-011 v2 (Janus Facing Applications), P3-012 (Agrinet Protocol Specification) et
P3-013 (Mycelium). Soumise à* Janus-Facing Architecture *(guide du concepteur, v2.0) et à*
Building JFA Software *(v1.0).*

Les mots-clés **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT** et **MAY** sont employés
au sens de la RFC 2119.

---

## 0. Ce qu'est LBTAS

LBTAS est la **couche pair / réputation** d'un réseau Janus-Facing Architecture. C'est un
**pacte** — une promesse permanente de ne pas nuire — **et non un score**. Sa logique est celle de
l'ingénieure en sécurité (Nancy Leveson) : deux accidents en soixante-treize vols clouent la flotte au sol.
Le volume est un signal, mais aucune quantité de bonnes notes ne dissout un préjudice dans une
moyenne rassurante.

Ici, la réputation est binaire là où cela compte : un membre est **en règle** ou **en
manquement**. La note la plus basse de l'échelle, un `−1`, **est le manquement lui-même** — et non un débit
sur un total cumulé.

Ce document définit l'échelle, le modèle de lecture et les invariants que toute implémentation
conforme MUST respecter. Le README expose la justification ; ce fichier expose les
exigences. Les implémentations de référence (`lbtas.py`, `.ts`, `.go`, `.rs`) y sont
soumises.

---

## 1. L'échelle

Une note est un entier sur une **échelle à six niveaux**, de `−1` à `+4` :

| Valeur | Libellé | Signification |
|---|---|---|
| `+4` | Delight | Anticipe l'évolution des pratiques et des préoccupations de l'utilisateur après la transaction. |
| `+3` | No Negative Consequences | Conçu pour prévenir les pertes ; dépasse la qualité de base. |
| `+2` | Basic Satisfaction | Satisfait à des normes socialement acceptables qui vont au-delà des demandes formulées. |
| `+1` | Basic Promise | Satisfait à toutes les demandes formulées, sans plus. |
| `0` | Cynical Satisfaction | Remplit une promesse de base avec peu ou pas de discipline orientée vers la satisfaction. |
| `−1` | No Trust | L'utilisateur a subi un préjudice, a été exploité, ou a reçu un produit/service sans aucune discipline ou avec une intention malveillante. |

`−1` est catégoriquement distinct de `0…+4` : la bande positive évalue la *qualité* ; `−1`
consigne un *préjudice*. Les implémentations MUST traiter `−1` comme un manquement, jamais comme « un cran sous zéro ».

---

## 2. Une distribution, jamais une moyenne

Une réputation est une **distribution** : le décompte des notes à chaque niveau (`−1, 0, +1, +2,
+3, +4`) à côté du total.

- Une implémentation **MUST NOT** calculer ni exposer une moyenne, une moyenne arithmétique, un score pondéré ou
  toute réduction des notes à un seul chiffre, où que ce soit dans une lecture, un rapport, un badge ou une API.
- Le volume se tient *à côté* du préjudice ; il ne l'annule jamais. Un préjudice reste visible en permanence à côté
  du volume.
- Les lectures **SHOULD** exposer aussi le **nombre de transactions** et l'**ancienneté** (horodatages de la première et de la dernière
  note) : le nombre et l'ancienneté sont eux-mêmes des signaux de confiance.

Un test de conformité : rechercher dans l'implémentation toute division d'une somme de notes par un
décompte, ou tout champ nommé `score`/`average`/`rating` qui écrase la distribution. Une
implémentation correcte n'en contient aucun. (Les implémentations de référence en font une erreur levée là où un
score serait sinon calculé.)

---

## 3. Circonscrite au rôle

La réputation est tenue **séparément pour chaque rôle** — la qualité en laquelle la partie notée a agi
(p. ex. `market_seller`/`market_buyer`, `service_provider`/`service_client`,
`plan_producer`/`plan_backer`), dérivée du type d'échange et du côté de la partie
notée. Un `−1` obtenu dans un rôle **MUST NOT** contaminer la distribution d'un autre. Une
même personne peut détenir simultanément plusieurs réputations circonscrites à un rôle.

---

## 4. Le préjudice s'accompagne d'un récit ; le préjudice n'est jamais masqué

- Un `−1` **MUST** s'accompagner d'un **récit justificatif de ≤ 500 mots**. Un `−1` sans
  récit est invalide et MUST être rejeté.
- Le récit est **local à l'opérateur** : conservé au frontend, référencé (non transporté) par
  l'enregistrement du protocole, **jamais** ancré dans le registre des communs, **jamais** fédéré, et
  lu uniquement par les parties propres à l'enregistrement et par l'arbitre de l'opérateur (P3-013 §6).
- L'**événement** de notation est **immuable et en ajout seul**. Il n'y a ni mise à jour ni suppression.
- Un **rejet annote, il n'efface jamais** (§6) : il retire l'événement de la distribution de confiance
  *active*, mais l'événement reste visible en aval, annoté de **qui l'a
  rejeté et pourquoi**. Un frontend **MAY** pardonner un préjudice ; il **MUST NOT** être en mesure de
  le masquer.

---

## 5. Symétrique — contestable dans les deux sens

Le pacte s'applique **dans les deux sens**. Le `−1` attribué par un producteur à un consommateur est **aussi contestable que**
l'inverse.

- Toute partie notée **MAY** contester une note la concernant, dans **l'un ou l'autre** sens.
- Le système **MUST NOT** encoder qu'une catégorie (p. ex. les vendeurs) est digne de confiance et que
  l'autre (p. ex. les acheteurs) représente le risque. Il n'existe aucun sens privilégié.
- La non-livraison est elle-même un préjudice et relève du pacte (voir le §8 pour ce qui n'en relève *pas*).

---

## 6. Arbitrage : rejeter = annoter

Un arbitre (un rôle **local à l'opérateur**, jamais une autorité globale sur les communs)
**MAY** rejeter une note jugée de mauvaise foi.

- Un rejet est consigné sous la forme d'une **nouvelle annotation**, jamais d'une modification ou d'une suppression (§4, P3-013
  §7). L'événement rejeté et l'annotation sont tous deux permanents et tous deux visibles.
- Une lecture calcule la distribution **active** *en excluant* les événements rejetés, tout en
  **faisant remonter chaque événement rejeté** avec la partie qui l'a rejeté et le motif et, pour une
  note contestée mais maintenue, le fait qu'elle a été maintenue.

---

## 7. Les valeurs par défaut à expiration du délai sont marquées

Lorsqu'un échange s'achève mais qu'une partie ne note pas dans sa **fenêtre de notation**, le
système attribue une **note par défaut de `+2`** (« Basic Satisfaction ») : le silence est interprété comme un
échange qui s'est terminé sans plainte — **non** comme un éloge, et **non** comme un préjudice.

- Une valeur par défaut à expiration du délai **MUST** être **attribuée au système** (`rater_role = system`) et
  **marquée comme valeur par défaut à expiration du délai**.
- Elle **MUST** être **distinguable dans la distribution** d'une note affirmée par une partie, dans chaque
  lecture (comme l'est un rejet), afin qu'une réputation construite en partie sur le silence ne soit jamais confondue
  avec une réputation construite sur l'affirmation. Les lectures **SHOULD** faire apparaître un décompte `defaulted`.
- `+2` est la valeur par défaut prudente (elle ne gonfle pas la réputation) ; `+3` est
  l'alternative documentée. C'est la seule constante réglable de l'échelle.

---

## 8. Détermine si, non combien

LBTAS détermine **si** un membre transige ou non sur la base de la confiance — **jamais combien**.

- Ce que le pacte garantit, c'est **l'honnêteté, non la capacité** : « je ne te nuirai pas » ne signifie pas « je
  peux livrer ce que j'ai promis ».
- **Borner la taille** d'un engagement qu'un acteur honnête peut prendre relève d'une **limite**, qui
  appartient à la **couche Économie**, et non à LBTAS. La limite **MUST** être dérivée de
  quelque chose d'*autre* que la distribution des préjudices (volume sans incident, capacité déclarée, une ligne
  de départ uniforme).
- Une implémentation **MUST NOT** dériver une limite ou un plafond de dépense/de crédit de la distribution
  LBTAS. Laisser le fait d'être en règle acheter un plafond plus élevé transforme la distribution des préjudices
  en score de crédit — la banque par la porte de service. Le pacte garde la porte ; la
  limite dimensionne la pièce ; il faut les maintenir séparés.

---

## 9. Relation avec le règlement

Là où LBTAS conditionne la libération d'un séquestre (P3-012 §7) : la note du consommateur est le déclencheur
de la libération. Une note `0…+4` libère les fonds retenus ; un `−1` **ne libère pas** — il gèle les fonds
et ouvre un audit. La note attribuée a posteriori par un producteur au consommateur ne déplace aucun argent. Il s'agit d'une
règle de *règlement* qui consomme LBTAS ; elle ne fait pas partie de l'échelle elle-même.

---

## 10. Garanties et non-garanties

**Garanties.** Une LBTAS conforme fait remonter le préjudice de manière permanente et visible, ne le fait jamais disparaître
dans une moyenne, le maintient circonscrit au rôle, rend chaque affirmation susceptible de réponse dans les deux sens, et
distingue les notes affirmées du silence et des rejets.

**Non-garanties.** LBTAS atteste **l'honnêteté, non la capacité** (§8), et n'atteste pas
l'honnêteté du calcul qui a produit un échange (un appariement ou un prix truqué) — cela
est hors périmètre, vérifié uniquement par la lisibilité et par une sortie peu coûteuse (P3-013 §9).

---

## 11. Conformité

Une implémentation est conforme si et seulement si **toutes** les conditions suivantes sont remplies :

1. Les notes sont des entiers `−1…+4` ; `−1` est traité comme un manquement, non comme un score faible (§1).
2. La réputation est exposée **uniquement** sous forme de distribution — aucune moyenne, moyenne arithmétique ou score unique
   où que ce soit (§2).
3. La réputation est **circonscrite au rôle** (§3).
4. Un `−1` exige un récit de ≤ 500 mots ; le récit est local à l'opérateur et ne figure jamais dans
   les communs (§4).
5. Les événements de notation sont en ajout seul ; les rejets **annotent, n'effacent jamais**, et restent
   visibles (§4, §6).
6. Le pacte est **symétrique** — contestable dans les deux sens, sans catégorie privilégiée
   (§5).
7. Les valeurs par défaut à expiration du délai sont `+2`, **attribuées au système et marquées**, distinguables dans la
   distribution (§7).
8. Aucune limite ni aucun plafond n'est dérivé de la distribution — elle **détermine si, non
   combien** (§8).

---

## 12. État de l'implémentation (informatif)

| Élément | État |
|---|---|
| Échelle à six niveaux, libellés (§1) | **Implémenté** (`lbtas.py`/`.ts`/`.go`/`.rs` ; README) |
| Distribution, jamais moyennée (§2) | **Implémenté** (implémentations de référence ; Agrinet `services/lbtas.js` + `utils/reputation.js` lève une erreur si un score est demandé) |
| Circonscrite au rôle (§3) | **Implémenté dans Agrinet** (`ratingRepository.getUserReputation` par rôle) ; **écart :** intégrer la circonscription au rôle dans les implémentations de référence autonomes |
| Récit `−1` ≤ 500 mots, local à l'opérateur (§4) | **Implémenté dans Agrinet** (`rating_narratives`) ; **écart :** documenter dans les implémentations de référence |
| En ajout seul ; rejeter = annoter (§4, §6) | **Implémenté dans Agrinet** (`voidById`/`upholdContest`, rejets remontés) ; **écart :** implémentations de référence |
| Contestation symétrique (§5) | **Implémenté dans Agrinet** (`contestRating` dans les deux sens) |
| Valeur par défaut à expiration `+2`, marquée (§7) | **Implémenté dans Agrinet** (`applyRatingTimeouts`, décompte `defaulted`) |
| Détermine si, non combien (§8) | **Conforme par absence** — aucune limite dérivée des notes n'existe nulle part |

Les implémentations de référence autonomes présentes ici couvrent l'échelle et la distribution
fidèlement ; le cycle de vie du pacte (circonscription au rôle, récit, contestation/rejet, valeur par défaut
à expiration) est actuellement le plus complet dans le backend d'Agrinet et est en cours de réintégration
dans les implémentations de référence. Voir [CONFORMANCE.md](CONFORMANCE.md) pour la matrice par
implémentation (auditée : aucune violation ; la circonscription au rôle est le seul écart au niveau du code dans les
implémentations autonomes).

---

*Network Theory Applied Research Institute, Inc. — 501(c)(3) — info@ntari.org*
*Documentation libre relevant des communs AGPL-3.0 du projet — faite pour être lue, réimplémentée et contestée.*
