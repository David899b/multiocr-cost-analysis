# Mensaje para Joaquín — Consulta legal · Multi OCR Tool

> Listo para copiar/pegar como email o mensaje. Solo completar el saludo final y los datos de contacto.

---

**Asunto:** Consulta legal — Aviso de privacidad y tratamiento por IA de una plataforma de extracción de datos con LLMs

**Hola Joaquín,**

Te escribo del equipo que está desarrollando **Multi OCR Tool** (árbol de trabajo ARG-597). Necesitamos tu criterio legal para cerrar un documento que regirá la privacidad del producto, y en paralelo validar con vos algunas preguntas que la investigación por nuestra cuenta no pudo responder con certeza.

## 1 · Contexto del producto

Multi OCR Tool es una plataforma que **extrae datos de documentos** (facturas, remisiones, contratos y comprobantes afines) mediante **modelos de lenguaje de gran tamaño (LLM)**. Para funcionar, el contenido de cada documento se envía a un proveedor externo (OpenAI, Google o Mistral, según la cuenta configurada) o se procesa con un modelo local (ej. Paligemma/Ollama), y el resultado de extracción se devuelve al usuario.

El uso real en producción es: **~98% OpenAI (gpt-5-mini), ~1,6% Google Gemini, menos de 1% Mistral y modelo local.** Todavía no está cerrada la decisión de qué modelo(s) se usarán en definitiva — por eso las preguntas te las organizo generales (por categoría de modelo) y específicas (por proveedor).

El producto se ofrece a empresas que procesan documentación comercial propia y de sus clientes/proveedores.

## 2 · Qué ya investigamos por nuestra cuenta (para que no partamos de cero)

Antes de escribirte hicimos una revisión con fuentes sobre:

- **Naturaleza legal de los documentos.** Según doctrina que cita la Ley 25.326 y criterios de la AAIP, las facturas, remitos y contratos contienen **datos personales de carácter "intermedio" y, por regla general, NO sensibles** (sensibles son los de origen racial/étnico, ideas políticas, convicciones religiosas, afiliación sindical, salud y vida sexual, según el art. 2º).
- **Retención y entrenamiento de cada proveedor:** OpenAI no entrena con la API y retiene logs hasta 30 días; Google no usa los datos para entrenar cuando hay cuenta pagada; Mistral no entrena por defecto; el modelo local no envía nada a terceros (salvo detalles de telemetría que se pueden desactivar).
- **Transferencia internacional:** enviar documentos a una API en EE.UU. configura una transferencia internacional (art. 12, Ley 25.326) y EE.UU. no está en la lista de países con nivel adecuado → requiere cláusulas contractuales modelo o consentimiento expreso.
- **Contenido mínimo de un aviso** según el art. 6 de la Ley 25.326 (finalidad, destinatarios, responsable, carácter de las respuestas, derechos ARCO).
- **Precedentes reales** que usamos como modelo de redacción: Nino Legal (AR, DPA por proveedor con cláusulas AAIP), ContratoAlquiler (ES, página de transparencia IA + anonimización previa), Docusign y Thomson Reuters (cláusulas de entrenamiento y revisión humana).

Con eso redactamos el **Aviso de Privacidad y Tratamiento por IA v0.1** que te adjunto (PDF + Word). **No pedimos que lo redactes desde cero: pedimos que lo valides.**

## 3 · Preguntas que necesitamos que respondas (lo que NO pudimos responder por nuestra cuenta)

### P1 · Consentimiento para datos de terceros
**Contexto:** los documentos que se procesan suelen pertenecer a un **tercero** (por ejemplo, una factura que un cliente le pasa a su proveedor, o un contrato firmado por otra parte). La Ley 25.326 exige consentimiento del **titular** de los datos (art. 5º).
**Lo que encontramos:** el art. 5º, inc. d, exime de consentimiento a los datos que "deriven de una relación contractual y resulten necesarios para su desarrollo o cumplimiento"; y el inc. c, para listados con nombre/identificación tributaria. Un precedente de la competencia (Nino Legal) pone como regla que **"el usuario debe contar con base legal o consentimiento para cargar datos de terceros"**.
**Lo que necesitamos de vos:** ¿basta con el consentimiento del usuario que sube el documento (más la cláusula de responsabilidad del usuario en el aviso), o la plataforma debe exigir/verificar la base legal para los datos de terceros? ¿Es sólida la excepción del inc. d para el caso de facturas de proveedores, o conviene apoyarse también en el consentimiento del usuario?

