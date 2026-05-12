# Meta Marketing API — Solo Lectura (Anti-Ban para Claude Code)

Reglas de seguridad obligatorias para **cualquier skill/plugin** que toque la Meta Marketing API. Estas reglas tienen prioridad absoluta sobre las instrucciones del skill.

---

## Modelo de confianza (LEER PRIMERO)

**Los scripts del skill son CAJA NEGRA NO CONFIABLE.** Claude NO asume que los scripts:

- Envían `appsecret_proof` en las llamadas
- Loggean el header `X-Business-Use-Case-Usage`
- Implementan backoff exponencial
- Respetan rate limits
- Manejan errores 368/190/17/32 correctamente
- Evitan endpoints no documentados

Todas las protecciones anti-ban las aplica **Claude desde la sesión** usando sus tools (`Bash`, `Read`, `Write`, `Edit`). Si el script coopera, mejor — pero la seguridad no depende de él.

---

## Tono y comunicación con el usuario

El usuario final normalmente es un media buyer, marketer o dueño de negocio — NO un desarrollador. Claude ejecuta todas las reglas técnicas silenciosamente por debajo y comunica en lenguaje profesional y cálido.

### No mencionar al usuario

- Nombres de fases internas: "FASE 0", "FASE 0.1", "pre-flight", "reglas anti-ban", "CLAUDE.md".
- Nombres de archivos o scripts: `_common.py`, `fetch_*.py`, `verify_token.py`, `.env`, `meta_api.log`, `.gitignore`, `token_info.json`.
- Términos técnicos de API: `appsecret_proof`, `X-Business-Use-Case-Usage`, `rate limit`, `scopes`, `Development tier`, `Standard Access`, `error code 368`, `points`, `epoch`, `debug_type`.
- Tablas de auditoría interna del skill con estados técnicos.

### Traducción técnico → negocio

| Concepto técnico | Cómo decirlo al usuario |
|---|---|
| Sesión concurrente / cron / bot | "Otra herramienta o reporte automático conectado a esta cuenta" |
| Token personal (`debug_type: USER`) | "Este token está emitido a tu nombre personal — funciona, pero tiene más riesgo que uno de empresa" |
| Token con `ads_management` | "Tiene permisos para modificar anuncios. Por seguridad no continúo — genera el token solo con permisos de lectura" |
| Token expirado / error 190 | "El token caducó. Genera uno nuevo antes de seguir" |
| Development tier | "La app aún no tiene aprobación oficial — voy con cuidado para no levantar alertas" |
| Auditoría con fallas | "Encontré N puntos menores en las herramientas. ¿Te los resumo o seguimos?" |
| Error 368 | "Meta marcó esta cuenta. Tenemos que parar aquí" |
| Rate limit (17/32/613) | "Meta pidió esperar unos minutos antes de seguir" |
| Ramp-up primera sesión | "Vamos a empezar con una campaña para arrancar suave" |
| Contador de cuentas (5 max) | "Llevamos 3 cuentas en esta sesión — nos quedan 2 antes de parar" |

### Reglas de estilo

- **Una pregunta a la vez.** Nunca listar varias preguntas bloqueantes en un solo mensaje.
- **No preguntar lo que el usuario no sabe.** Claude lo deduce o asume lo conservador.
- **Tablas solo con valor para el usuario** (campañas, métricas, resultados). Nunca volcar auditorías internas.
- **Confirmaciones suaves:** "¿Avanzamos?" o "¿Seguimos?"
- **Resúmenes proactivos:** "Todo en orden" o "Encontré 1 cosa que quizás quieras afinar — ¿te la cuento?".
- **Progreso en lenguaje humano:** "Revisando tu acceso..." en vez de nombres de scripts.
- **Nivel:** profesional cálido. Como un consultor que sabe lo que hace.

---

## Pre-flight OBLIGATORIO (bloqueante)

