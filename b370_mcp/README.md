# MCP Server para B370 Manager

> Capa de integración con Claude (Desktop / Code) que expone las operaciones
> de tu proyecto B370 Manager como herramientas conversacionales.

## Qué hace

Antes (terminal):
```bash
python scripts/b370_actualizar_precios.py
# editas el dict PRODUCT_PRICES en el código, ejecutas, presionas ENTER
```

Ahora (Claude):
> "Sube el precio de la 1.1 del producto 670 a $125.000"

Claude llama directamente `actualizar_precios_por_calidad(670, {"1.1": 125000})`,
con validación de bandas, dry-run preview, y log a archivo.

## Cómo se relaciona con tus scripts existentes

**Tus scripts en `scripts/` siguen funcionando igual.** Son ideales para:

- Cargas masivas con datos hardcodeados (lanzar 6 productos de un golpe)
- Ejecuciones recurrentes que ya tienes documentadas
- Operaciones de migración (normalizar calidad, instalar badges, redirects)

**El MCP es para flujos conversacionales:**

- "Necesito actualizar el stock del producto X"
- "¿Qué productos tienen precio fuera de las bandas?"
- "Genérame el copy del nuevo producto Y"
- "Crea el producto Z con esta info..."

Ambos comparten `mcp/core.py` — la lógica de WooCommerce y SSH está
centralizada, no se duplica.

## Estructura

```
B370-MANAGER/                     ← tu proyecto existente
├── scripts/                      ← INTACTO (no se tocó)
│   ├── b370_crear_producto.py
│   ├── b370_actualizar_precios.py
│   └── ... etc
├── data/
├── docs/
├── imagenes/
├── .env                          ← compartido entre scripts y MCP
├── README.md                     ← tu README original
│
└── mcp/                          ← NUEVO: server MCP
    ├── server.py                 entry point
    ├── core.py                   WC client + SSH + logging compartidos
    ├── tools/
    │   ├── productos.py
    │   ├── variaciones.py
    │   ├── stock.py
    │   ├── precios.py
    │   ├── imagenes.py
    │   ├── quenti.py
    │   └── copys.py
    ├── requirements.txt          dependencias adicionales
    └── README.md                 este archivo
```

## Instalación

Desde la raíz del proyecto B370-MANAGER:

```bash
# Activar el venv que ya tienes
venv\Scripts\activate              # Windows

# Instalar dependencias adicionales del MCP
pip install -r mcp/requirements.txt
```

## Configuración

### 1. Variables de entorno

El `.env` que ya tienes funciona tal cual. Agrégale estas variables opcionales:

```env
# Modo dry-run: true = simula, false = escribe a producción
B370_DRY_RUN=true

# Bandas de validación de precios (en COP)
B370_PRICE_MIN=50000
B370_PRICE_MAX=200000

# Para tool generar_copy_producto (opcional)
ANTHROPIC_API_KEY=sk-ant-...

# Path al repo de marca (opcional, para generar_copy_producto)
B370_BRAND_REPO=C:\Users\USUARIO\Code\b370-brand-context

# Archivo de log (opcional, default: ./b370-mcp.log)
B370_LOG_FILE=./b370-mcp.log
```

### 2. Conectar a Claude Desktop

Editar `claude_desktop_config.json`:

- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "b370-ecommerce": {
      "command": "C:\\Users\\USUARIO\\Desktop\\B370-MANAGER\\venv\\Scripts\\python.exe",
      "args": ["C:\\Users\\USUARIO\\Desktop\\B370-MANAGER\\mcp\\server.py"]
    }
  }
}
```

> ⚠️ Reemplaza las rutas con las reales de tu máquina.
> Si el venv está en otra ubicación, ajústalo.

Reinicia Claude Desktop completamente (Quit desde tray, no minimizar).

### 3. Probar antes de usar

Antes de conectar a Claude, valida con MCP Inspector:

```bash
npx @modelcontextprotocol/inspector python mcp/server.py
```

Esto abre una UI donde puedes invocar manualmente cada tool. Ideal para
verificar que tu `.env` está bien y la API de WC responde.

## Tools expuestas

### Lectura (siempre seguras)

| Tool | Qué hace |
|---|---|
| `listar_productos` | Lista productos publicados |
| `consultar_producto` | Detalle + variaciones de un producto |
| `consultar_stock` | Stock de todas las variaciones |
| `buscar_imagenes_wp` | Busca IDs de imágenes en WP Media (vía SSH) |
| `importar_excel_quenti_preview` | Preview de un Excel sin aplicar |

### Escritura (respetan DRY_RUN)

| Tool | Equivalente en scripts/ |
|---|---|
| `crear_producto` | `b370_crear_producto.py` (parte de creación) |
| `crear_variaciones` | `b370_crear_producto.py` (parte de variaciones) |
| `recrear_variaciones_producto` | `b370_crear_variaciones.py` |
| `actualizar_stock_variacion` | una variación específica |
| `actualizar_stock_por_sku` | `b370_actualizar_stock.py` |
| `actualizar_precio_variacion` | una variación específica |
| `actualizar_precios_por_calidad` | parte de `b370_actualizar_precios.py` |
| `actualizar_precios_multi_producto` | `b370_actualizar_precios.py` completo |
| `asignar_imagen_variacion_rest` | imagen principal vía REST |
| `asignar_imagenes_por_atributo` | `b370_imagenes_variaciones.py` |
| `asignar_imagenes_completas` | `b370_asignar_imagenes_nuevos.py` (vía SSH) |
| `importar_excel_quenti` | combina lectura Excel + actualización stock |
| `generar_copy_producto` | nuevo — genera copy con voice-tone de marca |

### Slash commands (workflows guiados)

| Comando | Qué hace |
|---|---|
| `/lanzar_producto_completo` | Workflow paso a paso para producto nuevo |
| `/auditar_producto` | Checklist de salud de un producto existente |
| `/cargar_inventario_quenti` | Workflow para procesar Excel de Quenti |

## Modo dry-run (default ON)

Por defecto **TODO está en simulación**. Las tools de escritura te devuelven
"esto haría..." sin tocar producción. Cuando confirmes que el comportamiento
es correcto:

```env
B370_DRY_RUN=false
```

Y reinicia Claude Desktop.

## Convenciones que aprende el MCP

El MCP conoce las convenciones específicas del proyecto B370 (descritas en
`b370://catalog/atributos`):

- Atributo de talla se llama **"Tallas"** (plural), no "Talla"
- Atributo de calidad: **"Calidad"** con valores `Tipo fan`, `Tipo jugador`,
  `1.1`, `Retro` (en migración a `Tipo original`)
- Cuando un producto NO tiene calidad, se usa la key Python `None`
- Galería de imágenes vía meta key `wavi_value`, formato CSV
- SSH + WP-CLI para asignación de meta keys (`_thumbnail_id`, `wavi_value`)

## Pendientes y mejoras futuras

- [ ] Tool para ejecutar el script `normalizar_calidad` (migrar Tipo jugador → Tipo original)
- [ ] Validación pre-publicación (checkout test automático)
- [ ] Webhook de WC → MCP para sincronizar pedidos en tiempo real
- [ ] Tool de generación masiva de SKU `AN-1-1` cuando Beto apruebe el sistema
- [ ] Integración bidireccional con Quenti API (cuando esté disponible)

## Logs

Por defecto se loggea a `b370-mcp.log` en la raíz del proyecto. Útil cuando
algo falla — ahí ves qué tool se llamó, con qué args, y qué respondió WC.

## Seguridad

⚠️ **Las credenciales que tienes ahora en `.env` ya circularon en chats con
Claude.** Antes de conectar este MCP a Claude para uso real:

1. Ve a https://b370sports.com/wp-admin/admin.php?page=wc-settings&tab=advanced&section=keys
2. Revoca la key `ck_820f0c1aded087d593791f97abbdeec382b15492`
3. Genera una nueva con permisos de Lectura/Escritura
4. Actualiza el `.env`

Lo mismo aplica para SSH: si la contraseña SSH circuló, considera cambiarla
desde el panel de Hostinger.
