> Traducción comunitaria (borrador) — Política P2-002 de NTARI, Difusión Multilingüe Global. Fuente: CONFORMANCE.md (original en inglés, instantánea del 2026-10-05). Borrador comunitario asistido por máquina, pendiente de revisión por mantenedores regionales conforme a P2-002 §3.1. Las especificaciones técnicas centrales permanecen en inglés conforme a §2.2.
>
> ¿Encontraste un error en esta traducción? Tu corrección es una contribución
> bienvenida y valorada: haz un fork del repositorio y abre un pull request en
> https://github.com/NTARI-RAND/Leveson-Based-Trade-Assessment-Scale.

> **El original en inglés es normativo.** Esta traducción se ofrece para lectura, no para interpretación: donde difiera de `CONFORMANCE.md`, rige el inglés. Las palabras clave normativas (MUST, MUST NOT, SHOULD, SHOULD NOT, MAY), los nombres de campos, las etiquetas y los identificadores se mantienen en inglés porque constituyen el contrato de conformidad.

# Conformidad — Janus-Facing Architecture

La autodescripción del repositorio en los propios términos de la arquitectura, expuesta **antes** de cualquier cosa específica del producto, según la regla de orden de la arquitectura. Cada afirmación de conformidad está vinculada al mecanismo y a la verificación que la hacen cumplir; de lo contrario, se etiqueta como suplencia. La prosa no vinculada es marketing.

La arquitectura es **Janus-Facing Architecture (JFA)**: el documento de arquitectura unificada de NTARI, documentación libre bajo el bien común AGPL-3.0 del proyecto.

## Declaración de rol

LBTAS es la **escala de evaluación** de la **capa de pacto** de JFA: la reputación como una promesa permanente de no causar daño, llevada como una distribución completa — nunca como una puntuación. La lógica es la del ingeniero de seguridad (Leveson): el daño es un evento discreto que debe hacerse visible, no una cantidad que deba suavizarse; dos accidentes en setenta y tres vuelos dejan en tierra a toda la flota. La escala es de dominio general: una economía consumidora la adopta y la interpreta en su contexto.

| Término de este repositorio | Rol en la arquitectura |
|---|---|
| La escala ordinal de 6 niveles (−1..+4) | el vocabulario de calificación cargado de significado del pacto; **−1 es el incumplimiento mismo** |
| `{distribution, total}` | la reputación llevada tal como la arquitectura lo exige: el conteo en cada nivel junto al total |
| Calificación bidireccional | simetría del pacto entre contrapartes |
| Distribuciones por categoría | lecturas acotadas a la relación (nunca colapsadas en una sola cifra) |

## Invariantes y sus vínculos — a la fecha de `main` (v2.0.0)

| Invariante (arquitectura) | Mecanismo aquí | Verificación |
|---|---|---|
| La reputación MUST NOT promediarse en una puntuación | La API de lectura de v2.0.0 devuelve `{distribution, total}` por categoría; `system_average`, `category_averages` y las listas de participantes ordenadas por promedio se han **eliminado** | CHANGELOG 2.0.0 (cambio incompatible); el comentario sobre la unidad de reputación en el código; no existe ninguna ruta de promediado a la que llamar |
| La **calificación más baja es el incumplimiento mismo** | −1 ("No Trust") es un evento de daño discreto que se mantiene permanentemente visible en la distribución, junto a cualquier volumen | Forma de la distribución; no existe aritmética de cancelación |
| El pacto es **simétrico** entre contrapartes | Bidireccional por diseño: un intercambio puede producir dos calificaciones, productor↔consumidor, con la misma escala en ambos sentidos | Definición de la escala; API |
| La escala es **cargada de significado, ordinal** — no un eje continuo | Cada nivel lleva una definición específica; enteros −1..+4 | Tabla canónica de CLAUDE.md; validación |
| La reputación determina **si**, nunca **cuánto** | La biblioteca no deriva de la distribución ningún límite de crédito, peso ni techo — no existe tal API | Superficie de la API |
| **No portable por defecto** | Datos por plataforma; la biblioteca no tiene identidad entre plataformas ni ruta de importación | Superficie de la API |
| **Diversidad observacional entre implementaciones** | Cuatro implementaciones de referencia (Go, Python, Rust, TypeScript) que deben mantenerse en paridad — codificaciones independientes de un mismo comportamiento | Regla de paridad de CLAUDE.md; ver suplencias |

## Deliberadamente fuera de alcance

La mecánica de impugnación — presentación de reclamos, adjudicación, desestimación como anotación, el sello — pertenece a las **capas de registro y de disputas** de la plataforma consumidora, no a esta biblioteca. LBTAS aporta el vocabulario y la distribución; el registro aporta la rendición de cuentas. Una plataforma consumidora que adopta la escala sin una canalización de reclamos con rendición de cuentas no ha implementado el pacto.

## Suplencias y residuos abiertos

- **Los vectores de referencia (golden vectors) entre implementaciones son un objetivo, todavía no una compuerta.** La paridad entre las cuatro implementaciones es una regla declarada que se hace cumplir mediante revisión; un conjunto compartido de vectores que haga fallar la CI ante una deriva (el patrón del repositorio del protocolo) es la verificación comprometida. Hasta que exista, la paridad se hace cumplir mediante revisión y se etiqueta como tal.
- **La rendición de cuentas de quien adjudica** es la ruptura de simetría que la arquitectura nombra explícitamente — una parte calificada que no tiene a quién responder. Es vinculante para las capas de disputas de las plataformas consumidoras; esta biblioteca no debe disimularla exponiendo ninguna ruta de calificación sin rendición de cuentas.
- **El tipado de relaciones** (comercio / conducta en la adjudicación / satisfacción con el veredicto) se lleva aquí solo como distribuciones por categoría; la disciplina completa de relaciones tipadas es vinculante en la capa de registro de las plataformas consumidoras.

## Declaración de dependencias

Una biblioteca hoja: sin dependencia de ningún coordinador, interfaz de usuario ni implementación de registro. Las economías consumidoras dependen de ella; ella no depende de ninguna.

## Notas específicas del producto (al final, según la regla de orden)

Se adopta por economía en el nivel económico. Las plataformas consumidoras fijan una versión publicada; el modelo de distribución v2 es el piso para cualquier nueva adopción.
