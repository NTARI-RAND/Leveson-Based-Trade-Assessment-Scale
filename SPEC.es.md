> Traducción comunitaria (borrador) — Política P2-002 de NTARI, Difusión Multilingüe Global. Fuente: SPEC.md (original en inglés, instantánea del 2026-10-05). Borrador comunitario asistido por máquina, pendiente de revisión por mantenedores regionales conforme a P2-002 §3.1. Las especificaciones técnicas centrales permanecen en inglés conforme a §2.2.
>
> ¿Encontraste un error en esta traducción? Tu corrección es una contribución
> bienvenida y valorada: haz un fork del repositorio y abre un pull request en
> https://github.com/NTARI-RAND/Leveson-Based-Trade-Assessment-Scale.

> **Precedencia.** El original en inglés es normativo. Esta traducción se ofrece para lectura, no para interpretación: donde difiera de `SPEC.md`, rige el inglés. Las palabras clave normativas (MUST, MUST NOT, SHOULD, SHOULD NOT, MAY), los nombres de campos, las etiquetas y los identificadores se mantienen en inglés porque constituyen el contrato de conformidad.

# Especificación de LBTAS — la reputación como pacto, no como puntuación

**Network Theory Applied Research Institute**
ID del documento: P3-014 · Versión: 0.1 (Borrador) · Junio de 2026
*Especificación normativa de la Leveson-Based Trade Assessment Scale. Acompaña a
P3-011 v2 (Janus Facing Applications), P3-012 (Agrinet Protocol Specification) y
P3-013 (Mycelium). Se rige por* Janus-Facing Architecture *(guía para constructores, v2.0) y*
Building JFA Software *(v1.0).*

Las palabras clave **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT** y **MAY** se usan
según RFC 2119.

---

## 0. Qué es LBTAS

LBTAS es la **capa de pares / reputación** de una red de Janus-Facing Architecture. Es un
**pacto** — una promesa permanente de no dañar — **no una puntuación**. Su lógica es la del
ingeniero de seguridad (Nancy Leveson): dos accidentes en setenta y tres vuelos dejan en tierra a la flota.
El volumen es una señal, pero ninguna cantidad de buenas calificaciones disuelve un daño en un promedio
cómodo.

Aquí la reputación es binaria donde importa: un miembro está **en buena posición** o **en
incumplimiento**. La calificación más baja de la escala, un `−1`, **es el incumplimiento mismo** — no un débito
contra un total acumulado.

Este documento define la escala, el modelo de lectura y las invariantes que toda
implementación conforme MUST mantener. El README expone la justificación; este archivo expone los
requisitos. Las implementaciones de referencia (`lbtas.py`, `.ts`, `.go`, `.rs`) se rigen por
él.

---

## 1. La escala

Una calificación es un entero en una **escala de seis puntos**, de `−1` a `+4`:

| Valor | Etiqueta | Significado |
|---|---|---|
| `+4` | Delight | Anticipa la evolución de las prácticas y preocupaciones del usuario después de la transacción. |
| `+3` | No Negative Consequences | Diseñado para prevenir pérdidas; supera la calidad básica. |
| `+2` | Basic Satisfaction | Cumple estándares socialmente aceptables que superan las demandas articuladas. |
| `+1` | Basic Promise | Cumple todas las demandas articuladas, y nada más. |
| `0` | Cynical Satisfaction | Cumple una promesa básica con poca o ninguna disciplina orientada a la satisfacción. |
| `−1` | No Trust | El usuario fue dañado, explotado, o recibió un producto/servicio sin disciplina o con intención maliciosa. |

`−1` es categóricamente distinto de `0…+4`: la banda positiva califica la *calidad*; `−1`
registra el *daño*. Las implementaciones MUST tratar `−1` como un incumplimiento, nunca como "uno por debajo de cero".

---

## 2. Distribución, nunca un promedio

Una reputación es una **distribución**: el conteo de calificaciones en cada nivel (`−1, 0, +1, +2,
+3, +4`) junto al total.

- Una implementación **MUST NOT** calcular ni exponer un promedio, una media, una puntuación ponderada ni
  ninguna reducción a un solo número de las calificaciones, en ninguna parte de una lectura, un informe, una insignia o una API.
- El volumen se sitúa *junto al* daño; nunca lo cancela. Un daño permanece visible de forma permanente junto
  al volumen.
- Las lecturas **SHOULD** exponer también el **conteo de transacciones** y la **antigüedad** (marcas de tiempo
  de la primera y la última calificación): el conteo y la antigüedad son, en sí mismos, señales de confianza.

