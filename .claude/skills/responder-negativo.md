---
name: responder-negativo
description: Genera respuestas a comentarios negativos o quejas siguiendo el playbook de marca de B370. Pega el comentario y recibe 2-3 opciones de respuesta listas para usar. Uso: /responder-negativo [pegar comentario o DM].
---

# Skill: Responder Comentario Negativo

## Cuándo usar esta skill
Cuando llega un comentario difícil en Instagram, TikTok, Facebook, o un DM de WhatsApp con queja.

Ejemplos de activación:
- `/responder-negativo [pega aquí el comentario]`
- `/responder-negativo DM: "el pedido lleva 8 días y no llega"`
- `/responder-negativo comentario IG: "esto es estafa, no compren"`

## Flujo de operación

### Paso 1 — Leer el playbook oficial

Antes de generar SIEMPRE leer:
`C:\Proyectos\b370\PROTOCOLO 1.1 B370\b370-brand-context\b370-brand-context\04_playbooks\responder-comentario-negativo.md`

Este archivo tiene los 6 tipos de queja y las plantillas oficiales de B370.

### Paso 2 — Clasificar el tipo de queja

| Tipo | Indicadores |
|---|---|
| **Demora en envío** | "no llega", "días esperando", "cuándo llega" |
| **Talla o calidad** | "no me quedó", "diferente a la foto", "calidad mala" |
| **Acusación de estafa** | "estafa", "me robaron", "no entregan", "fake" |
| **Crítica al precio** | "muy caro", "en otro lado más barato" |
| **Comentario agresivo** | insultos directos, lenguaje ofensivo |
| **Crítica a marca/equipo** | crítica al equipo de trabajo o a decisiones de marca |

### Paso 3 — Generar 2 versiones de respuesta

**Versión 1 — Respuesta pública** (para el comentario visible):
- Empática, sin ponerse a la defensiva
- Invita a continuar la conversación en privado
- Máx 2-3 líneas — los comentarios largos suenan defensivos
- Tono: humano, cálido, resolutivo

**Versión 2 — Respuesta privada** (DM para resolver el problema):
- Más detallada, pide los datos necesarios para solucionar
- Ofrece solución concreta si aplica
- Cierra con el WhatsApp de atención

### Paso 4 — Entrega

```
TIPO DETECTADO: [tipo de queja]

RESPUESTA PÚBLICA (para el comentario visible):
"[texto de la respuesta — listo para copiar]"

RESPUESTA PRIVADA (DM para resolver):
"[texto del DM — listo para copiar]"

ACCIÓN SUGERIDA:
[qué hacer después de responder — ej: "Verificar estado del pedido en WooCommerce antes de responder el DM"]
```

## Reglas absolutas (del playbook B370)

- **Nunca borrar comentarios negativos** — salvo spam evidente (palabras irrelevantes, bot)
- **Nunca responder con sarcasmo ni ironia**
- **Responder en máximo 2 horas** en horario laboral
- **Siempre mover la conversación a privado** — no resolver el problema en público
- **Volver al hilo público** cuando el problema se resuelva — "Ya resolvimos con [nombre], gracias por la paciencia"
- Si hay acusación de estafa → PRIORIDAD ALTA, responder en menos de 30 minutos

## Nota sobre el tono

B370 no es una corporación. La respuesta debe sonar como el equipo de la tienda respondiendo — no un guion corporativo. Empático, concreto, sin rodeos.
