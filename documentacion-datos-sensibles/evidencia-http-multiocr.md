# Evidencia HTTP — Integración MultiOCR (no forma parte del aviso)

> Documento de trabajo (capa de evidencia del paquete). No se entrega al cliente.
> HTTP reales probados contra producción · respaldo de `auto-eval/results/eval-20260923-produccion-output.json` y del informe `report-eval-20260923-produccion.md`.

## 1. Puerta de API y autenticación

| Aspecto | Detalle |
|---|---|
| Base URL | `https://www.concentrix.net.ar:2083/api` |
| Autenticación | Headers `x-api-id` / `x-api-secret` de la API key del cliente |
| Guardado | Solo en variables de entorno (`MULTIOCR_BASE_URL`, `MULTIOCR_API_ID`, `MULTIOCR_API_SECRET`); nunca en el repo. `apiSecretHash` con bcrypt en backend |
| Clasificación | Endpoints bajo `/api/config/*`, ámbito por `x-api-id` |

## 2. HTTP reales probados (env "Pruebas Nico", producción port 2083)

### 2.1 Verificación de credenciales — `GET /api/config` → 200 OK

```http
GET https://www.concentrix.net.ar:2083/api/config HTTP/1.1
Host: www.concentrix.net.ar:2083
x-api-id: <MULTIOCR_API_ID — ver .env>
x-api-secret: <MULTIOCR_API_SECRET — ver .env>
User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36
```

```
HTTP/1.1 200 OK
[array de 6 configs de la cuenta desplegadas en producción]
```

| Config | configId (según GET /config 23/09/2026) |
|---|---|
| Póliza | `6aa45eee852e6c70df88e3b2` |
| Expediente Laboral/Judicial | `6ab1673b9556dd1ec81ffa24` |
| Cromo Panini | `6aac38784e11cd789c8e1bac` |
| Test | `6a7f624771c289ffc35d8991` |
| Ticket Supermercado | `6a623faa71c289ffc35d744f` |
| Comprobante de pago | `6a623a6c71c289ffc35d720b` |

> Nota de verificabilidad: estos IDs salieron del GET /config de la sesión; si el archivo de respaldo vuelve a leerse, confirmar contra Swagger/GET /config antes de la demo.

### 2.2 Extracción — `POST /api/config/{configId}/load` → 200 OK (3 llamadas, docs Póliza)

```http
POST https://www.concentrix.net.ar:2083/api/config/6aa45eee852e6c70df88e3b2/load HTTP/1.1
Content-Type: application/json
x-api-id: <MULTIOCR_API_ID>
x-api-secret: <MULTIOCR_API_SECRET>
User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0 Safari/537.36

{
  "loadedImages": [{
    "loadedImage": "data:image/jpeg;base64,<imagen del documento en base64>",
    "isImage": true,
    "mimeType": "image/jpeg"
  }],
  "aiService": "openai"
}
```

```
HTTP/1.1 200 OK

{
  "configId": "6aa45eee852e6c70df88e3b2",
  "data": { "formData": { /* JSON extraído según esquema Póliza (13 campos) */ } },
  "consumption": {
    "promptTokens": <n>, "completionTokens": <m>, "totalTokens": <n+m>
  },
  "status": "ok"
}
```

Contrato completo documentado en `auto-eval/callers/callers.py` (clase `MultiOCRCaller`, `callers.py:178`).

### 2.3 Fallos documentados durante el desarrollo

```http
POST https://www.concentrix.net.ar:2083/api/api/config/6aa45eee.../load HTTP/1.1   ← doble /api
→ 403 Forbidden        (base_url ya trae /api; corregido en callers.py:233)

POST https://www.concentrix.net.ar:2083/api/config/6aa45eee.../load               ← sin User-Agent
→ 403 Forbidden        (WAF en el puerto 2083; corregido agregando User-Agent de navegador, callers.py:237)
```

## 3. Respuestas medidas (baseline al 23/09/2026)