Una prueba de conformidad: buscar en la implementación cualquier división de una suma de calificaciones entre un
conteo, o cualquier campo llamado `score`/`average`/`rating` que colapse la distribución. Una
implementación correcta no tiene ninguno. (Las implementaciones de referencia convierten esto en un error que se lanza donde
de otro modo se calcularía una puntuación).

---

## 3. Delimitada por rol

La reputación se mantiene **por separado para cada rol** — la capacidad en la que actuó la parte calificada
(p. ej., `market_seller`/`market_buyer`, `service_provider`/`service_client`,
`plan_producer`/`plan_backer`), derivada del tipo de intercambio y del lado de la parte calificada.
Un `−1` obtenido en un rol **MUST NOT** contaminar la distribución de otro. La
misma persona puede tener varias reputaciones delimitadas por rol a la vez.

---

## 4. El daño lleva una narrativa; el daño nunca se oculta

- Un `−1` **MUST** llevar una **narrativa justificativa de ≤ 500 palabras**. Un `−1` sin
  narrativa no es válido y MUST ser rechazado.
- La narrativa es **local al operador**: se guarda en el frontend, el registro del protocolo la referencia (no la
  transporta), **nunca** se ancla en el registro del bien común, **nunca** se federa, y
  solo la leen las propias partes del registro y el adjudicador del operador (P3-013 §6).
- El **evento** de calificación es **inmutable y de solo adición**. No hay actualización ni eliminación.
- Una **desestimación anota, nunca borra** (§6): retira el evento de la distribución de confianza
  *activa*, pero el evento sigue visible aguas abajo, anotado con **quién
  lo desestimó y por qué**. Un frontend **MAY** perdonar el daño; **MUST NOT** poder
  ocultarlo.

---

## 5. Simétrico — impugnable en ambos sentidos

El pacto funciona **en ambos sentidos**. El `−1` que un productor asigna a un consumidor es **tan impugnable como**
el inverso.

- Cualquier parte calificada **MAY** impugnar una calificación hecha en su contra, en **cualquiera de los dos** sentidos.
- El sistema **MUST NOT** codificar que una clase (p. ej., los vendedores) es confiable y la
  otra (p. ej., los compradores) es el riesgo. No existe una dirección privilegiada.
- La falta de entrega es en sí misma un daño y pertenece al pacto (véase §8 para lo que *no* pertenece).

---

## 6. Adjudicación: desestimar = anotar

Un adjudicador (un rol **local al operador**, nunca una autoridad global sobre el bien común)
**MAY** desestimar una calificación que se determine hecha de mala fe.

- Una desestimación se registra como una **nueva anotación**, nunca como una edición o eliminación (§4, P3-013
  §7). El evento desestimado y la anotación son ambos permanentes y ambos visibles.
- Una lectura calcula la distribución **activa** *excluyendo* los eventos desestimados, mientras sigue
  **mostrando cada evento desestimado** con la parte que lo desestimó y el motivo y, para una
  calificación impugnada pero ratificada, que fue ratificada.

---

## 7. Los valores por defecto por vencimiento se marcan

Cuando un intercambio se completa pero una parte no califica dentro de su **ventana de calificación**, el
sistema asigna una **calificación por defecto de `+2`** ("Basic Satisfaction"): el silencio se lee como un
intercambio que terminó sin quejas — **no** como un elogio, y **no** como un daño.

- Un valor por defecto por vencimiento **MUST** estar **atribuido al sistema** (`rater_role = system`) y
  **marcado como valor por defecto por vencimiento**.
- **MUST** ser **distinguible en la distribución** de una calificación afirmada por una parte en toda
  lectura (como lo es una desestimación), de modo que una reputación construida en parte a partir del silencio nunca se confunda
  con una construida a partir de la afirmación. Las lecturas **SHOULD** mostrar un conteo `defaulted`.
- `+2` es el valor por defecto conservador (no infla la reputación); `+3` es la
  alternativa documentada. Esta es la única constante ajustable de la escala.

---

## 8. Decide si, no cuánto

LBTAS decide **si** un miembro realiza transacciones basadas en la confianza o no — **nunca cuánto**.

- Lo que el pacto asegura es **honestidad, no capacidad**: "No te dañaré" no es "Puedo
  entregar lo que prometí".
- **Acotar el tamaño** de un compromiso que un actor honesto puede asumir es un **límite**, que
  pertenece a la **capa de economía**, no a LBTAS. El límite **MUST** derivarse de
  algo *distinto* de la distribución de daños (volumen limpio, capacidad declarada, una línea de
  partida uniforme).
