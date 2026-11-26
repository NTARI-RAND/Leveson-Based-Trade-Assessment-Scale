> Traducción comunitaria (borrador) — Política P2-002 de NTARI, Difusión Multilingüe Global. Fuente: SPEC-CONFORMANCE.md (original en inglés, instantánea del 2026-10-05). Borrador comunitario asistido por máquina, pendiente de revisión por mantenedores regionales conforme a P2-002 §3.1. Las especificaciones técnicas centrales permanecen en inglés conforme a §2.2.
>
> ¿Encontraste un error en esta traducción? Tu corrección es una contribución
> bienvenida y valorada: haz un fork del repositorio y abre un pull request en
> https://github.com/NTARI-RAND/Leveson-Based-Trade-Assessment-Scale.

> **Precedencia.** El original en inglés es normativo. Esta traducción se ofrece para lectura, no para interpretación: donde difiera de `SPEC-CONFORMANCE.md`, rige el inglés. Las palabras clave normativas (MUST, MUST NOT, SHOULD, SHOULD NOT, MAY), los nombres de campos, las etiquetas y los identificadores se mantienen en inglés porque constituyen el contrato de conformidad.

# Registro de conformidad de LBTAS

Estado de cada implementación frente a [`SPEC.md`](SPEC.md) (P3-014). Conforme al
método de JFA, este documento presenta el estado sin rodeos, en lugar de aparentar que
no existe ninguna brecha.

**Auditado:** 2026-07-01 frente a SPEC v0.1. **Resultado:** ninguna infracción — ningún
promedio en ninguna parte, ninguna deriva de etiquetas, ningún límite derivado de la
distribución de daños.

Leyenda: **yes** = implementado · **no** = aún no (a nivel de código) · **app** = asunto
de la aplicación del operador, documentado pero no implementado en una implementación de
referencia independiente.

## Matriz

| # | Invariante (§ de SPEC) | py | ts | go | rs | Agrinet¹ |
|---|---|:--:|:--:|:--:|:--:|:--:|
| 1 | Escala −1..+4 con etiquetas exactas (§1) | yes | yes | yes | yes | yes |
| 2 | Distribución, nunca un promedio (§2) | yes | yes | yes | yes | yes² |
| 3 | Reputación delimitada por rol (§3) | no | no | no | no | yes |
| 4 | −1 lleva una narrativa de ≤500 palabras, local al operador (§4) | app | app | app | app | yes |
| 5 | Solo adición; la desestimación anota, nunca borra (§4, §6) | app | app | app | app | yes |
| 6 | Simétrica — impugnable en ambos sentidos (§5) | app | app | app | app | yes |
| 7 | Valor por defecto +2 al vencer el plazo, atribuido al sistema y marcado (§7) | app | app | app | app | yes |
| 8 | Decide si, no cuánto (§8) | yes | yes | yes | yes | yes |

¹ Agrinet = `services/lbtas.js` + `repositories/ratingRepository.js` en `NTARI-RAND/Agrinet`.
² Agrinet además **lanza una excepción** si alguna vez se solicita una puntuación de reputación de número único (`utils/reputation.js`).

## De qué es responsable cada capa

La escala y el modelo de lectura de la distribución constituyen el **núcleo del
algoritmo** — toda implementación de referencia los incluye, y las cinco coinciden en las
seis etiquetas (Delight, No Negative Consequences, Basic Satisfaction, Basic Promise,
Cynical Satisfaction, No Trust) sin deriva.

El resto del ciclo de vida del pacto se reparte por capa:

- **A nivel de código, corresponde a una implementación de referencia:** la escala y la
  distribución (§1, §2), y la **delimitación por rol** (§3). La delimitación por rol —
  indexar la distribución según el rol de la parte calificada — es la única invariante a
  nivel de código que aún no está en las implementaciones de referencia independientes;
  está plenamente implementada en Agrinet y es la mejora en seguimiento para py/ts/go/rs.
- **Asuntos de la aplicación del operador, correctamente *documentados* pero no
  implementados en una implementación de referencia:** la narrativa de ≤500 palabras y su
  almacenamiento local al operador (§4), los eventos de solo adición con la desestimación
  como anotación (§4, §6), la impugnación bidireccional (§5) y el valor por defecto al
  vencer el plazo de la ventana de calificación (§7). Estos requieren un almacén de datos,
  un rol de adjudicador y un reloj — residen en el operador (Agrinet), que los materializa
  todos.

## Brechas reconocidas con honestidad

- **Delimitación por rol en py/ts/go/rs** — aún no implementada (en seguimiento). Las
  lecturas del núcleo son independientes del rol; un operador que necesite distribuciones
  por rol las obtiene como lo hace Agrinet.
- Ninguna implementación calcula promedios, expone una puntuación única ni deriva un
  límite de la distribución de daños — se cumplen todas las invariantes cuya infracción
  reconstruiría el buró de crédito.