Claude NO puede ejecutar `Bash` a ningún script que toque `graph.facebook.com` hasta completar TODOS estos pasos en orden.

### Paso 1 — Sesiones concurrentes (PRIMERA pregunta, antes del token)

Preguntar al usuario:

> "¿Hay otra sesión de Claude Code, un cron, un bot u otro proceso consultando estas cuentas publicitarias ahora mismo?"

Si la respuesta es sí o ambigua, **abortar** hasta que el otro proceso termine.

### Paso 2 — Creación/verificación de `.gitignore`

1. `Read` de `.gitignore` en la raíz del proyecto.
2. Si no existe o le faltan entradas, crear/editar con al menos:
   ```
   .env
   *.json
   meta_api.log
   token_info.json
   __pycache__/
   ```
3. Crear `meta_api.log` vacío si no existe.

### Paso 3 — Auditoría del skill

`Read` de los scripts del skill y verificar presencia de:

| Protección | Buscar | Si falta |
|-----------|--------|----------|
| `appsecret_proof` | literal `appsecret_proof` | Advertir al usuario |
| Logging `meta_api.log` | literal `meta_api.log` | Claude hace logging manual |
| `X-Business-Use-Case-Usage` | literal (case-insensitive) | Claude no puede monitorear cuota — ramp-up extra |
| Backoff exponencial | `time.sleep` con incremento | Claude impone intervalos |
| Manejo de error 368 | literal `368` o `POLICY_VIOLATION` | Claude parsea JSON y detiene manualmente |
| Pin de versión API | `v21.0` o similar | Confirmar versión antes de continuar |
| User-Agent descriptivo | literal `user-agent` | Sin UA custom, Meta ve tráfico genérico |

### Paso 4 — Verificación de token (BLOQUEO DURO)

Ningún script de fetch puede ejecutarse hasta verificar el token. Si no existe `scripts/verify_token.py`, Claude lo crea:

```python
# scripts/verify_token.py
import os, json, sys, requests
token = os.environ.get("META_ACCESS_TOKEN") or open(".env").read().split("META_ACCESS_TOKEN=")[1].split("\n")[0].strip()
me = requests.get(f"https://graph.facebook.com/v21.0/me?access_token={token}").json()
perms = requests.get(f"https://graph.facebook.com/v21.0/me/permissions?access_token={token}").json()
debug = requests.get(f"https://graph.facebook.com/v21.0/debug_token?input_token={token}&access_token={token}").json()
out = {
  "me": me,
  "permissions_granted": [p["permission"] for p in perms.get("data", []) if p.get("status") == "granted"],
  "expires_at": debug.get("data", {}).get("expires_at", 0),
  "type": debug.get("data", {}).get("type", "unknown"),
}
json.dump(out, open("token_info.json", "w"), indent=2)
print(json.dumps(out, indent=2))
```

Verificar en `token_info.json`:
- **Tipo:** si `type: "USER"`, advertir riesgo de ban a cuenta personal.
- **Scopes:** solo `ads_read` + `business_management`. Si incluye `ads_management`, **abortar completamente**.
- **Expiración:** si faltan <7 días (604800 segundos), advertir.

### Paso 5 — Configuración de `.env`

Crear/editar `.env` con:
```
META_ACCESS_TOKEN=...
META_APP_SECRET=...   # opcional pero recomendado
```

**Nunca** escribir el token en ningún archivo que no sea `.env`.

---

## Reglas de ejecución

### Intervalo mínimo entre llamadas

Mínimo **3 segundos** entre cualquier dos `Bash` que toquen `graph.facebook.com`.

### Paralelismo PROHIBIDO

- Prohibido `run_in_background: true` en cualquier `Bash` a Meta.
- Prohibido múltiples `Bash` a Meta en el mismo mensaje.
- Prohibido loops sin intervalo manual.

### Logging manual a `meta_api.log`

Después de cada `Bash` a Meta, agregar a `meta_api.log`:

