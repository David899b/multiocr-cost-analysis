# Guión de consulta — Joaquín (abogado e investigador en IA) · Multi OCR Tool

> **Ticket:** "Consultar con Joaquín sobre mejores prácticas legales y disclaimers de privacidad" (Épica ARG-597)
> **Objetivo:** validar con Joaquín cómo asegurar que los datos sensibles no sean retenidos por el LLM, y definir mejores prácticas legales y técnicas para el disclaimer de la plataforma.
> **Estado:** v2 — investigación web previa realizada (14/09/2026). La consulta ya no pregunta todo: se valida lo investigado y se resuelve lo que la web no responde.

---

## 1 · Contexto real de la plataforma (baseline medible)

- Multi OCR Tool procesa **facturas, remisiones y contratos** (esquemas de extracción de datos).
- El contenido del documento **se envía a un proveedor LLM** según la API key configurada.
- Uso real en producción (ailogs.json, 1.374 llamadas): **OpenAI (gpt-5-mini) ~98,2% · Gemini gemini-3-flash-preview 1,6% · Paligemma (local) 0,1% · Mistral 0,1%**. 6 API keys distintas.
- **Decisión abierta:** todavía no está definido qué modelo(s) se usarán en definitiva. Por eso las preguntas se organizan por **categoría de modelo** (general) y **por proveedor** (específico).

---

## 2 · Lo que YA está respondido con fuentes (no preguntar, solo validar)

> Investigación web realizada el 14/09/2026. Fuentes verificadas. Joaquín solo confirma o corrige.

### 2.1 Clasificación de los documentos (¿son "datos sensibles"?)
- **Respuesta: NO por defecto.** Según doctrina citando Ley 25.326 (Escobar, "_Clasificación de la información contable_"; AAIP) las **facturas, remitos y contratos = "datos intermedios"** (personales pero NO sensibles).
- Datos sensibles (art. 2º) son solo: origen racial/étnico, opiniones políticas, convicciones religiosas/filosóficas/morales, afiliación sindical, salud, vida sexual.
- Un contrato con DNI/CUIT/facturación es **dato personal**, no sensible. **Refuerzo:** art. 5º inc. c (listados limitados a nombre/DNI/CUIT/quella no requieren consentimiento) e inc. d (datos derivados de relación contractual no requieren consentimiento).
- Corolario: **el título del ticket ("datos sensibles") es impreciso.** El riesgo real es "datos personales + confidencialidad comercial + posible dato sensible si el contenido lo revela".

### 2.2 Retención y entrenamiento por proveedor (documentado, verificado)
| Proveedor | ¿Entrena con datos de la API? | Retención por defecto | ZDR / opt-out |
|---|---|---|---|
| OpenAI API | **No** (desde mar-2023, cualquier plan) | Logs de abuso **30 días** | ZDR: enterprise, con aprobación previa, no checkbox. `store:false` en /v1/responses |
| Google Gemini API | **No si hay Cloud Billing activado** (paid). AI Studio sin billing **sí** puede | Logs limitados (detección abuso); Grounding 30 días | Vertex (no entrena + VPC-SC + región + CMEK) |
| Mistral API | No por defecto (opt-out de training separado) | 30 días post-terminación (DPA) | ZDR en planes pagos, stateless, hay que pedirlo |
| Local (Ollama/Paligemma) | No (inferencia local) | Historial local texto plano (`~/.ollama/history`) | Ollama tray app chequea ollama.com; `-cloud` corre remoto |

- **Corrección importante a mi v1:** NO es "AI Studio entrena vs Vertex no". La frontera es **billing**: con Cloud Billing activada, todo (incl. AI Studio) es "Paid Service" y Google no usa los datos para entrenar.
- Modelos **preview** (gemini-3-flash-preview): verificar si su política de retención difiere (nota abierta).

