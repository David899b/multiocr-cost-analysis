# Evidencia y corte de cierre — Disclaimer MultiOCR SaaS (no forma parte del aviso)

> Documento de trabajo (capa de evidencia del paquete). No se entrega al cliente.
> Respaldo del `disclaimer-oficial-puente-datos-sensibles` v1.2 · 16/09/2026.

## Anexo técnico recuperado — Baseline medido al 15/09/2026

| Aspecto | Estado técnico real | Localización |
|---|---|---|
| Entorno | SaaS multi-tenant 100% en infra Concentrix/labIA (sin on-prem operativo) | Puerta de API `https://www.concentrix.net.ar:2083/api` |
| Flujo | Cliente → Backend MultiOCR → proveedor IA (OpenAI / Google Gemini / Anthropic Claude / DeepSeek / Custom) | Arquitectura y flujo funcional |
| Extracción `/load` | Sin persistencia de payload; procesamiento en memoria; JSON devuelto | Arquitectura y flujo funcional |
| Persistencia `/submission` | Solo si el cliente la envía: copia en colección `Submission` por `apiKeyId` | Arquitectura y flujo funcional |
| Retención | Indefinida; sin TTL/purga; borrado vía API DELETE | Portal Swagger / OpenAPI |
| Aislamiento | Validación y scoping estricto por `x-api-id` | Integración SaaS |
| Credenciales | `apiSecretHash` con bcrypt (nunca en claro) | Seguridad |
| Cifrado | Todo el tráfico sobre HTTPS | Seguridad |

## Corte de cierre (pendientes que no bloquean la demo)

| # | Punto | Importancia | Responsable |
|---|---|---|---|
| 1 | **Revisión legal — COMPLETADA** el 16/09/2026 con Joaquín; texto aprobado. Queda vigente para el aviso general y la modalidad on-prem en backlog (pendiente de arquitectura, no de redacción) | Cerrado | Legal (Joaquín) |
| 2 | Completar razón social, domicilio y contacto de labIA/Concentrix y nombre del cliente antes de la demo formal | Alta — identificación (sección 10 del aviso) | Contratación |
| 3 | Definir política de retención (recomendado: TTL/purga automática) para alinear la retención actual indefinida con el principio de minimización (art. 4º inc. 3) | Media | Producto / IT |
| 4 | Aviso previo en UI (modal de consentimiento antes del upload) — hoy no existe en la UI/API; el vehículo actual es el documento institucional | Media — recomendado UX | Producto |
| 5 | Detallar en Anexo Técnico la retención/entrenamiento de cada proveedor según el plan configurado | Media | Operaciones |
| 6 | **NUEVO 17/09/2026 — ZDR no es el default del proveedor**: respuesta del proveedor (ticket INC000029619478, ixHello) confirma que no garantiza retención cero por defecto y que puede parsear/indexar contenido según feature. Alinear: el Escenario B debe ofrecerse solo contra plan/contrato que acredite no retención, y verificarse antes de ofrecerlo | Alta — matiza afirmaciones de los escenarios A/B | Operaciones + Fernando Arpe |
| 7 | **NUEVO 17/09/2026 — catálogo de modelos**: el runtime enruta por 14 modelos de 5 proveedores (OpenAI, Anthropic, Gemini, DeepSeek, Custom). **RESUELTO 24/09/2026**: el catálogo `vnextRuntime` provisto por el usuario es la lista autoritativa; secciones 5 actualizadas en puente y escenarios A/B (se eliminaron NVIDIA y Mistral, se menciona el enrutado `auto`) | Cerrado | Operaciones |
| 8 | **NUEVO 24/09/2026 — verificación web de DPAs públicos (iX Hello/Concentrix)**: DPA procesador + SCC2021/914 + Privacy Policy sí existen y cubren breach/borrado/transferencia/logs. Se detectó que el SA §5.3 habilita textualmente entrenar con inputs; **resuelto con Legal (Joaquín) 24/09/2026**: la redacción vigente de los avisos es la aprobada (la lista de proveedores se alineó al `vnextRuntime`). ZDR sigue siendo contratación expresa (confirmado 17/09/2026). Ver `evidencia-web-dpa-ixhello.md` | Cerrado | Legal (Joaquín) + Operaciones |

## Anexo técnico recuperado — Baseline medido al 15/09/2026

