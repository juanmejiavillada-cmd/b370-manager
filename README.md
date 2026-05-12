# B370 Manager — Scripts de gestión WooCommerce

Sistema de automatización para B370 Línea Deportiva (b370sports.com)

## Estructura

```
b370-manager/
├── scripts/
│   ├── b370_crear_variaciones.py   → Crea variaciones + SKU de Quenti
│   ├── b370_actualizar_stock.py    → Sube inventario real por talla
│   ├── b370_actualizar_precios.py  → Asigna precios por tipo
│   ├── b370_imagenes_variaciones.py → Asigna imágenes por color/tipo
│   └── b370_crear_producto.py      → Crea productos nuevos desde cero
├── docs/
│   └── B370_SOP_Productos_Nuevos.docx
├── data/
│   └── (Excel de Quenti — no se sube a GitHub)
├── .env                  ← Credenciales (no se sube a GitHub)
├── .env.example          ← Plantilla de credenciales
├── B370-SSH.bat          ← Acceso rápido al servidor SSH
└── README.md
```

## Instalación

```bash
pip install requests python-dotenv openpyxl paramiko
```

## Configuración

1. Copia `.env.example` como `.env`
2. Rellena las credenciales en `.env`
3. Agrega el Excel de Quenti en `/data/`

## Uso

### Crear productos nuevos desde cero
```bash
python scripts/b370_crear_producto.py
```
Edita el array `PRODUCTS` en el script para agregar nuevos productos.

### Crear variaciones con SKU
```bash
python scripts/b370_crear_variaciones.py
```

### Actualizar stock desde Quenti
```bash
python scripts/b370_actualizar_stock.py
```

### Actualizar precios
```bash
python scripts/b370_actualizar_precios.py
```

### Asignar imágenes por color/tipo
```bash
python scripts/b370_imagenes_variaciones.py
```

## Acceso SSH rápido

Doble clic en `B370-SSH.bat` para conectarte al servidor.

## Convención de imágenes

Las fotos deben subirse a WordPress con este formato:
```
NOMBRE_PRODUCTO_1.jpg  → imagen principal
NOMBRE_PRODUCTO_2.jpg  → galería 2
NOMBRE_PRODUCTO_3.jpg  → galería 3
...
```

## Precios estándar B370

| Tipo | Precio |
|---|---|
| Tipo fan | $80.000 |
| Tipo jugador | $110.000 |
| 1.1 | $120.000 |
| Retro | $80.000 |
| Buzo AN | $95.000 |
| Gabán AN | $150.000 |
