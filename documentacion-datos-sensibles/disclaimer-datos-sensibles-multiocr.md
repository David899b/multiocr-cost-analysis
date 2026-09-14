# Disclaimer de manejo de datos sensibles — Multi OCR Tool

> **Ticket ARG-597** · Epic: Seguridad y gestión de datos sensibles
> **Descripción:** agregar disclaimers en la plataforma sobre el manejo de datos sensibles y las limitaciones de privacidad según el tipo de cuenta utilizada.
> **Entregable:** texto listo para integrar en la plataforma (variantes por proveedor/tipo de cuenta) + evidencia técnica de retención por proveedor para adjuntar en el ticket.

---

## 1 · Evidencia técnica: qué proveedores y modelos procesan los documentos hoy

Basado en datos reales de producción (collection `ailogs`, 1.374 llamadas, 24/08):

| Proveedor | Modelo principal | Llamadas | % del total | API keys |
|---|---|---|---|---|
| OpenAI | gpt-5-mini-2025-08-07 | 1.349 | 98,2% | hashes presentes |
| Google AI | gemini-3-flash-preview | 22 | 1,6% | ídem |
| Google (local híbrido) | paligemma | 2 | 0,1% | ídem |
| Mistral | mistral-large-3-675b-instruct-2512 | 1 | 0,1% | ídem |

Hallazgo relevante para el disclaimer: la plataforma envía el **contenido del documento (facturas, remisiones, contratos)** al proveedor LLM configurado para esa API key. **No todo el procesamiento es local.**

---

## 2 · Texto listo para la plataforma

### 2.1 Dislaimer general (banner al subir documento)

> **Tratamiento de datos sensibles**
>
> Multi OCR Tool procesa documentos mediante proveedores de inteligencia artificial de terceros (OpenAI, Google, Mistral, entre otros) para extraer la información que tu esquema requiere.
>
> Al subir un documento declarás que tenés la **autoridad para procesar los datos que contiene** y que conocés las implicancias de privacidad según el contrato/tipo de cuenta del proveedor configurado. Los documentos pueden ser **retenidos, registrados o utilizados por el proveedor** para las finalidades previstas en sus términos, conforme a su política de retención.
>
> Para documentos sujetos a normas de protección de datos personales (ej. Ley 25.326 en Argentina, GDPR en la UE) o con datos sensibles (salud, finanzas, identidad), verificá con tu responsable de datos el proveedor y el **tipo de cuenta** adecuado *(ver "Limitaciones por tipo de cuenta").*

### 2.2 Disclaimers según proveedor/tipo de cuenta

La limitación clave: **la retención y el uso de los datos depende de la cuenta de API que la organización configure en la plataforma (Free / Paid / Enterprise / Local).** No depende de la plataforma.

**☑️ OpenAI** (modelos `gpt-*`)
- **Cuenta API estándar (Paid):** los datos se retienen por defecto hasta **30 días** para auditoría y abuso. OpenAI ofrece **Zero Data Retention (ZDR)** solo en cuentas Enterprise (no se retienen los inputs/outputs). Sin ZDR, el proveedor puede utilizar los datos para **entrenamiento específico del usuario aislado** (pero no para entrenar modelos que no sean los del cliente).
- **Free tier / playground:** los datos pueden usarse para **entrenamiento general** si no se desactiva en la organización.
- **Disclaimer a mostrar:**
  > *"Los datos enviados a OpenAI se procesan bajo los términos del plan {FREE / PAID / ENTERPRISE} de tu organización. El plan estándar retiene los datos hasta 30 días y puede utilizarlos para entrenamiento aislado. El plan Enterprise con Zero Data Retention no retiene los datos. Verificá tu plan y habilitá ZDR antes de procesar datos sensibles."*

**☑️ Google AI (Gemini)**
- **Vertex AI (cuenta enterprise/profesional):** **sin retención por defecto** de los datos de entrenamiento (no usa tus datos para entrenar modelos). Es la configuración recomendable para datos sensibles.
- **Gemini API / AI Studio (free/dev):** los datos pueden **retroalimentar el entrenamiento** salvo que se desactive la opción de mejora por voz o texto en la consola.
- **Disclaimer a mostrar:**
  > *"Los datos enviados a Google se procesan según tu cuenta. La cuenta **Vertex AI** no usa los datos para entrenar modelos. La cuenta **Gemini API/AI Studio (gratuita o de desarrollo)** puede utilizarlos; desactivá la recopilación para generar mejores modelos en la consola antes de subir documentos con datos sensibles."*