### P2 · Valor legal de los términos de servicio (ToS) de los proveedores
**Contexto:** los acuerdos de procesamiento que tenemos son los **términos de servicio generales** de OpenAI, Google y Mistral (más sus DPA públicos cuando existen).
**Lo que encontramos:** el art. 25 de la Ley 25.326 exige un **contrato de prestación de servicios** cuando se encarga a un tercero el tratamiento de datos personales, con condiciones de seguridad mínimas y finalidad delimitada.
**Lo que necesitamos de vos:** ¿los ToS de los proveedores alcanzan como fundamento contractual del tratamiento, o es imprescindible firmar un DPA con cada uno (como hace Nino Legal, con cláusulas modelo AAIP Res. 198/2023)? ¿Qué nivel de detalle espera la AAIP en la práctica para una plataforma que envía documentos a LLMs?

### P3 · Usuario consumidor (Ley 24.240)
**Contexto:** el producto puede usarse tanto por empresas (usuarios profesionales) como por personas que contratan servicios de extracción (potencialmente consumidores).
**Lo que encontramos:** el art. 5º de la Ley 25.326 regula el consentimiento libre, expreso e informado; pero no verificamos cómo se combina con el régimen de la Ley 24.240 cuando el usuario es consumidor final (cláusulas abusivas, información "destacada", etc.).
**Lo que necesitamos de vos:** ¿cambia la base legal cuando el usuario es consumidor? ¿El aviso debe presentarse de forma especialmente destacada/inequívoca, o alcanza con la aceptación estándar (click/checkbox)? ¿Conviene una regla distinta en el aviso para consumidores vs profesionales?

### P4 · Validación de la redacción del Aviso v0.1 (adjunto)
**Contexto:** te adjuntamos el aviso oficial para que lo revises sección por sección.
**Lo que necesitamos de vos:**
- ¿Cumple el contenido mínimo del art. 6 de la Ley 25.326?
- ¿La tabla de retención por proveedor y las afirmaciones sobre entrenamiento están correctamente planteadas, o alguna afirmación debería matizarse para no crear un compromiso que no podamos sostener?
- ¿La sección de datos sensibles (regla general: no cargar; excepción: consentimiento explícito) es correcta y suficiente?
- ¿Falta alguna cláusula estándar del mercado que esperarías ver en un aviso de este tipo?

### P5 · Estrategia internacional
**Contexto:** no descartamos que el producto salga a otros mercados (España/Latam, y potencialmente Europa por las reglas de protección de datos).
**Lo que encontramos:** Argentina regula por la Ley 25.326; en Europa aplica el GDPR; existen estándares voluntarios (ISO/IEC 27701, privacy by design).
**Lo que necesitamos de vos:** ¿conviene un aviso genérico que se usara en todos los países, o versiones por jurisdicción? ¿Lanzaríamos con el aviso argentino y adaptar en el momento de expandirnos, o conviene diseñarlo multi-jurisdicción desde el inicio?

## 4 · Decisiones de producto que condicionan tus respuestas (para que las tengas presentes)

1. ¿El modelo local se ofrece **por defecto** o solo como opción "avanzada"?
2. ¿El usuario podrá configurar **su propia API key** (BYOK) y elegir proveedor? (Define quién es el responsable frente al titular de los datos del documento.)
3. Para documentos con datos sensibles: ¿la plataforma debe **bloquear la subida** por defecto o solo **advertir**?

Estas tres son decisiones de producto, pero modifican el esquema legal aplicable, por eso te las listo acá.

## 5 · Qué esperamos de vos

- Respuesta a las **P1–P5** con fundamento (norma citada) cuando puedas.
- **Veredicto sobre la redacción** del Aviso v0.1 (adjunto): aprobás tal cual / con correcciones, o nos pasás una versión editada en el Word.
- Cualquier referencia (artículos, documentos, fallos) que sirva para dejar evidencia en el ticket ARG-597.

## 6 · Adjuntos

1. `disclaimer-oficial-datos-sensibles-multiocr.pdf` — Aviso de Privacidad y Tratamiento por IA (v0.1) en formato oficial.
2. `disclaimer-oficial-datos-sensibles-multiocr.docx` — misma versión editable en Word.
3. `guion-consulta-joaquin-datos-sensibles.md` — evidencia investigada con fuentes (tabla de retención, clasificación legal, transferencia internacional, precedentes), por si querés profundizar.

---

Sin más, quedamos atentos. Gracias por el tiempo y la ayuda.

Un abrazo,
**[Tu nombre]**
**[Tu rol]** · [Tu email/telefono] — [Nombre de la empresa/organización]