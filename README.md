# B370 Manager — Sprint 1

Plugin interno de WordPress para gestionar el catálogo WooCommerce de
[b370sports.com](https://b370sports.com). Reemplaza el flujo manual de SSH +
scripts Python + pegar en chat por una UI dentro del admin de WP.

## Estado actual (Sprint 1)

| Módulo                         | Estado           |
|--------------------------------|------------------|
| 1. Selector de producto        | ✅ Funcional     |
| 2. Subida de imágenes          | 🔲 Placeholder   |
| 3. Importar Quenti (parser)    | ✅ Parser listo y validado contra inventario real |
| 3. Importar Quenti (UI/subida) | 🔲 Sprint 2      |
| 4. Configuración variaciones   | 🔲 Sprint 2      |
| 5. Ejecución masiva            | 🔲 Sprint 3      |
| Settings (credenciales/precios)| ✅ Funcional     |

## Instalación en b370sports.com

1. **Comprimir la carpeta** `b370-manager/` en `b370-manager.zip`.
2. En el admin de WP → **Plugins → Añadir nuevo → Subir plugin**.
3. Seleccionar el `.zip` y activar.
4. Aparece el menú lateral **B370 Manager**.
5. Ir a **B370 Manager → Configuración** y pegar:
   - URL de la tienda (por defecto `https://b370sports.com`)
   - Consumer Key y Consumer Secret (generar en WooCommerce → Ajustes → Avanzado → API REST, con permisos de **Lectura/Escritura**)
   - Revisar los precios por defecto.
6. Volver a **B370 Manager → Productos**. Debería listar los productos variables de la tienda en el dropdown.

## Seguridad — importante

- Las credenciales WooCommerce que Juanjo compartió inicialmente en texto plano (conversación de brief) deben rotarse: **revocar la API key antigua** y generar una nueva desde WooCommerce → Ajustes → Avanzado → API REST.
- La Consumer Secret se guarda en `wp_options` y se envía por HTTP Basic sobre HTTPS — no queda nunca en el código del plugin.
- El plugin requiere capability `manage_woocommerce` para acceder a sus pantallas.

## Estructura del plugin

```
b370-manager/
├── b370-manager.php            # Archivo principal: header, constantes, activación, autoloader
├── includes/
│   ├── class-admin.php         # Menú + submenús + enqueue + guardado de Settings
│   ├── class-products.php      # Cliente WC REST API (GET/POST/PUT)
│   └── class-quenti.php        # Parser del Excel de Quenti (sin dependencia de WP para tests)
├── admin/
│   ├── views/
│   │   ├── products.php        # Módulo 1 — dropdown + tabla de variaciones
│   │   ├── images.php          # Módulo 2 — placeholder
│   │   ├── quenti.php          # Módulo 3 — placeholder UI
│   │   └── settings.php        # Formulario de configuración
│   └── css/
│       └── b370-admin.css      # Estilos con colores de marca
├── assets/
│   └── js/
│       └── b370-manager.js     # Placeholder JS
├── tests/
│   └── test_parser_against_real_xlsx.py  # Validación del parser contra inventario real
└── README.md
```

## Parser de Quenti — resultados de validación

Corrido contra `CUENTI INVENTARIO 6 ABRIL.xlsx` (3.025 filas totales):

| Métrica                                     | Valor |
|---------------------------------------------|------:|
| Filas CAMISETA/BUSO parseadas OK            | **1.077** |
| Rechazadas por talla infantil (`/6..18`)    | 13 (busos de arquero niño — Beto las sube después) |
| Cobertura sobre camisetas + busos           | **98,8%** |
| Familias únicas detectadas                  | 233 |

**Por tipo:** 1.019 camisetas · 58 busos
**Por calidad:** 295 Version Fan · 289 Tipo Original · 303 1.1 · 190 sin calidad explícita
**Por acabado:** 1.022 sin parches (implícito) · 55 con parches (explícito)
**Tallas detectadas:** XS, S, M, L, XL, 2XL, 3XL, 4XL, 5XL, 6XL

### Decisiones del parser (acordadas con Juanjo)

1. **`XXL` → `2XL`** (normalización, ya que Quenti usa `2XL` y WooCommerce debe alinearse).
2. **`3XL`, `4XL`, `5XL`, `6XL`, `XS` NO existen aún** como opciones del atributo Tallas en WC. El Módulo 4 debe crearlas en la primera corrida si se detectan (el test confirma que **sí** se usan en productos reales como `COLOMBIA LOCAL 2026`).
3. **`RETRO` es parte del nombre base**, NO se extrae como atributo.
4. **`TIPO ORIGINAL` == "Tipo Jugador"** del brief inicial. Unificados bajo "Tipo Original" (lo que Beto ve en Quenti).
5. **`CON PARCHES` solo se taggea explícito**; la ausencia → `sin_parches` implícito.
6. **`FAN` solo (sin "VERSION FAN")** se acepta como `version_fan` — es la forma más común en Quenti (870 filas vs 56 con "VERSION FAN").
7. **`1,1` (coma decimal colombiana) == `1.1`** — 256 filas usan coma.
8. **Prefijos aceptados:** `CAMISETA`, `CAMISETA DE`, `CAMISETA DEL`, `BUSO`, `BUSO DE`, `BUSO DEL`.

## Cómo correr el test del parser

El test replica la lógica de `B370_Manager_Quenti::parse_name()` en Python para poder ejecutarse sin servidor WordPress.

```bash
cd "ACTUALIZACION CATALOGO WOOCOMERCE"
python b370-manager/tests/test_parser_against_real_xlsx.py
```

Requiere `openpyxl` (`pip install openpyxl`) y el archivo `CUENTI INVENTARIO 6 ABRIL.xlsx` en `~/Downloads/`.

**Cuando Juanjo cambie la lógica en `class-quenti.php`, debe reflejar el cambio en el test Python** — ambos deben mantenerse 1:1. Esto es la "red de seguridad" hasta que haya tests PHP con PHPUnit.

## Roadmap

- **Sprint 2:** UI de upload del Excel de Quenti + preview de cruce contra producto padre seleccionado + integrar PhpSpreadsheet como `vendor/` preempaquetado.
- **Sprint 2:** Módulo 2 — subida de imágenes con drag & drop agrupadas por tipo (fan / original / 1.1).
- **Sprint 3:** Módulo 4 — formulario de configuración de variaciones + Módulo 5 — ejecución masiva con barra de progreso y botón de deshacer.

## Alcance vigente (prioridad Beto)

- **SÍ gestiona:** camisetas y busos de mayor rotación (~1.090 productos, 233 familias).
- **NO gestiona (por ahora):** guayos, tenis, balones, banderas, uniformes escolares. Beto los subirá poco a poco más adelante; el parser los ignora pero no falla.
