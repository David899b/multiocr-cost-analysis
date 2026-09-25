# Aviso de Privacidad y Seguridad de Datos — MultiOCR SaaS · Escenario A: el proveedor de IA retiene el contenido

Este aviso describe cómo MultiOCR procesa los documentos que el cliente envía para extracción de datos con IA en el escenario contratado (escenario A). El servicio está diseñado considerando el cumplimiento, la privacidad y la seguridad de los datos. Sin embargo, el cliente es responsable del uso del servicio y de la implementación de la tecnología en su organización: es responsabilidad del cliente cumplir toda ley y normativa aplicable en su jurisdicción (Ley 25.326, decretos y disposiciones reglamentarias, y toda norma sectorial aplicable).

## Promesa de tratamiento responsable

MultiOCR hace una promesa explícita sobre los datos del cliente, en línea con la práctica de mercado de los servicios de procesamiento documental con IA:

- MultiOCR no utiliza los documentos del cliente para entrenar, ajustar ni mejorar modelos de labIA.
- MultiOCR no utiliza los documentos del cliente para otro fin distinto del de prestar el servicio de extracción.
- MultiOCR no vende ni comparte los documentos del cliente con terceros salvo lo necesario para prestar el servicio (el proveedor de IA, en las condiciones de la sección 5).
- MultiOCR no reclama titularidad sobre los documentos del cliente: los documentos y los datos extraídos son y permanecen del cliente.

En este escenario A, **el proveedor de IA puede retener o utilizar el contenido** conforme a su propia política: por eso se lo informa como sub-procesador con transferencia internacional (sección 5). Las promesas anteriores se refieren al tratamiento que realiza MultiOCR como capa de extracción; no alcanzan al tratamiento posterior del proveedor.

## 1. Qué hace MultiOCR y cuál es su rol

MultiOCR es un servicio SaaS multi-tenant que ejecuta sobre la infraestructura de Concentrix / labIA (puerta de API: `https://www.concentrix.net.ar:2083/api`). Su función es técnica e intermediaria: recibe un documento (factura, remisión, contrato o comprobante), lo remite a un modelo de IA de un proveedor externo y devuelve al cliente el texto y los datos extraídos en formato JSON, listos para su revisión humana.

Rol legal. labIA / Concentrix actúa como Encargado del Tratamiento por cuenta y orden del cliente, que es el Responsable del Tratamiento: define la finalidad, decide qué documentos procesar y qué uso dar a los resultados. El proveedor de IA interviene como sub-procesador (sección 5).

Resumen del tratamiento:

| Etapa | Qué ocurre | Retención |
|---|---|---|
| Extracción (`/load`) | El documento se procesa en memoria y el resultado se devuelve en JSON | Sin persistencia de contenido en MultiOCR |
| Persistencia (`/submission`) | Solo si el cliente la envía, se guarda una copia asociada a su cuenta | Indefinida; borrado a demanda vía API |
| Proveedor de IA | El contenido se remite al modelo configurado y el proveedor puede retenerlo conforme a su política | Regida por las condiciones del sub-procesador |

## 2. Qué ocurre con los datos en este escenario

El contenido del documento se remite al proveedor de IA configurado (por ejemplo, OpenAI, Google Gemini, Anthropic Claude o DeepSeek, según el catálogo habilitado) bajo el plan contratado. Los términos de ese proveedor pueden contemplar la retención o el uso del contenido conforme a su política, incluida la mejora de sus propios servicios.

- MultiOCR no controla la política de retención del proveedor. Cuando corresponde, este aviso la informa y exige al proveedor condiciones de protección mediante acuerdos de procesamiento de datos (DPA) y cláusulas contractuales modelo aprobadas por la AAIP.
- El cliente que no desee que un tercero retenga el contenido debe contratar el escenario B (retención cero) o el escenario C (capa de extracción con JSON devuelto), que MultiOCR ofrece como alternativas.
- Se aplican las reglas de datos sensibles de la sección 6 y la transferencia internacional de la sección 5.

## 3. Cómo procesa MultiOCR los datos

### 3.1 Autenticación (clave de API)

Cada operación autentica al cliente mediante los encabezados de la API (`x-api-id` y el secreto de la cuenta). El secreto se almacena como hash unidireccional bcrypt, nunca en claro, y su uso se registra en los logs del servicio. La clave valida la suscripción y delimita el alcance de la cuenta.

### 3.2 Seguridad del dato en tránsito

Todos los endpoints de la API usan HTTPS para cifrar la información durante la transmisión.

### 3.3 Cifrado y procesamiento de los datos de entrada

Cuando el cliente envía un documento, MultiOCR arma de forma dinámica la instrucción (prompt) con el esquema y las reglas especiales de la cuenta, y remite el contenido al proveedor de IA configurado (OpenAI / Google Gemini / Anthropic Claude / DeepSeek, según el catálogo habilitado) para extraer texto, estructura y valores. El backend de MultiOCR no persiste el contenido en esta etapa: procesa en memoria y devuelve el resultado al cliente.

### 3.4 Recuperación de los resultados

El resultado se devuelve al cliente en formato JSON, autenticando la operación contra la misma clave que la originó, de modo que ningún otro cliente pueda acceder a esos datos.

### 3.5 Datos almacenados por MultiOCR

- Durante la extracción (`/load`): no se almacena el contenido del documento ni el resultado intermedio; el procesamiento se realiza en memoria.
- Solo si el cliente lo envía (`/submission`): si el cliente decide persistir los datos confirmados, se conserva una copia en la base de datos, asociada a la cuenta (`apiKeyId`) que los envió. La persistencia es una decisión del cliente.
- Múltiples clientes en la misma plataforma: los clientes comparten la infraestructura, pero sus datos están lógicamente aislados por `x-api-id`: cada cuenta solo puede acceder a sus propias configuraciones y submissions.
- Configuración y registros operativos: el servicio conserva la configuración de extracción de cada cuenta (esquema y reglas) y registros técnicos (proveedor de IA, modelo, conteo de tokens) sin contenido de los documentos. Estos registros se utilizan con fines de operación, facturación y diagnóstico del servicio.

