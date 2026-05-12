---
name: copy-producto
description: Genera copy completo y publicable para un producto de B370 Sports siguiendo el template oficial validado en Chapecoense 1.1. Incluye Title SEO, Description Short, Description Long con HTML, Bullets, CTA y Hashtags. Adapta el hook emocional según la categoría del producto (Colombiano, Selección, Internacional, Retro, etc.).
---

# Skill: Generar Copy de Producto B370

## Cuándo usar esta skill
Cuando el usuario pida "genera copy para producto X", "copy de [equipo]", "copy ID [número]", o similar.

## Modo de operación: HÍBRIDO

1. Si el usuario pasa un product_id → leer datos del MCP automáticamente
2. Detectar categoría del producto desde nombre/categoría WC
3. Si hay info clara → generar sin preguntar
4. Si falta info crítica → preguntar SOLO lo necesario

## Paso 0 — Verificar si ya tiene copy

Si se pasó un product_id, antes de generar:
1. Llamar `consultar_producto(product_id)` y revisar los campos `description` y `short_description`
2. Si ya tienen contenido → mostrar el copy actual y preguntar: "Este producto ya tiene copy. ¿Quieres reemplazarlo o mejorarlo? (mejorarlo = tomar el existente como base)"
3. Si están vacíos → proceder directamente a generación sin preguntar

## Paso 1 — Leer archivos de marca SIEMPRE
Antes de generar, leer:
- C:\Proyectos\b370\PROTOCOLO 1.1 B370\b370-brand-context\02_catalog\precios-estructura.md (glosario de calidades)
- C:\Proyectos\b370\PROTOCOLO 1.1 B370\b370-brand-context\02_catalog\metodos-pago.md (4 métodos)
- C:\Proyectos\b370\PROTOCOLO 1.1 B370\b370-brand-context\00_brand\voice-tone.md
- C:\Proyectos\b370\PROTOCOLO 1.1 B370\b370-brand-context\00_brand\buyer-personas.md

## Paso 2 — Detectar categoría
Leer nombre y categorías WC del producto. Identificar a cuál de estas pertenece:

### Categorías y hooks emocionales

**EQUIPOS_COLOMBIANOS** (Nacional, Medellín, Junior, América, Cali, Once Caldas, Tolima, Santa Fe, Millonarios, etc.)
Hook: identidad regional + hinchada + pasión local
Tono: pasional, "nosotros", "el que la viste, la siente"

**SELECCION_COLOMBIA** (cualquier producto que mencione Colombia + selección/local/visitante)
Hook: orgullo nacional + sueño colectivo + memoria de partidos
Tono: épico, unitario, "cuando sale Colombia..."

**INTERNACIONALES_TOP** (Real Madrid, Barcelona, PSG, Liverpool, Manchester City/United, Bayern, Juventus, Chelsea)
Hook: ídolos globales + estilo + culés/madridistas
Tono: aspiracional, prestigioso, "el club que define una era"

**INTERNACIONALES_SECUNDARIOS** (Boca, River, Inter, Milan, Atlético Madrid, Roma, Napoli, Borussia, Ajax)
Hook: tradición + rivalidades + historia
Tono: respetuoso, identitario, "hay clubes con jersey, y hay clubes con identidad"

**RETRO** (cualquier producto con "Retro" en nombre o categoría)
Hook: nostalgia + edición limitada + coleccionismo
Tono: emocional, vintage, "la que ya no se hace"

**HISTORIA_ESPECIAL** (Chapecoense, equipos con momentos icónicos)
Hook: respeto + memoria + resiliencia
Tono: solemne, sin victimizar, "memoria activa"

**BUZOS_GABANES_CHAQUETAS** (Buzo, Gabán, Chaqueta, Chompa)
Hook: estilo + calidez + uso urbano
Tono: práctico, versátil, "no solo para el estadio"
IMPORTANTE: NO mencionar ciudades específicas. Usar genérico: "el frío", "las noches frescas", "el día a día"

**TIPO_POLO_ENTRENO** (Tipo polo, ropa de entreno, training)
Hook: deportivo + casual + versatilidad
Tono: activo, funcional, "para entrenar, salir y vivir el fútbol todos los días"

**EDICIONES_ESPECIALES** (Edición especial, limitada, conmemorativa, aniversario)
Hook: exclusividad + edición numerada + coleccionismo
Tono: premium, escaso, "cuando se acaban, no vuelven"

## Paso 3 — Estructura OBLIGATORIA del copy

### Title SEO (3 opciones, máx 60 chars cada una)
- A: SEO/keyword (con palabras de búsqueda)
- B: Emocional (voz de marca)
- C: Mixta (balance recomendado)

