# B370 Manager — Sistema de gestión WooCommerce con Claude Code

Sistema de automatización para B370 Línea Deportiva (b370sports.com).  
Permite subir productos, sincronizar inventario Quenti, gestionar imágenes y generar contenido usando Claude Code + MCPs.

## Instalación en PC nuevo

### 1. Clonar el repositorio

```powershell
git clone https://github.com/juanmejiavillada-cmd/b370-manager.git "C:\Proyectos\b370\PROTOCOLO 1.1 B370\B370-MANAGER"
cd "C:\Proyectos\b370\PROTOCOLO 1.1 B370\B370-MANAGER"
```

### 2. Instalar Python 3.14+

Descargar desde [python.org](https://python.org/downloads) — marcar **"Add Python to PATH"** al instalar.

### 3. Crear entorno virtual e instalar dependencias

```powershell
python -m venv venv
venv\Scripts\pip install anthropic fastmcp paramiko pandas openpyxl requests python-dotenv scp mcp
```

### 4. Configurar credenciales

Crear el archivo `.env` en la raíz del proyecto (pedir a Juanjo):

```
WC_URL=https://b370sports.com
WC_CK=ck_...
WC_CS=cs_...
SSH_HOST=195.35.15.241
SSH_PORT=65002
SSH_USER=...
SSH_PASS=...
SSH_PATH=/home/u122447978/domains/b370sports.com/public_html
ANTHROPIC_API_KEY=sk-ant-...
B370_DRY_RUN=false
```

### 5. Instalar Claude Code

Descargar desde [claude.ai/code](https://claude.ai/code) e iniciar sesión con la cuenta de Claude.

### 6. Abrir el proyecto

Abrir Claude Code → abrir carpeta `C:\Proyectos\b370\PROTOCOLO 1.1 B370\B370-MANAGER`

---

## Flujo de trabajo (subir un producto)

1. Soltar las fotos en `imagenes/por-renombrar/`
2. Abrir Claude Code con el proyecto
3. Escribir en el chat: `NOMBRE DEL PRODUCTO / CALIDAD`

Ejemplo: `BARCELONA LOCAL / TIPO ORIGINAL CON DORSAL`

Claude hace todo automáticamente: renombra imágenes, las sube al servidor, crea el producto en WooCommerce, asigna SKUs desde Quenti.

---

## Estructura

```
B370-MANAGER/
├── .claude/          ← configuración Claude Code (agentes, skills, CLAUDE.md)
├── b370_mcp/         ← MCP servidor ecommerce (WooCommerce + SSH)
├── b370_content/     ← MCP servidor contenido (posts, emails, WhatsApp)
├── imagenes/
│   ├── por-renombrar/  ← soltar fotos aquí
│   └── para-subir/     ← fotos procesadas (se genera automáticamente)
├── data/             ← inventario Quenti (Excel) + calendario deportivo
├── scripts/          ← scripts de utilidad
├── .env              ← credenciales (NO está en GitHub)
└── README.md
```

---

## Precios estándar B370

| Calidad | Precio |
|---|---|
| Tipo fan | $79.900 |
| Tipo original | $109.900 |
| 1.1 | $119.900 |
| Retro | $79.900 |