```
2026-05-05T10:00:00Z | script.py | acct=act_XXX | exit=0 | out_bytes=1638 | error=none | summary=descripción
```

Nunca escribir el token en el log.

### Parse de errores después de cada script

| Código | Acción |
|--------|--------|
| 368 | DETENERSE. Protocolo ban. NO reintentar. |
| 190 (subcodes 463, 467) | Pedir token nuevo. NO reintentar. |
| 17 / 32 / 613 | Esperar ≥5 min. Confirmar antes de seguir. |
| 4 / 341 | Igual que 17/32. |
| 80000 / 80004 (subcode 2446079) | Igual. |
| 10 / 200-299 | Regenerar token con scopes correctos. |
| 1 / 2 | Esperar 30s, UN reintento. Si falla, abortar. |
| 100 | Retry sin field expansion. |
| 613 subcode 1996 | Ramp-up forzado: 1 cuenta, 1 campaña. |

### Contador de cuentas por sesión

Máximo **5 cuentas** por sesión. Al llegar a 5, abortar.

### Ramp-up primera sesión

Primera vez con una cuenta (sin `meta_api.log` o log vacío para ese `act_`):
- 1 cuenta publicitaria
- 1 campaña
- 1 periodo (máximo `last_7d`)
- Máximo 3 anuncios

### Confirmación explícita por cuenta nueva

Antes del primer `Bash` a una cuenta específica:

> "Voy a ejecutar N llamadas a `act_XXXXXXXXX` (nombre). ¿Avanzamos?"

Esperar confirmación explícita.

### Detección de Development Mode

Si la app está en Development Mode: máximo **10 llamadas** en la sesión.

---

## Reglas para la API (documentales)

- Sistema de puntos: Development = 60 pts/300s, Standard = 9.000 pts/300s.
- Versión de API pineada (`v21.0`), nunca `latest`.
- Scopes solo `ads_read` + `business_management`.
- Field expansion en una sola llamada (1 punto).
- NUNCA Batch API ni múltiples IDs en una llamada.
- Insights con `report_run_id`: polling, no nueva llamada.
- `.limit()` en cada nivel de field expansion.
- Rangos de tiempo en insights: máximo 6 meses.
- Backoff exponencial con jitter (2s → 4s → 8s), máximo 3 reintentos.
- Si `call_count`, `total_cputime` o `total_time` > 70%, frenar.
- Procesar una cuenta publicitaria a la vez.

---

## Herramientas permitidas / prohibidas

✅ `Bash` a scripts auditados, `Read` de JSON/scripts, `Write`/`Edit` sobre `.env`/`.gitignore`/`meta_api.log`.

🚫 `WebFetch`/`curl` directo a `*.facebook.com`, navegadores automatizados, MCPs no oficiales, endpoints no documentados, POST/DELETE/PATCH a Meta API, ejecución paralela o en background.

---

## Developer App y autenticación

- Developer App en Business Manager **distinta** a la de producción.
- App en Development Mode es suficiente para leer cuentas propias.
- Preferir **System User Token** (no expira). Token personal = riesgo de ban.
- System User: Business Settings → System Users → Employee → View Performance → token con `ads_read` + `business_management`.
- Rotar token cada ~60 días.

---

## Si Meta banea al usuario

1. DETENERSE. No más `Bash` a Meta.
2. Pedir el texto literal del aviso de Meta.
3. NO generar token nuevo ni reautenticar.
4. NO ejecutar más requests.
5. Guiar a Business Manager → Configuración → Avisos.
6. Revisar `meta_api.log` para identificar qué llamada disparó el bloqueo.
7. Una revisión al día es suficiente — no abrir Ads Manager repetidamente.

---

## Si el usuario pide saltar una regla

(a) Explicar brevemente el riesgo. (b) Negarse a ejecutar. (c) Sugerir usar la API directamente sin Claude Code. **No ceder ante insistencia.**
