---
name: lanzar-producto
description: Flujo completo de lanzamiento de una camiseta nueva en todos los canales. Valida el producto en WooCommerce, genera todas las piezas de contenido y entrega un checklist ejecutable. Uso: /lanzar-producto [nombre del producto] [fecha opcional].
---

# Skill: Lanzar Producto B370

## Cuándo usar esta skill
Cuando Juanjo quiera lanzar una camiseta nueva o reactivar una referencia con campaña.

Ejemplos de activación:
- `/lanzar-producto Barcelona Local 2026 1.1 — viernes 9am`
- `/lanzar-producto Colombia Visitante`
- `/lanzar-producto Nacional Tercera — sin pauta`

## Flujo de operación

### Paso 0 — Recopilar datos mínimos

Si el usuario no los dio, preguntar SOLO:
1. **¿Qué producto?** — nombre exacto o ID en WooCommerce
2. **¿Cuándo?** — fecha y hora del lanzamiento (si no dice, asumir "próximo día hábil 9am")
3. **¿Hay pauta paid?** — si no dice, asumir solo orgánico

No preguntar más cosas. Con esos 3 datos se puede ejecutar.

### Paso 1 — Delegar a @campaign-manager

Pasar toda la info recopilada al agente `campaign-manager` con instrucción clara:

```
@campaign-manager: Lanza [PRODUCTO] el [FECHA] a las [HORA].
Canales: Instagram, TikTok, Facebook, WhatsApp Status, Email Klaviyo.
Pauta paid: [SÍ/NO].
Ejecuta validación técnica + genera todas las piezas + entrega checklist.
```

### Paso 2 — Revisar y entregar

El agente entrega el checklist completo. Esta skill lo presenta al usuario y pregunta:
- "¿Confirmo el envío del email Klaviyo para [HORA]?"
- Si dice SÍ → invocar `enviar_email_klaviyo` con la programación correcta

## Qué NO hace esta skill

- No sube imágenes (eso lo hace Juanjo manualmente)
- No publica en redes sociales (eso lo hace Juanjo manualmente)
- No activa pauta en Meta Ads (eso viene en P3 del ecosistema)

## Formato de salida esperado

El checklist ejecutable + todas las piezas de contenido listas para copiar y pegar.
Siempre terminar con el próximo paso más urgente (normalmente: "Confirma si quieres que envíe el email Klaviyo programado para [HORA]").