### 2.3 Transferencia internacional (TIDP)
- Enviar datos a proveedor en EE.UU. (OpenAI/Google) = **transferencia internacional** (art. 12 Ley 25.326).
- **EE.UU. NO está en la lista de países con nivel adecuado** (Disp. 60-E/2016; Res. AAIP 34/2019) → se requiere: cláusulas contractuales modelo (Disp. 60-E/2016 o Res. AAIP 198/2023) **o** consentimiento expreso del titular **o** mecanismo contractual.
- Cloud computing ya fue calificada como exportación por la RIPD (Recomendaciones sobre computación en la nube).
- **Aplicación a nosotros:** el reproceso de los documentos vía API de OpenAI/Google/Mistral debe encuadrarse en consentimiento del usuario y/o CCM con los proveedores. **Nino Legal (ARG) ya lo hace:** DPA con cada proveedor (OpenAI y Microsoft) con cláusulas AAIP Res. 198/2023.

### 2.4 Contenido mínimo obligatorio del disclaimer (art. 6 Ley 25.326)
Al recabar datos personales se debe informar previamente, en forma expresa y clara:
1. Finalidad del tratamiento.
2. Quiénes son los destinatarios (proveedores LLM).
3. Identidad/domicilio del responsable.
4. Carácter obligatorio/opcional de las respuestas y consecuencias.
5. Derechos ARCO (acceso, rectificación, supresión, oposición).

### 2.5 Precedentes de disclaimers de plataformas de análisis de documentos (modelos)
| Precedente | Qué hace bien |
|---|---|
| **Nino Legal (AR)** | DPA por proveedor con cláusulas AAIP 198/2023; "el usuario debe contar con base legal o consentimiento para cargar datos de terceros"; no entrenamiento en cuentas pagas |
| **ContratoAlquiler (ES)** | Página de Transparencia IA: nombra el LLM (Gemini), envío del texto completo, DPA con proveedores, **anonimización previa** (DNI oculto, IBAN completo, teléfono parcial), no entrenamiento, eliminación a demanda |
| **Docusign AI Attachment** | Cláusulas de entrenamiento (agregadas + anonimizadas, opt-out account-level), outputs as-is, revisión humana, conspicuidad |
| **Thomson Reuters / LexisNexis GenAI** | "No entrenamos con user content ni terceros"; verificación de outputs; aceptación de third-party provider terms |
| **LLM Consensus / routing-layers** | "No suba datos sensibles"; logs limitados; proveedor actúa como controlador independiente |
| **AAIP Res. 161/2023** | Programa de transparencia y protección de datos en IA; guías de buenas prácticas |
| **Poder Judicial CABA** | "Optar por ejecución local cuando sea posible"; anonimizar antes de enviar a políticas que no protejan |

---

## 3 · Preguntas a Joaquín — GENERALES por categoría de modelo (modelo aún no decidido)

> Estas preguntas deben responderse para CUALQUIER modelo que se elija. Diseñadas para que la respuesta quede "agnóstica al modelo".

### A · Cloud LLM vía API (OpenAI / Google / Mistral / Anthropic)
1. ¿Es suficiente el esquema "consentimiento informado del usuario al subir + DPA por proveedor" (estilo Nino Legal) como base legal para enviar documentos a la API de un tercero, o hace falta algo más?
2. Para el disclaimer: ¿es obligatorio **nombrar el proveedor** o basta con informar "un proveedor externo"? (contrapunto: art. 6 requiere 'destinatarios' — ¿se satisface con categoría o exige identificar?)
3. Si NO está decidido el modelo final: ¿recomendás **cláusulas dinámicas** (lista de proveedores actualizable) o exigís un disclaimer fijo por proveedor?
4. ¿La retención del proveedor (ej. 30 días de OpenAI) debe constar en el disclaimer con el plazo exacto, o basta decir "período definido por el proveedor según su política"?

### B · Modelo local / on-premise (Paligemma, Ollama, llama.cpp)
5. Confirmación: si el modelo corre **100% local** y no sale del perímetro, ¿se evita la TIDP (art. 12) y el régimen de proveedor/encargado? ¿Qué obligaciones quedan (seguridad art. 9, deber de confidencialidad, contrato art. 25)?
6. El "local" no es garantía automática (historial en texto plano, update-checks, telemetría de librerías HF). ¿Exigirías algo en el disclaimer/local para "local"? (¿o es tema de hardening técnico y no de disclaimer?)
7. Si ofrecemos **"local por defecto + cloud opcional para cuentas premium"**: ¿el disclaimer debe diferir según cuenta, o conviene un solo texto que describa ambos escenarios?