REGLAS OBLIGATORIAS:
- SIEMPRE en MAYÚSCULAS
- NUNCA incluir "| B370" al final
- Formato base: "CAMISETA [EQUIPO] [CALIDAD] – [FRASE]"

### Description Short (máx 200 chars)
Debe incluir: producto + calidad + 2-3 métodos de pago
Formato: "[Hook corto del equipo]. [Producto] [Calidad]: [característica clave]. Paga contra-entrega, con tarjeta o en cuotas Addi."

### Description Long (HTML para WooCommerce)

**Párrafo 1 — Hook emocional**
Específico al equipo y a la categoría. Sin clichés.
Cierre con frase impactante.

**Párrafo 2 — Calidad + Glosario**
Empezar posicionando la calidad del producto.
Insertar glosario fluido de las 4 calidades B370 (usar EXACTAMENTE las descripciones del archivo precios-estructura.md).
Volver a características técnicas específicas (sublimación, materiales, corte).

**Párrafo 3 — Tallas + Pago**
Texto de tallas: "En B370 no te pedimos que adivines tu talla. Mira la guía de medidas en la galería: largo, ancho y manga en centímetros, para que elijas con datos, no con suerte..."

NO insertar imagen aquí. La imagen de guía de tallas va SOLO en la short_description (ver abajo).

Párrafo de pago: "Pagas como prefieras: contra-entrega cuando la recibes, con tarjeta vía Wompi, en cuotas con Addi sin necesidad de tarjeta, o por PSE desde tu banco. En B370 no te pedimos que adelantes nada."

**Párrafo 4 — Cierre**
Volver al hook del párrafo 1 con un giro conclusivo.
Cerrar SIEMPRE con: "En B370, vestimos la pasión."

**Mini-bloque opcional al final** (en cursiva):
"¿Aún tienes dudas sobre qué calidad elegir? Escríbenos al WhatsApp y te asesoramos sin compromiso."

### Bullets (5-6, dentro de <ul>)
SIEMPRE incluir:
- Bullet de calidad: "Calidad [X] sin atajos. Como debe ser." o variante
- Bullet de sublimación/material
- Bullet de corte oficial / detalles
- Bullet de guía de tallas: "Guía de tallas con medidas reales en centímetros — eliges con datos, no con suerte"
- Bullet de pago: "4 formas de pago: contra-entrega, tarjeta (Wompi), Addi en cuotas sin tarjeta, o PSE — eliges cómo"
- Bullet de credibilidad: "Tienda real, aval real: sede física en La Ceja, Antioquia. Jugadores profesionales nos visitan."

NUNCA mencionar precio en bullets.

### CTA principal
Frase corta y directa. Default: "Pídela hoy. La pagas cuando llega a tu puerta."
Variantes según categoría:
- Retro: "Llévatela mientras quedan unidades."
- Edición especial: "No esperes a que se agoten."

### Description Short — estructura con imagen
La short_description SIEMPRE lleva la imagen de guía de tallas AL FINAL, después del texto:

```html
<p>[Texto short description]</p>
<img src="https://b370sports.com/wp-content/uploads/2026/03/GUIA-DE-TALLAS.png" alt="Guía de tallas B370" width="400" height="500" style="max-width:100%;height:auto;display:block;margin-top:12px;" />
```

La imagen NO va en la description larga. Solo en short_description.

### Hashtags (5-7)
Mezcla balanceada:
- 1-2 del equipo (#Equipo #ApodoEquipo)
- 2 de marca (#B370 #B370Sports)
- 2-3 de comunidad (#FutbolColombia #HinchaDeVerdad #CamisetasFutbol)

## Paso 4 — Aplicar en WooCommerce

Si el usuario aprueba el copy:
1. Hacer BACKUP del copy actual en `b370-brand-context/05_assets/backup-copys/[ID]_[nombre]_backup_[fecha].md`
2. Llamar `actualizar_copy_en_wc(product_id, copy_dict)` con el dict que contiene:
   - `title_seo`: el título SEO elegido (opción C mixta por defecto)
   - `description_short`: el texto con la imagen de guía de tallas al final
   - `description_long`: el HTML completo (párrafos + glosario + tallas + pago + cierre)
   - `bullets`: lista de bullets (sin precios)
   - `cta`: el llamado a la acción

Si DRY_RUN está activo, la tool solo simula — informar al usuario.

NUNCA aplicar sin aprobación explícita.

## Paso 5 — Reportar resultado
Devolver:
- ID y nombre del producto actualizado
- HTTP status de la actualización
- URL pública para validar
- Categoría detectada y hook usado

## URL de imagen de guía de tallas
La URL de la imagen GUIA-DE-TALLAS.png en WP Media debe buscarse con tool buscar_imagenes_wp en cada generación, ya que puede variar. Cachear durante la sesión para no consultar repetidamente.
