# B370 Manager

Plugin interno de WordPress + CLI Python para gestionar el catálogo WooCommerce de
[b370sports.com](https://b370sports.com).

Reemplaza el flujo manual de SSH + scripts sueltos + copiar/pegar por una UI dentro
del admin de WordPress. Beto opera todo sin conocimientos técnicos.

---

## Estado actual

| Módulo                          | Estado                                              |
|---------------------------------|-----------------------------------------------------|
| CLI Python (lectura)            | ✅ Funcional — ping, list-products, parse-quenti    |
| 1. Selector de producto (UI)    | ✅ Funcional                                        |
| 2. Subida de imágenes           | 🔲 Sprint 2                                         |
| 3. Importar Quenti (parser)     | ✅ Parser validado — 98,8% cobertura                |
| 3. Importar Quenti (UI)         | 🔲 Sprint 2                                         |
| 4. Configuración de variaciones | 🔲 Sprint 2                                         |
| 5. Ejecución masiva             | 🔲 Sprint 3                                         |
| Configuración (credenciales)    | ✅ Funcional                                        |

---

## Estructura del proyecto

```
b370-manager/
├── .env                        ← credenciales reales (NUNCA a GitHub)
├── .env.example                ← plantilla — copia y rellena
├── .gitignore
├── README.md
├── scripts/                    ← CLI Python
│   ├── cli.py                  ← punto de entrada: python cli.py <comando>
│   ├── wc.py                   ← cliente WooCommerce REST API
│   ├── quenti.py               ← parser del Excel de Quenti
│   ├── config.py               ← lee credenciales del .env (NO tocar)
│   └── requirements.txt
├── includes/                   ← plugin WordPress (PHP)
│   ├── class-admin.php
│   ├── class-products.php
│   ├── class-quenti.php
│   ├── class-variations.php
│   └── class-settings.php
├── admin/
│   ├── views/
│   │   ├── products.php
│   │   ├── images.php
│   │   ├── quenti.php
│   │   └── settings.php
│   └── css/b370-admin.css
├── assets/js/b370-manager.js
├── b370-manager.php            ← archivo principal del plugin
└── tests/
    └── test_parser_against_real_xlsx.py
```

---

## SOP — Configuración inicial (primera vez)

### 1. Clonar el repositorio

```bash
git clone https://github.com/juanmejiavillada-cmd/b370-manager.git
cd b370-manager
```

### 2. Crear el archivo .env

```bash
cp .env.example .env
```

Abrir `.env` y rellenar con las credenciales reales:

| Variable    | Dónde encontrarla                                          |
|-------------|-------------------------------------------------------------|
| `WC_URL`    | URL de la tienda: `https://b370sports.com`                 |
| `WC_CK`     | WooCommerce → Ajustes → Avanzado → API REST → Consumer Key |
| `WC_CS`     | Mismo lugar → Consumer Secret                              |
| `SSH_HOST`  | Panel Hostinger → SSH/FTP → Host                           |
| `SSH_PORT`  | Panel Hostinger → SSH/FTP → Puerto (65002)                 |
| `SSH_USER`  | Panel Hostinger → SSH/FTP → Usuario                        |
| `SSH_PATH`  | Ruta al `public_html` en el servidor                       |
| `XLSX_PATH` | Ruta local al Excel exportado desde Quenti                 |

> **Seguridad:** El `.env` nunca se sube a GitHub. El `.gitignore` ya lo excluye.
> Si las claves de API fueron compartidas en texto plano (chat, correo), rótalas:
> WooCommerce → Ajustes → Avanzado → API REST → revocar y crear nueva.

### 3. Instalar dependencias Python

```bash
pip install -r scripts/requirements.txt
```

### 4. Verificar conexión

```bash
cd scripts
python cli.py ping
```

Resultado esperado:
```
✅ Conexión OK con b370sports.com
   WC version:    8.x.x
   WP version:    6.x.x
   PHP version:   8.x.x
   Currency:      COP
```

---

## SOP — Uso del CLI Python

Todos los comandos se ejecutan desde la carpeta `scripts/`:

```bash
cd scripts
```

### Verificar conexión
```bash
python cli.py ping
```

### Listar productos variables
```bash
python cli.py list-products
```

### Ver detalle de un producto (con variaciones)
```bash
python cli.py product 1234
```

### Ver tallas configuradas en WooCommerce
```bash
python cli.py size-options
```

### Parsear inventario de Quenti
```bash
# Usa la ruta de XLSX_PATH en .env
python cli.py parse-quenti

# O especificar ruta manualmente
python cli.py parse-quenti "C:\ruta\al\inventario.xlsx"
```

### Buscar familias de productos en Quenti
```bash
python cli.py family "COLOMBIA"
python cli.py family "REAL MADRID"
```

---

## SOP — Instalar el plugin en WordPress

1. Comprimir la carpeta `b370-manager/` → `b370-manager.zip`
   (excluir `.env`, `.git/`, `scripts/`, `tests/`)
2. WordPress admin → **Plugins → Añadir nuevo → Subir plugin**
3. Seleccionar el `.zip` → Instalar → Activar
4. Aparece el menú **B370 Manager** en el sidebar
5. Ir a **B370 Manager → Configuración** y pegar:
   - URL de la tienda
   - Consumer Key y Consumer Secret (permisos: **Lectura/Escritura**)
   - Precios por defecto por tipo de calidad
6. Ir a **B370 Manager → Productos** — debe listar los productos variables

---

## SOP — Flujo completo para subir un producto nuevo

> Este flujo aplica desde Sprint 3. Por ahora los módulos 2-5 están en construcción.

1. **Exportar inventario** desde Quenti → Excel (.xlsx)
2. En WordPress admin → **B370 Manager → Productos** → seleccionar el producto padre
3. **Módulo 3:** Subir el Excel de Quenti → revisar la tabla de coincidencias → confirmar
4. **Módulo 2:** Subir imágenes drag & drop → asignar por tipo (principal + galería)
5. **Módulo 4:** Configurar variaciones:
   - ¿Tiene parches? → genera variantes con/sin
   - Seleccionar tallas disponibles
   - Confirmar precios por tipo
   - Revisar el preview
6. **Módulo 5:** Ejecutar → ver progreso en tiempo real → revisar log ✅/❌

---

## Atributos y precios de WooCommerce

### Tallas
`XS · S · M · L · XL · 2XL · 3XL · 4XL · 5XL · 6XL`

> ⚠ `XS`, `3XL`, `4XL`, `5XL`, `6XL` aún no existen en WC.
> El sistema pedirá confirmación antes de crearlas (ya hay productos reales que las usan).

### Tipos de calidad y precios estándar

| Calidad        | Precio COP  |
|----------------|-------------|
| Tipo fan       | $80.000     |
| Tipo original  | $110.000    |
| 1.1            | $120.000    |
| Retro          | $80.000     |
| Buzo AN        | $95.000     |
| Gabán AN       | $150.000    |

### Acabados
- **Con parches** / **Sin parches** — aplica solo a Tipo Original y Tipo Jugador

### Galería de imágenes
Las imágenes adicionales se guardan en la meta key `wavi_value` con formato `"ID1,ID2,ID3"`.

---

## Parser de Quenti — resultados de validación

Corrido contra `CUENTI INVENTARIO 6 ABRIL.xlsx` (3.025 filas):

| Métrica                                  | Valor      |
|------------------------------------------|:----------:|
| Filas CAMISETA/BUSO parseadas OK         | **1.077**  |
| Rechazadas (talla infantil `/6..18`)     | 13         |
| Cobertura sobre camisetas + busos        | **98,8%**  |
| Familias únicas detectadas               | 233        |

**Por tipo:** 1.019 camisetas · 58 busos
**Por calidad:** 295 Version Fan · 289 Tipo Original · 303 1.1 · 190 sin calidad explícita

### Decisiones del parser (no cambiar sin avisar)

1. `XXL` → `2XL`, `XXXL` → `3XL` (normalización)
2. `TIPO ORIGINAL` == calidad "tipo_original" (no "Tipo Jugador")
3. `CON PARCHES` se extrae como atributo; ausencia → `sin_parches` implícito
4. `FAN` solo (sin "VERSION") se acepta — es la forma más común en Quenti
5. `1,1` (coma colombiana) == `1.1`
6. `RETRO` queda en el nombre base, NO es atributo
7. Prefijos válidos: `CAMISETA`, `CAMISETA DE`, `CAMISETA DEL`, `BUSO`, `BUSO DE`, `BUSO DEL`

### Correr el test del parser

```bash
cd b370-manager
python tests/test_parser_against_real_xlsx.py
```

Requiere `openpyxl` y el Excel en la ruta configurada en `XLSX_PATH` del `.env`.

**Regla:** cuando cambie la lógica en `class-quenti.php`, debe reflejarse también
en `tests/test_parser_against_real_xlsx.py` — ambos deben mantenerse 1:1.

---

## Colores de marca B370

| Nombre        | Hex       |
|---------------|-----------|
| Azul Prusiano | `#151B2D` |
| Caramelo      | `#E2AC70` |
| Porcelana     | `#F9FAF7` |
| Canela        | `#C47B5D` |

---

## Roadmap

| Sprint | Módulos                                                                 |
|--------|-------------------------------------------------------------------------|
| 1      | ✅ CLI Python · Selector de producto · Parser Quenti · Settings         |
| 2      | Módulo 2 (imágenes drag & drop) · Módulo 3 (UI Excel + preview cruce)  |
| 3      | Módulo 4 (configurar variaciones) · Módulo 5 (ejecución masiva + log)  |
| 4      | Pruebas en b370sports.com · ajustes según feedback de Beto              |

---

## Alcance actual

- **Gestiona:** camisetas y busos de mayor rotación (~1.090 productos, 233 familias)
- **No gestiona por ahora:** guayos, tenis, balones, banderas, uniformes escolares
  (Beto los sube manualmente; el parser los ignora sin fallar)