| Doc | Status | Field F1 | ANLS | Schema OK | Costo U$S | Latencia ms | Tokens totales |
|---|---:|---:|---:|---:|---:|---:|---:|
| 01_limpia_Allianz | 200 | 1.0000 (cae a 0.9565 por tilde: pred "Benito Juárez" vs gold "Benito Juár") | 1.0000 | ✅ | 0.0043 | 163.246 | ~4.914 |
| 01_sinSuma | 200 | 0.9565 (sum_insured_total: pred 35.000.000 inferido de insured_items vs gold vacío) | 0.9565 | ✅ | 0.0045 | 167.571 | ~4.914 |
| 05_sin_numero | 200 | 0.9565–1.0000 según corrida | 0.9957 | ✅ | 0.0042 | 165.139 | ~4.914 |

Totales: **costo 0.0129 U$S en 3 llamadas · latencia p95 165.139 ms · tokens/llamada 4.913,7 · Field F1 0.9710 · ANLS 0.9841 · Schema OK 100%** · modelo observado: gpt-5-mini (routing del runtime).

Gates: Field F1 ≥ 0.9 ✅ GO · latencia ≤ 15 s ❌ **NO-GO (165 s)** · costo ≤ 50 U$S ✅ GO. Jurado multi-modelo (gemma3:12b, qwen3:14b, mistral:7b): GO, consenso 0.9840.

## 4. Persistencia / clasificación / consumo (contrato, no ejecutadas en esta corrida)

```http
POST /api/submission HTTP/1.1        # persiste la submission en la colección por apiKeyId (solo si el cliente la envía; ver evidencia-corte item "Persistencia /submission")
POST /api/config/load HTTP/1.1       # clasificación automática de tipo de documento (sin configId; retorna candidatos con umbral de confianza 0.7)
GET  /api/auth/consumption           # auditoría de consumo (propuesta en solicitud-api-key)
```

## 5. Posibles preguntas con respuestas fundamentadas

- **¿Por qué el Flujo del aviso dice "proveedor IA (OpenAI / Google Gemini / Anthropic Claude / DeepSeek / Custom)" si el HTTP usa `aiService: openai`?** Porque el catálogo `vnextRuntime` habilita 5 proveedores y el enrutado `auto` decide por tiers; `aiService` selecciona el provider en la llamada. Ver sección 5 de los avisos.
- **¿La extracción persiste el documento?** No: `/load` procesa en memoria y devuelve el JSON; solo `POST /api/submission` persiste, y únicamente si el cliente la envía.
- **¿Por qué latencia 165 s si el "promedio" del catálogo es 0,8 s?** Porque en esta medición se midió el tiempo total de la llamada `/load` contra el puerto 2083 (envío de imagen + extracción + retorno), no el TPS del LLM puro; es el dato que ve el cliente real.

## 6. Bloqueadores / decisiones abiertas

| # | Punto | Estado | Responsable |
|---|---|---|---|
| 1 | **Archivos `auto-eval/results/eval-*.json` y `golden/Póliza/*.json` y `*.jpg` eviccionados de disco local (stubs, `stat` blocks=0) al 24/09/2026.** Los `.md` sí están materializados. `brctl download` devolvió OK pero no materializó; el daemon de iCloud muestra errores de sync (`CKErrorDomain:7`, un item `needs-sync-up` con `CKInternalErrorDomain:2061`). No hay snapshots APFS locales con el dato. La lectura de los stubs falla (`FileSystem.readAlloc`, timeouts). **Conclusión: no recuperable desde este entorno; depende de materializar desde iCloud (Finder / Mac normal / otro dispositivo).** El `report-*.md` ya vuelca las métricas; el JSON crudo (predictions por doc) es el pérdido | Bloqueado — requiere acción de iCloud/Finder del usuario | Usuario
| 2 | Decisión caso `sinSuma`: gold `''` vs inferencia 35.000.000 (define el Field F1 real del campo) | Abierto | Producto |
| 3 | Defecto de gold "Planta Benito Juár" (falta la "e" final en el gold vs "Juárez" del documento) | Abierto — baja prioridad | Naturaleza del dato |
| 4 | ZDR: sólo contratación expresa (Escenario B), no default | Cerrado 17/09/2026 (INC000029619478) | Operaciones |
| 5 | Lista de proveedores alineada al `vnextRuntime` | Cerrado 24/09/2026 | Operaciones + Legal |