> Traduction communautaire (brouillon) — politique NTARI P2-002, Diffusion multilingue mondiale. Source : CONFORMANCE.md (original anglais, instantané du 2026-10-05). Brouillon communautaire assisté par machine, en attente de relecture par le mainteneur régional conformément à P2-002 §3.1. Les spécifications techniques essentielles restent en anglais conformément au §2.2.
>
> Vous avez remarqué une erreur de traduction ? N'hésitez pas à la corriger
> vous-même : forkez le dépôt https://github.com/NTARI-RAND/Leveson-Based-Trade-Assessment-Scale et
> ouvrez une pull request. Les corrections de traduction sont des
> contributions précieuses, tout autant que le code.

> L'original anglais est normatif. Cette traduction est proposée pour la lecture, non pour l'interprétation : là où elle diverge de `CONFORMANCE.md`, l'anglais fait foi. Les mots-clés normatifs (MUST, MUST NOT, SHOULD, SHOULD NOT, MAY), les noms de champs, les libellés et les identifiants sont conservés en anglais, car ils constituent le contrat de conformité.

# Conformité — Janus-Facing Architecture

L'autodescription du dépôt dans les termes propres à l'architecture, énoncée **avant** tout élément propre au produit, conformément à la règle d'ordre de l'architecture. Chaque affirmation de conformité est rattachée au mécanisme et à la vérification qui la font respecter, ou bien elle est étiquetée comme substitution. Une prose non rattachée n'est que du marketing.

L'architecture est **Janus-Facing Architecture (JFA)** — le document d'architecture unifiée de NTARI, documentation libre relevant des communs AGPL-3.0 du projet.

## Déclaration de rôle

LBTAS est l'**échelle d'évaluation** de la **couche Pacte** de JFA : la réputation comme promesse permanente de ne pas nuire, portée sous la forme d'une distribution complète — jamais d'un score. La logique est celle de l'ingénieure en sécurité (Leveson) : un préjudice est un événement discret à faire remonter, non une quantité à lisser ; deux accidents en soixante-treize vols clouent la flotte au sol. L'échelle est indépendante du domaine : une économie consommatrice l'adopte et l'interprète selon son contexte.

| Terme de ce dépôt | Rôle dans l'architecture |
|---|---|
| L'échelle ordinale à 6 niveaux (−1..+4) | le vocabulaire de notation du pacte, chargé de sens ; **−1 est le manquement lui-même** |
| `{distribution, total}` | la réputation portée comme l'exige l'architecture : le décompte à chaque niveau à côté du total |
| Notation bidirectionnelle | symétrie du pacte entre contreparties |
| Distributions par catégorie | lectures circonscrites à une relation (jamais réduites à un seul chiffre) |

## Invariants et leurs rattachements — à l'état de `main` (v2.0.0)

| Invariant (architecture) | Mécanisme ici | Vérification |
|---|---|---|
| La réputation MUST NOT être moyennée en un score | l'API de lecture v2.0.0 renvoie `{distribution, total}` par catégorie ; `system_average`, `category_averages` et les listes d'acteurs classées par moyenne sont **supprimés** | CHANGELOG 2.0.0 (rupture de compatibilité) ; le commentaire sur l'unité de réputation dans le code ; aucun chemin de calcul de moyenne n'existe à appeler |
| La **note la plus basse est le manquement lui-même** | −1 (« No Trust ») est un événement de préjudice discret, maintenu visible en permanence dans la distribution à côté de tout volume | Forme de la distribution ; aucune arithmétique de compensation n'existe |
| Le pacte est **symétrique** entre contreparties | Bidirectionnel par conception : un même échange peut produire deux notes, producteur↔consommateur, sur la même échelle dans les deux sens | Définition de l'échelle ; API |
| L'échelle est **chargée de sens, ordinale** — et non un axe continu | Chaque niveau porte une définition précise ; entiers −1..+4 | Tableau canonique de CLAUDE.md ; validation |
| La réputation détermine **si**, jamais **combien** | La bibliothèque ne dérive de la distribution aucune limite de crédit, aucun poids ni plafond — aucune API de ce type n'existe | Surface de l'API |
| **Non portable par défaut** | Données propres à chaque plateforme ; aucune identité inter-plateformes ni chemin d'importation dans la bibliothèque | Surface de l'API |
| **Diversité d'observation entre implémentations** | Quatre implémentations de référence (Go, Python, Rust, TypeScript) qui doivent rester à parité — des encodages indépendants d'un même comportement | Règle de parité de CLAUDE.md ; voir les substitutions |

## Délibérément hors périmètre

Les mécanismes de contestation — le dépôt de réclamations, l'arbitrage, le rejet sous forme d'annotation, le sceau — relèvent des **couches de registre et de litige** de la plateforme consommatrice, et non de cette bibliothèque. LBTAS fournit le vocabulaire et la distribution ; le registre fournit la redevabilité. Une plateforme consommatrice qui adopte l'échelle sans chaîne de traitement de réclamations redevables n'a pas implémenté le pacte.

## Substitutions et résidus ouverts

- **Les vecteurs de référence inter-implémentations sont un objectif, pas encore un verrou.** La parité entre les quatre implémentations est une règle énoncée, appliquée par la revue ; une suite de vecteurs partagée qui fait échouer la CI en cas de dérive (le modèle du dépôt du protocole) est la vérification à laquelle le projet s'est engagé. Tant qu'elle n'existe pas, la parité est assurée par la revue et étiquetée comme telle.
- **La redevabilité de l'arbitre** est le manquement à la symétrie nommé par l'architecture — une partie notée sans possibilité de réponse. Elle s'impose aux couches de litige des plateformes consommatrices ; cette bibliothèque ne doit pas la masquer en exposant un quelconque chemin de notation sans réponse possible.
- **Le typage des relations** (échange commercial / conduite de l'arbitrage / satisfaction quant au verdict) n'est porté ici que sous forme de distributions par catégorie ; la discipline complète des relations typées s'impose au niveau de la couche Registre des plateformes consommatrices.

## Déclaration de dépendances

Une bibliothèque feuille : aucune dépendance envers un coordinateur, un frontend ou une implémentation de registre. Les économies consommatrices en dépendent ; elle ne dépend d'aucune d'entre elles.

## Notes propres au produit (en dernier, conformément à la règle d'ordre)

Adoptée économie par économie, au niveau économique. Les plateformes consommatrices épinglent une version publiée ; le modèle de distribution v2 est le plancher pour toute nouvelle adoption.
