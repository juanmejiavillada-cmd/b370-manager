# /analizar-ads

Analiza el rendimiento de las campañas de Meta Ads de B370 y entrega un semáforo accionable con qué pausar, qué escalar y 3 acciones concretas.

## Input esperado

El usuario puede invocar esta skill de varias formas:
- `/analizar-ads` — análisis de los últimos 7 días
- `/analizar-ads 30d` — análisis de los últimos 30 días
- `/analizar-ads campaña [nombre]` — análisis de una campaña específica

Si no especifica período, usar los **últimos 7 días** por defecto.

## Flujo

### Paso 1 — Interpretar el pedido

Identificar:
- **Período:** `last_7d` (default), `last_30d`, `this_month`, o rango personalizado
- **Alcance:** cuenta completa (default) o campaña/ad set específico
- **Foco:** si el usuario menciona una métrica específica (ROAS, CTR, creativos), priorizar ese ángulo

### Paso 2 — Delegar al agente @ads-analyst

Transferir el control a `@ads-analyst` con:
- El período identificado
- El alcance (cuenta completa o IDs específicos)
- Cualquier foco especial mencionado

### Paso 3 — Entregar el reporte

El reporte final debe incluir siempre:
1. Resumen de cuenta (gasto, ROAS, compras, CPA)
2. Semáforo por campaña (🟢🟡🔴)
3. 3 acciones concretas priorizadas por impacto
4. Alertas activas (errores, frecuencia alta, presupuesto agotado)
5. Un solo próximo paso

## Contexto que el agente tiene disponible

- Precios y márgenes B370 por calidad
- Avatares: Hincha urbano (20-35) y Hincha presupuesto (18-50)
- KPIs objetivo con thresholds para Colombia fashion e-commerce
- Calendario deportivo para contextualizar rendimiento por fecha
- Acceso directo a Meta Ads MCP para datos en tiempo real

## Notas

- Esta skill NO ejecuta cambios en Meta Ads — solo analiza y recomienda.
- Para ejecutar cambios (pausar, escalar, cambiar presupuesto), confirmar con Juanjo primero.
- Si hay campañas con pocos datos (< 50 eventos de conversión), marcarlo como inconcluyente.
- Si detecta fatiga creativa, sugerir invocar `@content-writer` para rotar creativos.
