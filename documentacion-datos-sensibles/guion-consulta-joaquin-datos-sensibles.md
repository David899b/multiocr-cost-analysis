# Guión de consulta — Joaquín (abogado e investigador en IA) · Multi OCR Tool

> **Ticket:** "Consultar con Joaquín sobre mejores prácticas legales y disclaimers de privacidad" (Épica ARG-597)
> **Objetivo:** validar con Joaquín cómo asegurar que los datos sensibles no sean retenidos por el LLM, y definir mejores prácticas legales y técnicas para el disclaimer de la plataforma.

---

## 1 · Contexto que me llevo (datos reales de la plataforma)

- Multi OCR Tool procesa **facturas, remisiones y contratos** (esquemas de extracción de datos).
- El contenido del documento **se envía a un proveedor LLM** según la API key configurada.
- Uso real en producción: **OpenAI (gpt-5-mini) ~98% · Gemini gemini-3-flash 1,6% · Paligemma (local) 0,1% · Mistral 0,1%**. 6 API keys distintas.
- La retención de datos depende del **tipo de cuenta** del proveedor (Free / Paid / Enterprise / Local).

---

## 2 · Preguntas legales (para Joaquín)

### A · Retención por el LLM
1. ¿Qué significa jurídicamente que un proveedor LLM **retenga** los inputs/outputs por 30 días (OpenAI estándar) o sin retención (Enterprise/ZDR)? ¿Bajo qué norma se analiza la retención (Ley 25.326 AR / GDPR / otras)?
2. ¿Cómo se clasifican estos documentos (facturas, contratos, remisiones) respecto a **datos sensibles** según Ley 25.326 (art. 2º: origen racial, salud, ideología, hábitos sexuales…)? ¿Cuándo un documento sobrepasa "datos sensibles" y cuándo es solo "dato personal"? ¿Un contrato con DNI/CUIT es sensible o personal?
3. Si el proveedor **usa los datos para entrenar modelos aislados** (ej. OpenAI sin ZDR), ¿eso configura una **cesión o transferencia internacional de datos**? ¿Qué consentimiento / base de legitimación se requiere?
4. ¿Es suficiente el consentimiento del usuario que sube el documento, o la plataforma debe garantizar el consentimiento del **titular de los datos contenidos** (tercera persona de la factura/contrato)?

### B · Disclaimer y privacidad
5. ¿El disclaimer del tipo "los datos pueden ser procesados por un tercero" es suficiente, o qué información mínima debe contener (identidad responsable, finalidad, destino, derechos ARCO, plazo de conservación)?
6. ¿Conviene distinción por **tipo de cuenta** (Free/Paid/Enterprise/Local) dentro del disclaimer, o eso confunde y expone al cliente? ¿Es obligatorio informar la retención antes de la subida (consentimiento informado)?
7. ¿Qué vigencia tienen los **términos de servicio** de proveedores (OpenAI/Google/Mistral) como fundamento legal del tratamiento? ¿Decaerá esa defensa con la Ley Argentina de Defensa del Consumidor al usar cuentas free vs enterprise?

### C · Práctica recomendada
8. ¿Cuál es la **mejor práctica** para documentos con datos sensibles: modelo local (sin transferencia) frente a cloud con ZDR? ¿Existe obligación legal de minimización (subir solo lo necesario)?
9. ¿Recomendás algún **modelo de cláusula o disclaimer tipo** (plantilla)? ¿Qué referencias normativas citaría (25.326, GDPR, ISO/IEC 27701, principios de privacy by design)?
10. Para la versión **internacional** (si el producto sale a más países): ¿conviene un único disclaimer genérico o versiones por jurisdicción?

---

## 3 · Preguntas técnicas (para validar las afirmaciones del disclaimer)

1. **OpenAI:** confirmar que ZDR (Zero Data Retention) existe solo en **Enterprise** y que el plan estándar retiene 30 días. ¿El endpoint con la cuenta Paid utilizó "training isolation" por defecto?
2. **Google:** confirmar que **Vertex AI no usa datos para entrenar** y que **Gemini API / AI Studio puede** hacerlo si no se desactiva la preferencia. ¿Qué configuración técnica hay que tocar para desactivar la mejora?
3. **Mistral:** plazos de retención de logs según plan (standard vs enterprise).
4. **Local (Paligemma/Ollama):** verificada la no transferencia, ¿toda la infraestructura es propia (sin llamadas a telemetría del proveedor de hardware)? También atender el supuesto de modelos locales que hacen **telemetría**.
5. ¿Existe **logging de contenido** en el lado de la plataforma (ailogs) que esté capturando documentos completos? Si sí, eso es retención propia y debe informarse también.

---

## 4 · Lo que espero llevarme de la reunión

- [ ] Respuestas A1–A10 con fundamento (norma citada).
- [ ] Confirmación/corrección de la tabla "por tipo de cuenta" del disclaimer.
- [ ] Veredicto sobre si la plataforma debe **bloquear** la subida de datos sensibles por defecto o solo advertir.
- [ ] Recomendación de configuración segura para clientes con datos sensibles (mini-guía de una página).
- [ ] Nombre y evidencia (artículos/docs) para adjuntar al ticket ARG-597.

---

## 5 · Notas a llevar en la reunión

- La propuesta no inventa obligaciones: describe la retención contractual real del proveedor.
- Algunas cuentas usan nombres de esquema en español y modelos preview (gemini-3-flash-preview) → validar si eso cambia la política de retención (modelos preview pueden tener retención diferente, ej. gemini flash preview de Google).
- Decisión de producto pendiente: ¿el modelo local es opción ofrecida por defecto o solo "avanzado"?