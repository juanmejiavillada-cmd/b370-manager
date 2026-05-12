---
name: post-hoy
description: Propone qué publicar hoy y genera el copy listo. Lee el calendario deportivo y el stock activo para hacer una recomendación contextualizada. Uso: /post-hoy o /post-hoy [canal específico] o /post-hoy [contexto].
---

# Skill: Post de Hoy

## Cuándo usar esta skill
El comando más frecuente del día. Cuando Juanjo quiere saber qué publicar hoy y obtener el copy listo sin pensar demasiado.

Ejemplos de activación:
- `/post-hoy`
- `/post-hoy tiktok`
- `/post-hoy — hoy hay clásico paisa`
- `/post-hoy IG, foco en Nacional`

## Flujo de operación

### Paso 1 — Leer el contexto del día

En paralelo:
1. **Leer el calendario deportivo** — `data/calendario-deportivo.json` en el proyecto. Buscar eventos de hoy o los próximos 2 días.
2. **Consultar stock activo** — invocar `listar_productos()` para ver qué tiene stock disponible.
3. **Detectar qué pilares se han usado esta semana** — si el usuario menciona esto, tomarlo en cuenta. Si no, asumir que hay que balancear: si ya se publicaron 2 posts de venta directa, hoy toca entretenimiento o educación.

### Paso 2 — Determinar el pilar del día

Distribución objetivo de la semana (según content-strategy.md):
- 35% venta directa
- 25% educación
- 20% entretenimiento
- 10% aspiracional
- 10% credibilidad

Regla simple:
- Si hay evento deportivo relevante (clásico, eliminatoria, partido de un equipo que vendemos) → entretenimiento o aspiracional
- Si hay producto con buen stock y sin post reciente → venta directa
- Si no hay nada especial → educación (enseña algo, genera valor)

### Paso 3 — Generar 2-3 opciones

Para cada opción usar `generar_post_social` con el canal apropiado:
- Canal principal por defecto: Instagram (si el usuario especificó otro, usar ese)
- Generar el post completo: caption + hashtags + nota visual

Presentar las opciones así:
```
OPCIÓN 1 — [PILAR]
Canal: Instagram
Caption: [caption completo]
Hashtags: [hashtags]
Nota visual: [qué imagen/video usar]

OPCIÓN 2 — [PILAR]
...
```

### Paso 4 — Ajustar si pide cambios

Si el usuario elige una opción y pide ajustes → modificar el texto y entregar el definitivo.

## Reglas

- Nunca generar más de 3 opciones — más es parálisis
- El caption de la opción ganadora debe quedar listo para pegar directamente
- Si hay evento deportivo grande hoy → siempre incluir al menos 1 opción relacionada
- Si el usuario dice "para todos los canales" → generar Instagram + TikTok + Facebook del mismo post adaptado

## Formato de salida

2-3 opciones bien diferenciadas + la opción de ajustar cualquiera de ellas.
Terminar con: "¿Cuál vas a publicar?" o "Confirma cuál prefieres y te paso la versión final para copiar."
