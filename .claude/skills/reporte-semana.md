---
name: reporte-semana
description: Genera el reporte semanal de ventas y KPIs de B370. Lee pedidos reales de WooCommerce, compara contra los KPIs objetivo y entrega 3 acciones concretas para la próxima semana. Uso: /reporte-semana o /reporte-semana [días] o /reporte-semana beto.
---

# Skill: Reporte Semana B370

## Cuándo usar esta skill
Cuando Juanjo quiere el reporte semanal para él o para compartir con Beto.

Ejemplos de activación:
- `/reporte-semana`
- `/reporte-semana 14` (últimos 14 días)
- `/reporte-semana beto` (versión resumida para WhatsApp a Beto)

## Flujo de operación

### Paso 1 — Recopilar datos de ventas

Invocar el MCP b370-ecommerce:
```
metricas_ventas_periodo(dias=7)
```

Esto devuelve: total pedidos, facturación, ticket promedio, top productos, ventas por calidad.

### Paso 2 — Leer CSV de métricas orgánicas (si existe)

Buscar en `data/metricas/` el archivo más reciente de Metricool (formato CSV).
- Si existe → leer y extraer: alcance IG, alcance TikTok, engagement, seguidores ganados
- Si no existe → reportar que faltan y decirle a Juanjo cómo bajarlo de Metricool:
  "Para métricas orgánicas: Metricool → Analytics → Exportar CSV → guardarlo en data/metricas/"

### Paso 3 — Comparar contra KPIs objetivo

KPIs objetivo del proyecto (de kpis.md):
| KPI | Objetivo |
|---|---|
| Ticket promedio | > $130.000 COP |
| Conversión web | 1.5%+ |
| CAC | < $25.000 COP |
| ROAS Meta Ads | > 3.0x (cuando haya pauta) |
| Alcance IG | +15% semana a semana |
| Alcance TikTok | +25% semana a semana |
| Engagement | > 5% |
| Respuesta WA laboral | < 30 min |

Semáforo por KPI:
- 🟢 En objetivo
- 🟡 Cerca (< 20% por debajo)
- 🔴 Fuera de objetivo

### Paso 4 — Generar las 3 acciones

Basadas en los datos reales, identificar las 3 acciones más impactantes para la próxima semana. Priorizar:
1. Lo que está en rojo y tiene solución clara
2. Lo que puede aumentar ventas en los próximos 7 días
3. Lo que evita perder ventas existentes (ej: stock crítico, producto sin precio)

### Paso 5 — Entregar el reporte

**Formato completo (para Juanjo):**
```
📊 REPORTE B370 — Semana [fechas]

VENTAS
Pedidos: [N] ([comparación semana anterior si aplica])
Facturación: $[X]
Ticket promedio: $[X] → [🟢🟡🔴]
Top producto: [nombre] ([N] unidades)

CONTENIDO ORGÁNICO
[datos de Metricool si están disponibles / mensaje de qué falta]

📌 3 ACCIONES PRÓXIMA SEMANA
1. [acción concreta con impacto esperado]
2. [acción concreta]
3. [acción concreta]
```

**Formato para Beto (si pide `/reporte-semana beto`):**
Versión corta para WhatsApp — máx 5 líneas, solo números clave y próximo paso más importante. Lista para copiar y pegar.

## Reglas

- Nunca inventar datos — si WooCommerce no devuelve pedidos, decir "0 pedidos registrados"
- Si hay dato faltante, mencionar cómo obtenerlo (no simplemente omitirlo)
- Las 3 acciones deben ser concretas, no genéricas ("publicar más contenido" NO sirve; "crear post educativo de guía de tallas el martes" SÍ sirve)
- Terminar con: "¿Te lo preparo en formato WhatsApp para Beto?" (si no lo pidió ya)
