# Aviso de Privacidad y Tratamiento por Inteligencia Artificial — Multi OCR Tool

---

## 1. Objeto y alcance

Este Aviso explica, de forma clara y previa a la carga de cualquier documento, cómo **Multi OCR Tool** trata los documentos (facturas, remisiones, contratos y archivos afines) que los usuarios suben **para extracción de datos con modelos de inteligencia artificial (IA)**.

Aplica a todas las cuentas y modalidades de procesamiento: modelos en la nube (API de terceros) y modelos locales (on-premise). Se actualizará cuando cambie el proveedor, la política de retención de un proveedor o la arquitectura del servicio.

## 2. Definiciones

- **Documento:** factura, remisión, contrato o comprobante subido por el usuario para extracción de datos.
- **Datos personales:** información referida a personas físicas o de existencia ideal determinadas o determinables (art. 2º, Ley 25.326).
- **Datos personales sensibles:** datos que revelan origen racial o étnico, opiniones políticas, convicciones religiosas, filosóficas o morales, afiliación sindical, información de salud o de vida sexual (art. 2º, Ley 25.326).
- **Proveedor LLM:** tercero que ejecuta el modelo de IA (OpenAI, Google, Mistral u otro) en la nube o localmente.
- **Procesamiento:** envío del documento al modelo de IA y recepción del resultado de extracción.

## 3. Qué hace la plataforma con el documento

Para prestar el servicio, el contenido del documento **se envía al proveedor LLM** configurado según la cuenta, y el resultado de extracción es devuelto al usuario. El procesamiento se realiza **únicamente** para cumplir la finalidad declarada de extracción de datos del documento.

## 4. Naturaleza de los datos contenidos en los documentos

Conforme a la Ley 25.326 y los criterios de la AAIP, los documentos típicamente procesados (facturas, remisiones, contratos) contienen **datos personales de carácter intermedio** (identificación, CUIT, domicilio, datos patrimoniales). **No son, por regla general, datos sensibles** en los términos del art. 2º. Si un documento contuviera datos que revelen salud, religión, ideología, afiliación sindical u origen racial, regirá lo dispuesto en el art. 7º de la Ley 25.326 y **el usuario no deberá cargarlo** salvo que cuente con el consentimiento explícito del titular o base legal válida.

## 5. Manera en que el proveedor trata los datos (retención y entrenamiento)

El tratamiento que realiza cada proveedor depende del **tipo de cuenta** y de las condiciones contractuales del proveedor, no de esta plataforma. Resumen vigente a la fecha de este Aviso:

| Escenario | ¿El proveedor entrena con los documentos? | Retención por defecto | Mitigación disponible |
|---|---|---|---|
| **OpenAI API** | No (toda la API, desde 2023) | Logs de abuso hasta 30 días | ZDR (Enterprise, aprobación previa) |
| **Google Gemini API** | No si hay cuenta pagada (billing activo) | Logs limitados (detección de abuso) | Vertex AI (región, VPC-SC, no entrenamiento) |
| **Mistral API** | No por defecto | Según DPA (30 días post-terminación) | ZDR en planes pagos |
| **Modelo local (on-premise)** | No | Sin envío a terceros | Aislamiento de red; cifrado local |

> Fuente: políticas y términos vigentes de OpenAI, Google y Mistral a la fecha. Se actualizan sin cambios contractuales que requieran aviso.

## 6. Transferencia internacional de datos

Cuando el procesamiento utiliza un proveedor en la nube, los datos pueden salir de la República Argentina y transferirse a un tercer país (art. 12, Ley 25.326). La plataforma:
- informa previamente esta transferencia en este Aviso;
- exige a sus proveedores condiciones de protección mediante acuerdos de procesamiento de datos (DPA) y, cuando corresponda, cláusulas contractuales modelo aprobadas por la AAIP (Disp. 60-E/2016 y Res. AAIP 198/2023);
- cuando el modelo corre en forma local, **no se produce transferencia internacional** porque el documento no abandona el entorno del usuario.

## 7. Base legal y consentimiento

El tratamiento de los datos contenidos en los documentos se apoya en:
- el **consentimiento libre, expreso e informado** del usuario al cargar el documento en la plataforma (art. 5º, Ley 25.326), prestado mediante la aceptación de este Aviso; y/o
- las excepciones legales aplicables (art. 5º incs. c y d, Ley 25.326) cuando los datos derivan de una relación contractual.

