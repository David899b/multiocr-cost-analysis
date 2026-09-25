# Mensaje para Nahuel — Revisión del disclaimer de datos sensibles · MultiOCR · Escenario A

> Listo para copiar/pegar. Completar saludo y, si querés, ajustar el tono.

---

**Asunto:** Revisión del aviso de privacidad MultiOCR — te pido valides el Escenario A (retención)

**Hola Nahuel,**

Te comparto el paquete de **avisos de privacidad de datos del producto MultiOCR** (extracción de datos de documentos con IA). Definimos y **concluimos los 3 escenarios de despliegue** según qué pasa con la información del lado del proveedor de IA. **Te pido que revises el primero (Escenario A)** porque es el que aplica por defecto en la demo; los otros dos los dejé en el paquete para cuando los necesitemos.

## Qué te pido

1. Revisar `disclaimer-multiocr-escenario-a-retencion.pdf` (anexo al mensaje).
2. Confirmar si la redacción es correcta o marcar los puntos a corregir (puede ser sobre cualquier sección: promesa, rol legal, proveedor, datos sensibles, ARCO).
3. Para la validación legal, consultá con **Joaquín** y con **Fernando Arpe**. Cuando me devuelvas tus correcciones, consulto de nuevo con Fernando Arpe y cerramos.

## La diferencia entre los 3 escenarios

| Escenario | Qué hace el proveedor de IA con el contenido | Cuándo se usa | Documento |
|---|---|---|---|
| **A · El proveedor retiene** | Puede conservar el contenido conforme a su política (incluida mejora de servicios) | **Por defecto en la demo** | `disclaimer-multiocr-escenario-a-retencion.pdf` |
| **B · Sin retención (ZDR)** | Procesa y descarta el contenido tras la respuesta (retención cero) | Si el cliente no quiere que un tercero retenga data | `disclaimer-multiocr-escenario-b-zdr.pdf` |
| **C · Capa pura (JSON al LLM del cliente)** | MultiOCR extrae y devuelve el JSON; el LLM del cliente queda fuera del ámbito de MultiOCR | Si el cliente usa su propio LLM | `disclaimer-multiocr-escenario-c-capax-llm-cliente.pdf` |

## Bloqueador a resolver

Antes de la demo formal quedan **campos por completar** en los tres documentos (no bloquean la redacción ni el uso interno, pero sí la entrega oficial):

- **[RAZÓN SOCIAL / DOMICILIO / CONTACTO]** de labIA / Concentrix como Encargado del Tratamiento.
- **[CLIENTE]** — nombre de la empresa contratante.
- **[EMAIL / TEL]** de contacto de labIA.
- **Decisión pendiente:** si algún cliente adopta el Escenario B, hay que verificar que el plan real de cada proveedor (OpenAI / Google Gemini / NVIDIA) garantice retención cero antes de ofrecerlo.

Avisame si lo revisás y cuáles son tus correcciones, así consulto de vuelta con Fernando Arpe y cerramos. Gracias.

**[Tu nombre]** · [rol] · [contacto]