**☑️ Mistral**
- Plan Enterprise con retención de datos configurable; estándar mantiene logs de funcionamiento limitados. Validar retención contractual de la cuenta.
- **Disclaimer a mostrar:**
  > *"Los datos enviados a Mistral se procesan según tu cuenta. Validá la política de retención de tu plan (estándar vs enterprise) antes de procesar datos sensibles."*

**☑️ Modelos locales / self-host (ej. Paligemma, Ollama)**
- **No hay transferencia a terceros** si el modelo corre en infraestructura propia.
- **Disclaimer a mostrar:**
  > *"Esta configuración procesa los documentos con un modelo local en tu infraestructura. Los datos no salen de tu entorno. Esta es la opción recomendada para datos con mayor sensibilidad."*

### 2.3 Versión corta para UI (toast / checkbox de consentimiento)

> *"Los documentos que subás pueden ser procesados por un proveedor de IA de terceros y quedar sujetos a su política de retención. Confirmo que tengo autoridad para procesarlos."* `[Acepto]`

### 2.4 Texto para el módulo de administración de API keys

> **Uso de datos por proveedor**
>
> - **OpenAI:** estándar retiene 30 días · **Enterprise/ZDR no retiene**.
> - **Google Vertex:** **no entrena** con tus datos · **Gemini API/AI Studio:** puede entrenar salvo que se desactive.
> - **Modelos locales:** no transfieren datos fuera de tu red.
>
> *Al configurar una API key, se recomienda el plan que garantice **no retención / no entrenamiento** para ambientes con datos sensibles.*

---

## 3 · Metodología de esta redacción (respaldo del guión)

1. **Contexto medido:** uso real por proveedor (tabla §1) — el disclaimer no es genérico, refleja cómo opera la plataforma hoy.
2. **Dimensión legal anclada en lo verificable:** la retención y el entrenamiento son hechos contractuales de cada proveedor; el disclaimer **no inventa obligaciones**, describe la configuración de la cuenta.
3. **Cumplimiento de normas aplicables (a validar con Joaquín):**
   - **Ley 25.326 (AR):** datos sensibles requieren consentimiento explícito y tratamiento bajo finalidades lícitas.
   - **GDPR (UE):** transferencia internacional → requiere cláusulas contractuales tipo (SCC) o un marco de adecuación.
   - **Políticas de retención:** el procesador (proveedor) define plazos; el responsable (cliente) debe comunicarlo.
4. **Recomendación de configuración segura (default):** para datos sensibles usar **modelo local** o **plan Enterprise con Zero Data Retention**.

---

## 4 · Pendientes para cerrar el ticket

| # | Bloqueador | Depende de | Impacto |
|---|---|---|---|
| B1 | Confirmar qué planes de proveedor tiene hoy la organización (¿OpenAI con ZDR? ¿Vertex o Gemini API?) | Cliente / admin | Cambia el texto "por tipo de cuenta" (§2.2) |
| B2 | Revisión legal de Joaquín de los textos (§2.1–2.4) | Ticket 2 (consulta con Joaquín) | Aprobación final |
| B3 | Ubicación técnica del disclaimer (banner al subir, footer, admin de keys, o varios) | Devs + diseño | Alcance de implementación |
| B4 | Idioma adicional (¿inglés requerido?) | Producto | Versión bilingüe si aplica |
| B5 | Nombrar el responsable (data owner) que confirma autoridad de procesamiento | Cliente | Texto del consentimiento |

---

## 5 · Archivos relacionados

- Guión de la consulta a Joaquín: `guion-consulta-joaquin-datos-sensibles.md`
- Página de retención de los proveedores: OpenAI Help Center · Google Cloud (Vertex AI / data governance) · Mistral Trust & Security · alternativas: "Retention of inputs and outputs".