### 3.6 Retención y borrado de datos

La política de retención actual del servicio es indefinida (no existe purga automática por tiempo de vida configurada en la base): los registros y submissions permanecen hasta su borrado explícito. El cliente puede eliminar sus datos de forma anticipada mediante la operación de borrado de la API (DELETE); esta eliminación es permanente y asociada a la cuenta que la solicita. El cliente puede asimismo solicitar la supresión de sus datos conforme a la sección 9.

## 4. Qué NO hace MultiOCR con los datos

- No entrena modelos con los documentos del cliente: el contenido procesado no se utiliza para entrenar, ajustar ni mejorar modelos de labIA.
- No utiliza los datos para otros fines: los documentos solo se procesan con la finalidad declarada de extracción.
- No conserva el contenido durante la extracción: en `/load` el documento y el resultado intermedio no se persisten.
- No bloquea ni anonimiza automáticamente: el servicio no cuenta con módulos DLP ni filtros previos de bloqueo/anonimización de contenido sensible (ver sección 6).

## 5. Proveedor de IA (sub-procesador) y transferencia internacional

- MultiOCR remite el contenido del documento al proveedor de IA configurado para la cuenta del cliente a fin de realizar la extracción.
- El proveedor (por ejemplo, OpenAI, Google Gemini, Anthropic Claude, DeepSeek u otro del catálogo habilitado, incluido el enrutado automático `auto` según el plan de la cuenta) puede estar situado fuera de la República Argentina: en ese caso, los datos pueden salir del país (art. 12, Ley 25.326). MultiOCR informa esta transferencia en este aviso y exige a su proveedor condiciones de protección mediante acuerdos de procesamiento de datos (DPA) y, cuando corresponde, cláusulas contractuales modelo aprobadas por la AAIP.
- La política de retención, uso y entrenamiento del proveedor es la propia de ese proveedor para el plan configurado y se documenta en el Anexo Técnico del paquete.

## 6. Datos sensibles: reglas de uso

- Regla general: no cargue documentos que contengan datos personales sensibles (art. 2º, Ley 25.326: origen racial o étnico, salud, ideología, religión, afiliación sindical, vida sexual, entre otros).
- Excepción: si el caso lo exige, solo con el consentimiento explícito, previo y documentado del titular, y restringido a la finalidad declarada (art. 7º, Ley 25.326).
- Conducta de la plataforma: MultiOCR informa al usuario sobre el manejo de los datos, pero no bloquea ni anonimiza la carga de forma automática. El cliente es responsable del tipo de datos enviados y de contar con base legal para su procesamiento.

## 7. Medidas de seguridad

- Cifrado en tránsito obligatorio: todo el tráfico corre exclusivamente sobre HTTPS.
- No persistencia en extracción: el payload y el resultado intermedio no se guardan durante `/load`.
- Aislamiento multi-tenant: validación y alcance estricto por `x-api-id` en cada operación, impidiendo el acceso entre distintos clientes.
- Credenciales protegidas: los secretos de cliente se almacenan con hash unidireccional (`bcrypt`), nunca en claro.

## 8. Responsabilidad del cliente y de los usuarios

- El cliente define la finalidad, los documentos a procesar y el uso de los resultados: es el Responsable del Tratamiento.
- El resultado de la extracción es generado por IA y, por su naturaleza probabilística, puede contener errores u omisiones; por lo tanto debe ser revisado y validado por una persona antes de su uso. No constituye asesoramiento legal, contable ni financiero.
- El cliente es responsable de cumplir la legislación aplicable en su jurisdicción, de obtener el consentimiento que corresponda sobre los titulares de los datos y de decidir la retención interna de los resultados.
- Dado que en este escenario el proveedor puede retener el contenido, el cliente debe evaluar si la política de retención de ese proveedor es aceptable para los documentos que procesa.
- Antes de usar el servicio en casos sensibles o de alto riesgo, se recomienda contar con revisión legal del uso previsto.

## 9. Derechos del titular de los datos (ARCO)

Todo titular puede ejercer los derechos de Acceso, Rectificación, Supresión y Oposición (arts. 14, 16 y 27, Ley 25.326) ante:

- el cliente, como Responsable del Tratamiento; y/o
- labIA / Concentrix, como Encargado del Tratamiento, en el contacto indicado al pie, para dar traslado de la solicitud y ejecutar la supresión de los datos persistidos.

MultiOCR atenderá las solicitudes dentro de los plazos legales y dará traslado al responsable (cliente) cuando corresponda, incluida la supresión de datos al término del vínculo contractual.

## 10. Vigencia y cambios

Este aviso entra en vigencia el 16/09/2026 y se revisará ante cualquier cambio en: proveedor de IA, políticas de retención de proveedores, arquitectura del servicio o normativa aplicable. Las modificaciones se publicarán con aviso previo en la plataforma.

## 11. Contacto y responsable

- Encargado del Tratamiento: labIA / Concentrix · [RAZÓN SOCIAL / DOMICILIO / CONTACTO — a completar]
- Responsable del Tratamiento: [CLIENTE — nombre de la empresa contratante]
- Contacto de labIA: [EMAIL / TEL]
- Referencias normativas: Ley 25.326 y Decreto 1558/2001 · Disp. AAIP 60-E/2016 · Res. AAIP 159/2018 · Res. AAIP 198/2023 · Res. AAIP 47/2018 · Ley 26.388 · CCyC art. 1106.