| Aspecto | Estado técnico real | Localización |
|---|---|---|
| Entorno | SaaS multi-tenant 100% en infra Concentrix/labIA (sin on-prem operativo) | Puerta de API `https://www.concentrix.net.ar:2083/api` |
| Flujo | Cliente → Backend MultiOCR → proveedor IA (OpenAI / Google Gemini / Anthropic Claude / DeepSeek / Custom) | Arquitectura y flujo funcional |
| Extracción `/load` | Sin persistencia de payload; procesamiento en memoria; JSON devuelto | Arquitectura y flujo funcional |
| Persistencia `/submission` | Solo si el cliente la envía: copia en colección `Submission` por `apiKeyId` | Arquitectura y flujo funcional |
| Retención | Indefinida; sin TTL/purga; borrado vía API DELETE | Portal Swagger / OpenAPI |
| Aislamiento | Validación y scoping estricto por `x-api-id` | Integración SaaS |
| Credenciales | `apiSecretHash` con bcrypt (nunca en claro) | Seguridad |
| Cifrado | Todo el tráfico sobre HTTPS | Seguridad |

## Anexo técnico NUEVO 17/09/2026 — Respuesta del proveedor sobre retención y persistencia (ticket INC000029619478, ixHello)

Ticket abierto por Federico Albertengo (17/09/2026), respondido por el equipo del proveedor. Síntesis que respalda los matices agregados a los avisos:

| Pregunta | Respuesta del proveedor | Impacto en disclaimers |
|---|---|---|
| ¿Retención cero garantizada por defecto? | **No.** iX Hello no garantiza retención cero por defecto; puede retener datos por seguridad, monitoreo, confiabilidad o cumplimiento. Varía según entorno, configuración y acuerdo | El Escenario B (ZDR) debe expresarse como **contratación expresa**, no como comportamiento default |
| ¿Persiste o registra el contenido del documento, o es pass-through puro? | **No es pass-through puro.** Soporta chat con archivos, knowledge bases, asistentes y conectores de datos; el contenido puede cargarse, parsearse, indexarse o procesarse temporalmente según la feature; puede haber logs/metadata operativos | Los avisos deben aclarar el alcance: para extracción `/load` de MultiOCR se mantiene el no-persistencia; para features de plataforma (bases de conocimiento) puede haber indexación — fuera del alcance declarado de la extracción |
| ¿Logging/persistencia según uso? | Puede ocurrir (archivos en chat → procesamiento temporal; archivos a knowledge base → almacenamiento/indexación para consulta) | A documentar en Anexo Técnico según feature; el cliente decide qué features usa |

## Anexo técnico NUEVO 17/09/2026 — Catálogo de modelos del runtime (`vnextRuntime`, unión a/desde ix-proxy/ixHello)

El runtime de concentrix (ij/vnext) enruta por modelos de los siguientes proveedores. Costos y latencias de referencia del propio catálogo; los tiers orientan el routing automático:

| Modelo | Proveedor | Recomendado | Costo USD/1k | Latencia hint ms | cost/speed/accuracy tiers |
|---|---|---|--:|---:|---|
| gpt-5.5 | OpenAI | no | 0.0200 | 2500 | 1 / 1 / 3 |
| gpt-5.4 | OpenAI | no | 0.0150 | 1800 | 1 / 2 / 3 |
| **gpt-5.4-mini** | OpenAI | **sí** | 0.0010 | 800 | 2 / 3 / 2 |
| gpt-4o | OpenAI | no | 0.0030 | 1500 | 1 / 2 / 3 |
| gpt-4o-mini | OpenAI | no | 0.00015 | 600 | 3 / 3 / 1 |
| **claude-haiku-4-5** | Anthropic | **sí** | 0.00025 | 700 | 3 / 3 / 1 |
| claude-sonnet-4-6 | Anthropic | no | 0.0030 | 1200 | 2 / 2 / 2 |
| claude-opus-4-7 | Anthropic | no | 0.0150 | 3000 | 1 / 1 / 3 |
| claude-opus-4-6 | Anthropic | no | 0.0150 | 3000 | 1 / 1 / 3 |
| gemini-3.1-pro-preview | Gemini | no | 0.0070 | 1500 | 1 / 2 / 3 |
| gemini-3-flash-preview | Gemini | no | 0.00075 | 700 | 3 / 3 / 2 |
| gemini-3.1-flash-lite | Gemini | no | 0.0001 | 500 | 3 / 3 / 1 |
| DeepSeek-V4-Pro | DeepSeek | no | — | — | — |
| auto (routing custom) | Custom | — | — | — | — |

Implicancias:
- Los avisos vigentes citan "OpenAI, Google Gemini, NVIDIA y Mistral" como proveedores posibles → el catálogo actual incluye además **Anthropic (Claude) y DeepSeek**. Actualizar la enumeración de la sección 5 (sub-procesadores) y el Anexo Técnico.
- El routing automático (`auto`) puede elegir proveedor según cost/speed/accuracy tiers: el Anexo Técnico debe documentar qué proveedores quedan habilitados por cuenta, ya que esto define qué sub-procesadores intervienen.