### C · Arquitectura que aún no existe (híbrido / varios proveedores)
8. Si el cliente configura SU PROPIA API key (BYOK) y elige el proveedor: ¿quién es responsable del tratamiento (la plataforma, el usuario del sistema, o el cliente) frente al titular de los datos del documento? ¿Cambia la respuesta según quién eligió el proveedor?
9. ¿Conviene **prohibir/bloquear por defecto** la subida de documentos con datos sensibles y permitirla solo con aviso severo (opt-in explícito), o solo advertir? (precedente LLM Consensus: "no suba datos sensibles"; Poder Judicial CABA: "optar por lo local/anonimizar")

## 4 · Preguntas a Joaquín — ESPECÍFICAS por proveedor (para cuando se decida)

1. **OpenAI:** con DPA + cláusulas AAIP, ¿"30 días de retención" + "no entrenamiento" + "ZDR enterprise" es un nivel aceptable para facturas/contratos? ¿Recomendás ZDR para todos los clientes o solo para los que procesen datos personales masivos?
2. **Google:** si migramos a **Vertex AI** (no entrena + región + VPC-SC): ¿esto elimina el problema de la TIDP realm? ¿O la transferencia a EE.UU./región persiste y se resuelve con el DPA?
3. **Mistral:** ZDR solo en planes pagos y stateless. ¿Alcanza con DPA estándar o conviene pedir ZDR a priori?
4. **Local (Paligemma):** ¿el supuesto de "sin transferencia" requiere evidencia técnica (firewall/egress) para sostener el disclaimer, o basta la afirmación de diseño?
5. **Modelos preview** (ej. gemini-3-flash-preview): ¿la política de retención puede diferir y debe verificarse antes de usar en producción con datos reales?

## 5 · Preguntas legales residuales (lo que la web NO responde)

1. **Consentimiento de terceros:** si el documento pertenece a un tercero (proveedor del cliente), ¿basta el consentimiento del usuario que sube, o la plataforma/cliente debe poder acreditar la base legal para DATOS DE TERCEROS? Encontré el art. 5º inc. d como excepción posible — ¿es sólida para el caso de facturas de proveedores? SOLO JOQUIÁN.
2. **ToS de proveedores como fundamento:** ¿los términos de servicio de OpenAI/Google/Mistral son suficiente fundamento legal del tratamiento, o exigen DPA formal? (Argentina: art. 25 Ley 25.326 exige contrato de prestación de servicios para encargo.) **¿ECA: DPA es imprescindible?** SOLO JOQUIÁN.
3. **Defensa del consumidor:** ¿decae la defensa basada en ToS cuando el usuario es consumidor (Ley 24.240) vs profesional? ¿El disclaimer debe ser "destacado" siempre? SOLO JOQUIÁN.
4. **Plantilla final:** validar la redacción del disclaimer oficial (versión v0.1) y los textos por variante (banner/checkbox/toast) antes de integrar a la UI. SOLO JOQUIÁN.
5. **Internacionalización:** si sale a otros países, ¿disclaimer genérico o por jurisdicción? (decisión de producto + legal.) SOLO JOQUIÁN.

---

## 6 · Lo que espero llevarme de la reunión

- [ ] Veredicto sobre la **categoría A/B/C** (3 preguntas de arquitectura): qué diseño minimiza riesgo legal.
- [ ] Confirmación/corrección de la **tabla de retención por proveedor** (sección 2.2).
- [ ] Respuesta definitiva a las **5 líneas de "Solo Joaquín"**.
- [ ] Veredicto **bloquear vs advertir** para datos sensibles.
- [ ] Validación del **disclaimer oficial v0.1** (nueva capítulo en `documentacion-datos-sensibles/`).
- [ ] Nombre y evidencia (artículos/docs) para adjuntar al ticket ARG-597.

---

## 7 · Notas a llevar en la reunión

- La propuesta no inventa obligaciones: describe la retención contractual real del proveedor y la somete a norma.
- El título del ticket/historia usa "datos sensibles"; la investigación sugiere que el grueso de docs son "datos personales/intermedios". Confirmar con Joaquín si el disclaimer debe llamarse "privacidad y tratamiento por IA" en lugar de "datos sensibles".
- Pendientes de producto que condicionan el disclaimer: ¿local por defecto?, ¿BYOK?, ¿nombre del responsable legal final?, ¿idioma (es/en)?