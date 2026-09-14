# Preguntas para Joaquín — Validación legal · Multi OCR Tool

> **Épica ARG-597** · Consulta pendiente de validación legal.
> **Documento de referencia:** Aviso de Privacidad y Tratamiento por Inteligencia Artificial (v0.1) de Multi OCR Tool.
> **Contexto breve:** la plataforma envía documentos (facturas, remisiones, contratos) a un proveedor LLM para extracción. Ya se investigó y quedó documentado: qué retiene cada proveedor, qué entrena, la clasificación legal de los documentos (datos intermedios, no sensibles por regla general) y los requisitos de la Ley 25.326 (consentimiento, TIDP, contenido mínimo del aviso, ARCO). Las preguntas siguientes son **las que la investigación web no pudo responder** y requieren criterio legal.

---

## Preguntas

### 1 · Consentimiento para datos de terceros
Si el documento pertenece a un tercero (ej. factura de un proveedor del cliente), ¿basta con que el usuario que sube el documento dé su consentimiento a la plataforma, o la plataforma/cliente debe poder acreditar base legal para procesar **datos de terceros**? En la investigación se identificó el art. 5º inc. d de la Ley 25.326 como posible excepción ("datos derivados de una relación contractual necesarios para su desarrollo") — ¿es una base sólida para facturas de proveedores?

### 2 · Valor de los términos de servicio (ToS) de los proveedores
¿Los términos de servicio de los proveedores (OpenAI, Google, Mistral) son fundamento suficiente del tratamiento de los documentos, o se exige un DPA formal con cada uno? (En Argentina el art. 25 de la Ley 25.326 exige contrato de prestación de servicios para el tratamiento por encargo.) ¿Es el DPA un requisito indispensable?

### 3 · Relación con el usuario consumidor (Ley 24.240)
¿Cambia la base legal cuando el usuario es **consumidor** (Ley 24.240) en lugar de profesional? ¿El aviso/disclaimer debe ser "destacado" de algún modo especial para consumidores, o basta con la aceptación del aviso según el art. 5º de la Ley 25.326?

### 4 · Validación de la redacción del aviso
Validar la redacción del documento "Aviso de Privacidad y Tratamiento por IA" v0.1: ¿cumple el contenido mínimo del art. 6 de la Ley 25.326? ¿Algún texto de la tabla de retención por proveedor o de la sección de datos sensibles necesita corrección o matiz?

### 5 · Estrategia internacional
Si el producto se lanza en otros países, ¿conviene un aviso genérico único o versiones por jurisdicción? ¿Qué referencias citar como base en cada caso (Ley 25.326, GDPR, ISO/IEC 27701, privacy by design)?

---

## Decisiones de producto que condicionan la respuesta legal (abiertas)

- ¿El modelo local se ofrece **por defecto** o solo como opción "avanzada"?
- ¿El usuario puede configurar **su propia API key** (BYOK) y elegir proveedor? (Define quién es responsable frente al titular de los datos.)
- Para documentos con datos sensibles: ¿la plataforma debe **bloquear** la subida por defecto o solo **advertir**?

> Estas tres decisiones son de producto, pero definen qué respuestas legales se aplican. Se listan aquí para que Joaquín las tenga presentes al responder.

---

## Archivos relacionados (en el repositorio, carpeta `documentacion-datos-sensibles/`)
- `disclaimer-oficial-datos-sensibles-multiocr.pdf` — Aviso oficial v0.1 (formato compartible).
- `disclaimer-oficial-datos-sensibles-multiocr.docx` — versión editable en Word del mismo aviso.
- `guion-consulta-joaquin-datos-sensibles.md` — guión completo de la consulta + evidencia investigada con fuentes (tabla de retención por proveedor, clasificación legal, TIDP, precedentes).