- Una implementación **MUST NOT** derivar un límite o tope de gasto/crédito de la distribución de
  LBTAS. Permitir que la buena posición compre un tope más alto convierte la distribución de daños
  en una puntuación crediticia — el banco por la puerta trasera. El pacto custodia la puerta; el
  límite dimensiona la habitación; mantenlos separados.

---

## 9. Relación con la liquidación

Donde LBTAS controla la liberación de un escrow (P3-012 §7): la calificación del consumidor es el disparador de
la liberación. Un `0…+4` libera los fondos retenidos; un `−1` **no** libera — congela los fondos
y abre una auditoría. La calificación posterior que un productor hace del consumidor no mueve dinero. Esta es una
regla de *liquidación* que consume LBTAS; no forma parte de la escala en sí.

---

## 10. Garantías y no garantías

**Garantías.** Un LBTAS conforme muestra el daño de forma permanente y visible, nunca lo diluye en un promedio,
lo mantiene delimitado por rol, hace que toda afirmación pueda ser respondida en ambos sentidos, y
distingue las calificaciones afirmadas del silencio y de las desestimaciones.

**No garantías.** LBTAS atestigua **honestidad, no capacidad** (§8), y no atestigua
la honestidad del cómputo que produjo un intercambio (un emparejamiento o un precio amañado) — eso
queda fuera de alcance, y solo se verifica mediante la legibilidad y la salida barata (P3-013 §9).

---

## 11. Conformidad

Una implementación es conforme si y solo si se cumplen **todas** las condiciones siguientes:

1. Las calificaciones son enteros `−1…+4`; `−1` se trata como un incumplimiento, no como una puntuación baja (§1).
2. La reputación se expone **solo** como una distribución — sin promedio, media ni puntuación única
   en ninguna parte (§2).
3. La reputación está **delimitada por rol** (§3).
4. Un `−1` requiere una narrativa de ≤ 500 palabras; la narrativa es local al operador y nunca está en
   el bien común (§4).
5. Los eventos de calificación son de solo adición; las desestimaciones **anotan, nunca borran**, y permanecen
   visibles (§4, §6).
6. El pacto es **simétrico** — impugnable en ambos sentidos, sin clase privilegiada
   (§5).
7. Los valores por defecto por vencimiento son `+2`, **atribuidos al sistema y marcados**, distinguibles en la
   distribución (§7).
8. Ningún límite o tope se deriva de la distribución — **decide si, no
   cuánto** (§8).

---

## 12. Estado de implementación (informativo)

| Elemento | Estado |
|---|---|
| Escala de seis puntos, etiquetas (§1) | **Implementado** (`lbtas.py`/`.ts`/`.go`/`.rs`; README) |
| Distribución, nunca promediada (§2) | **Implementado** (implementaciones de referencia; Agrinet `services/lbtas.js` + `utils/reputation.js` lanza una excepción si se solicita una puntuación) |
| Delimitada por rol (§3) | **Implementado en Agrinet** (`ratingRepository.getUserReputation` por rol); **delta:** incorporar la delimitación por rol en las implementaciones de referencia independientes |
| Narrativa de `−1` ≤ 500 palabras, local al operador (§4) | **Implementado en Agrinet** (`rating_narratives`); **delta:** documentarlo en las implementaciones de referencia |
| Solo adición; desestimar = anotar (§4, §6) | **Implementado en Agrinet** (`voidById`/`upholdContest`, desestimados mostrados); **delta:** implementaciones de referencia |
| Impugnación simétrica (§5) | **Implementado en Agrinet** (`contestRating` en ambos sentidos) |
| Valor por defecto `+2` por vencimiento, marcado (§7) | **Implementado en Agrinet** (`applyRatingTimeouts`, conteo `defaulted`) |
| Decide si, no cuánto (§8) | **Conforme por ausencia** — no existe en ninguna parte un límite derivado de las calificaciones |

Las implementaciones de referencia independientes de este repositorio cubren fielmente la escala y la distribución;
el ciclo de vida del pacto (delimitación por rol, narrativa, impugnación/desestimación, valor por defecto
por vencimiento) está actualmente más completo en el backend de Agrinet y se está reconciliando de vuelta
en las implementaciones de referencia. Véase [CONFORMANCE.md](CONFORMANCE.md) para la matriz por
implementación (auditada: ninguna infracción; la delimitación por rol es la única brecha a nivel de código en las
implementaciones de referencia independientes).

---

*Network Theory Applied Research Institute, Inc. — 501(c)(3) — info@ntari.org*
*Documentación libre bajo el bien común AGPL-3.0 del proyecto — hecha para ser leída, reimplementada e impugnada.*