**Responsabilidad del usuario:** al subir un documento, el usuario declara contar con base legal o consentimiento para procesar los datos personales contenidos, **incluidos los de terceros** (clientes, proveedores, firmantes). La plataforma no verifica el contenido de cada documento ni asume la responsabilidad del usuario por datos de terceros cargados sin la base legal correspondiente.

## 8. Datos sensibles: reglas de uso

- **Regla general:** no cargue documentos que contengan datos personales sensibles (art. 2º, Ley 25.326).
- **Excepción:** si el caso lo exige, solo con el consentimiento explícito, previo y documentado del titular, y restringido a la finalidad declarada.
- La plataforma puede **bloquear la carga** o **advertir** en función de la configuración de cuenta y de los controles de seguridad activados.

## 9. Medidas de seguridad y minimización

La plataforma aplica medidas técnicas y organizativas razonables para proteger los documentos (confidencialidad, integridad y disponibilidad, art. 9º, Ley 25.326), incluida la **minimización de datos** (art. 4º, inc. 3): solo se envían al proveedor los datos necesarios para la extracción. Se recomienda al usuario:
- **anonimizar/seudonimizar** identificadores (DNI, CUIT, IBAN, teléfonos) cuando la extracción no los requiera;
- contratar la modalidad **local** para documentos con máxima confidencialidad; y
- conservar la **revisión humana** del resultado antes de su uso comercial o legal.

## 10. Derechos del titular de los datos (ARCO)

Todo titular puede ejercer los derechos de **Acceso, Rectificación, Supresión y Oposición** (arts. 14, 16 y 27, Ley 25.326) ante:
- la plataforma, en la dirección de contacto indicada al pie; y/o
- el proveedor LLM, conforme a sus propias políticas.

La plataforma atenderá las solicitudes dentro de los plazos legales y dará traslado a los proveedores cuando el dato esté en su poder.

## 11. Exactitud de los resultados

El resultado de la extracción se genera mediante modelos de IA y, por su naturaleza probabilística, **puede contener errores u omisiones**. No constituye asesoramiento legal, contable ni financiero. El usuario es el único responsable de revisar, validar y utilizar el resultado con criterio profesional.

## 12. Vigencia y cambios

Este Aviso entra en vigencia el [FECHA] y se revisará ante cualquier cambio en: proveedores LLM utilizados, políticas de retención de proveedores, arquitectura del servicio o normativa aplicable. Las modificaciones se publicarán con aviso previo en la plataforma.

## 13. Contacto y responsable

- **Responsable del tratamiento:** [NOMBRE / RAZÓN SOCIAL — pendiente de definición]
- **Domicilio:** [DOMICILIO — pendiente]
- **Contacto:** [EMAIL / TEL — pendiente]
- **Referencias normativas:** Ley 25.326 y Decreto 1558/2001 · Disp. AAIP 60-E/2016 · Res. AAIP 159/2018 · Res. AAIP 198/2023 · Res. AAIP 47/2018 · Ley 26.388 · CCyC art. 1106.

---

### Bloqueadores para cierre del documento (dependencia · responsable)
| # | Pendiente | Depende de | Responsable |
|---|---|---|---|
| B1 | Decidir proveedor(es) de modelo final y plan de cuenta | Decisión de producto/arquitectura | Producto/Arquitectura |
| B2 | Definir nombre/razón social y datos de contacto del responsable | Definición legal/comercial | Dirección |
| B3 | Aprobación legal de la redacción (este documento v0.1) | Consulta con Joaquín (ARG-597) | Joaquín |
| B4 | Definir ubicación UIs de los textos (banner, checkbox, toast, admin) | Ticket de UI | Producto/UX |
| B5 | Decidir idioma (es/en) para despliegue internacional | Estrategia de expansión | Producto |

### Referencias de precedentes usados como modelo
- Nino Legal (AR): DPA por proveedor con cláusulas AAIP 198/2023; responsabilidad del usuario por datos de terceros.
- ContratoAlquiler.com (ES): página de Transparencia IA; anonimización previa (DNI/IBAN/teléfonos); DPA con proveedores; no entrenamiento.
- Docusign AI Attachment: cláusulas de entrenamiento opt-out; revisión humana; conspicuidad.
- Thomson Reuters / LexisNexis (GenAI Terms): no entrenamiento con user content; verificación de outputs; aceptación de términos de terceros.
- Poder Judicial de la Ciudad de Buenos Aires: preferir ejecución local; anonimizar antes de enviar.