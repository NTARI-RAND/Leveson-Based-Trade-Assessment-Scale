> Traduction communautaire (brouillon) — politique NTARI P2-002, Diffusion multilingue mondiale. Source : SPEC-CONFORMANCE.md (original anglais, instantané du 2026-10-05). Brouillon communautaire assisté par machine, en attente de relecture par le mainteneur régional conformément à P2-002 §3.1. Les spécifications techniques essentielles restent en anglais conformément au §2.2.
>
> Vous avez remarqué une erreur de traduction ? N'hésitez pas à la corriger
> vous-même : forkez le dépôt https://github.com/NTARI-RAND/Leveson-Based-Trade-Assessment-Scale et
> ouvrez une pull request. Les corrections de traduction sont des
> contributions précieuses, tout autant que le code.

> L'original anglais est normatif. Cette traduction est proposée pour la lecture, non pour l'interprétation : là où elle diverge de `SPEC-CONFORMANCE.md`, l'anglais fait foi. Les mots-clés normatifs (MUST, MUST NOT, SHOULD, SHOULD NOT, MAY), les noms de champs, les libellés et les identifiants sont conservés en anglais, car ils constituent le contrat de conformité.

# Registre de conformité LBTAS

État de chaque implémentation au regard de [`SPEC.md`](SPEC.md) (P3-014). Conformément à la
méthode JFA, ce document expose l'état tel qu'il est, plutôt que de mettre en scène l'absence d'écart.

**Audité :** le 2026-07-01, au regard de la SPEC v0.1. **Résultat :** aucune violation — aucune moyenne
nulle part, aucune dérive des libellés, aucune limite dérivée de la distribution des préjudices.

Légende : **yes** = implémenté · **no** = pas encore (niveau code) · **app** = relève de l'application
de l'opérateur, documenté mais non implémenté dans une implémentation de référence autonome.

## Matrice

| # | Invariant (§ de la SPEC) | py | ts | go | rs | Agrinet¹ |
|---|---|:--:|:--:|:--:|:--:|:--:|
| 1 | Échelle −1..+4 avec les libellés exacts (§1) | yes | yes | yes | yes | yes |
| 2 | Distribution, jamais une moyenne (§2) | yes | yes | yes | yes | yes² |
| 3 | Réputation circonscrite au rôle (§3) | no | no | no | no | yes |
| 4 | −1 s'accompagne d'un récit ≤500 mots, local à l'opérateur (§4) | app | app | app | app | yes |
| 5 | En ajout seul ; le rejet annote, n'efface jamais (§4, §6) | app | app | app | app | yes |
| 6 | Symétrique — contestable dans les deux sens (§5) | app | app | app | app | yes |
| 7 | Note par défaut +2 à l'expiration du délai, attribuée au système et signalée comme telle (§7) | app | app | app | app | yes |
| 8 | Détermine si, non combien (§8) | yes | yes | yes | yes | yes |

¹ Agrinet = `services/lbtas.js` + `repositories/ratingRepository.js` dans `NTARI-RAND/Agrinet`.
² Agrinet, en outre, **lève une exception** si un score de réputation à chiffre unique est demandé (`utils/reputation.js`).

## Ce dont chaque couche est responsable

L'échelle et le modèle de lecture de la distribution constituent le **cœur algorithmique** — chaque implémentation
de référence les porte, et les cinq s'accordent sur les six libellés (Delight, No Negative
Consequences, Basic Satisfaction, Basic Promise, Cynical Satisfaction, No Trust) sans aucune
dérive.

Le reste du cycle de vie du pacte se répartit par couche :

- **Niveau code, relève d'une implémentation de référence :** l'échelle et la distribution (§1, §2),
  ainsi que la **circonscription au rôle** (§3). La circonscription au rôle — indexer la distribution selon le rôle
  de la partie notée — est le seul invariant de niveau code qui ne figure pas encore dans les implémentations de référence
  autonomes ; elle est entièrement implémentée dans Agrinet et constitue l'amélioration suivie pour py/ts/go/rs.
- **Préoccupations de l'application de l'opérateur, à juste titre *documentées* mais non implémentées dans une implémentation de référence :**
  le récit de ≤500 mots et son stockage local à l'opérateur (§4), les événements en ajout seul avec
  le rejet sous forme d'annotation (§4, §6), la contestation bidirectionnelle (§5) et la note par défaut à l'expiration
  de la fenêtre de notation (§7). Ces éléments exigent un magasin de données, un rôle d'arbitre et une horloge —
  ils relèvent de l'opérateur (Agrinet), qui les réalise tous.

## Écarts reconnus

- **Circonscription au rôle dans py/ts/go/rs** — pas encore implémentée (suivie). Les lectures du cœur sont
  indépendantes du rôle ; un opérateur qui a besoin de distributions par rôle procède comme le fait Agrinet.
- Aucune implémentation ne calcule de moyenne, n'expose de score unique ni ne dérive de limite à partir de la distribution
  des préjudices — les invariants dont la violation reconstruirait l'agence d'évaluation du crédit sont tous respectés.
