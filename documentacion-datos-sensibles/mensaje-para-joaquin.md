# Mensaje para Joaquín — Consulta legal · Multi OCR Tool

> Listo para copiar/pegar. Completar saludo final y datos de contacto.

---

**Asunto:** Consulta legal — Aviso de privacidad y tratamiento por IA (SAR: extracción de documentos con LLMs) · ARG-597

**Hola Joaquín,**

Te escribo por una consulta puntual del proyecto **Multi OCR Tool**: una plataforma que extrae datos de facturas, remisiones y contratos usando LLMs (hoy ~98% OpenAI, el resto Google Gemini y Mistral; también hay modo local). El contenido del documento se envía al proveedor según la cuenta configurada, y el modelo final todavía no está decidido.

Antes de escribirte ya investigamos y documentamos con fuentes: la clasificación legal de estos documentos bajo la Ley 25.326 (facturas/contratos = datos intermedios, no sensibles por regla general), qué retiene/entrena cada proveedor, el régimen de transferencia internacional (art. 12) y el contenido mínimo de un aviso (art. 6). Con eso redactamos el **Aviso de Privacidad v0.1** adjunto, que **no te pedimos redactar sino validar**.

## Preguntas (lo que no pudimos responder por nuestra cuenta)

**1 · Consentimiento para datos de terceros.** El documento puede ser de un tercero (ej. factura de un proveedor del cliente). Encontramos como posible excepción el art. 5º inc. d ("datos derivados de relación contractual"). ¿Basta el consentimiento del usuario que sube, con cláusula de responsabilidad en el aviso, o la plataforma debe exigir base legal por los datos de terceros? ¿Es sólida la excepción del inc. d acá?

**2 · Valor legal de los ToS de los proveedores.** ¿Los términos de servicio de OpenAI/Google/Mistral alcanzan como fundamento contractual, o es imprescindible un DPA firmado con cada uno (art. 25, Ley 25.326)? ¿Qué espera la AAIP en práctica?

**3 · Usuario consumidor (Ley 24.240).** Si el usuario es consumidor y no empresa, ¿cambia la base legal? ¿El aviso debe presentarse destacado/inequívoco o alcanza la aceptación estándar?

**4 · Validación del Aviso v0.1 (adjunto).** ¿Cumple el art. 6? ¿Alguna afirmación de la tabla de retención por proveedor debería matizarse para no comprometernos de más? ¿Falta alguna cláusula estándar de mercado?

**5 · Estrategia internacional.** Si el producto sale de Argentina: ¿aviso genérico o versiones por jurisdicción? ¿Diseñarlo multi-jurisdicción desde el inicio o adaptar al expandir?

## Decisiones de producto abiertas (condicionan las respuestas)
- ¿Modelo local por defecto o solo "avanzado"?
- ¿Usuario con su propia API key (BYOK) eligiendo proveedor? (define quién es responsable frente al titular de los datos)
- Datos sensibles: ¿bloquear la subida por defecto o solo advertir?

## Qué esperamos de vos
- Respuesta a las **P1–P5** con norma citada.
- **Veredicto** sobre el Aviso v0.1: aprobás, aprobás con cambios, o nos pasás tu versión.
- Referencias (artículos/fallos) para dejar como evidencia en el ticket.

## Adjuntos
1. `disclaimer-oficial-datos-sensibles-multiocr.pdf` — Aviso v0.1 (formato oficial).
2. `disclaimer-oficial-datos-sensibles-multiocr.docx` — misma versión editable.
3. `guion-consulta-joaquin-datos-sensibles.md` — evidencia investigada con fuentes.

Gracias por el tiempo. Quedamos atentos.

Un abrazo,
**[Tu nombre]**
**[Tu rol]** · [contacto] — [empresa/organización]