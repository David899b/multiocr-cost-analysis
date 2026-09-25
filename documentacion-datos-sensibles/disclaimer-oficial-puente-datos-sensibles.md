# Aviso de Privacidad y Seguridad de Datos — MultiOCR SaaS (Modalidad Puente)

Este aviso describe cómo MultiOCR procesa los documentos que el cliente envía para extracción de datos con IA. El servicio está diseñado considerando el cumplimiento, la privacidad y la seguridad de los datos. Sin embargo, el cliente es responsable del uso del servicio y de la implementación de la tecnología en su organización: es responsabilidad del cliente cumplir toda ley y normativa aplicable en su jurisdicción (Ley 25.326, decretos y disposiciones reglamentarias, y toda norma sectorial aplicable).

## Promesa de tratamiento responsable

MultiOCR hace una promesa explícita sobre los datos del cliente, en línea con la práctica de mercado de los servicios de procesamiento documental con IA:

- MultiOCR no utiliza los documentos del cliente para entrenar, ajustar ni mejorar modelos de labIA.
- MultiOCR no utiliza los documentos del cliente para otro fin distinto del de prestar el servicio de extracción.
- MultiOCR no vende ni comparte los documentos del cliente con terceros salvo lo necesario para prestar el servicio (proveedores de IA, en las condiciones que correspondan a cada escenario).
- MultiOCR no reclama titularidad sobre los documentos del cliente: los documentos y los datos extraídos son y permanecen del cliente.

Estas promesas se refieren al tratamiento que realiza MultiOCR como capa de extracción. El tratamiento por los proveedores de IA puede variar según el escenario de despliegue contratado por el cliente (sección 2), y por eso este aviso los describe a cada uno de forma diferenciada.

## 1. Qué hace MultiOCR y cuál es su rol

MultiOCR es un servicio SaaS multi-tenant que ejecuta sobre la infraestructura de Concentrix / labIA (puerta de API: `https://www.concentrix.net.ar:2083/api`). Su función es técnica e intermediaria: recibe un documento (factura, remisión, contrato o comprobante), lo remite a un modelo de IA y devuelve al cliente el texto y los datos extraídos en formato JSON, listos para su revisión humana.

Rol legal. En este esquema, labIA / Concentrix actúa como Encargado del Tratamiento por cuenta y orden del cliente, que es el Responsable del Tratamiento: define la finalidad, decide qué documentos procesar y qué uso dar a los resultados. Según el escenario, los proveedores de IA pueden intervenir como sub-procesadores del servicio (escenarios A y B) o quedar fuera del ámbito de tratamiento de MultiOCR (escenario C).

## 2. Escenarios de despliegue y qué ocurre con los datos

MultiOCR puede operar en tres escenarios de despliegue, que difieren en cómo se trata el contenido del documento del lado del proveedor de IA:

| Escenario | Qué hace el proveedor de IA con el contenido | Qué retiene MultiOCR | Dato clave para el aviso |
|---|---|---|---|
| A · El proveedor retiene el contenido | Puede conservar/custodiar el contenido conforme a su política (incluida posible mejora de servicios) | Solo metadatos operativos y lo que el cliente confirme (sección 3.5) | El proveedor es sub-procesador; puede haber retención por parte del tercero |
| B · El proveedor no retiene el contenido (ZDR) | Procesa y descarta el contenido tras la respuesta (retención cero o equivalente, sin entrenamiento) — **condición contractual expresa, no default** | Solo metadatos operativos y lo que el cliente confirme (sección 3.5) | El proveedor es sub-procesador, sin retención contratada (verificar plan) |
| C · MultiOCR como capa de extracción (modo puente) | La extracción devuelve el JSON al cliente; MultiOCR no persiste el contenido | Sin persistencia de contenido (extracción en memoria) | No hay proveedor de IA de MultiOCR que custodie la data: el JSON se devuelve al cliente y a su LLM |

### 2.1 Escenario A — El proveedor de IA retiene el contenido

En este escenario el contenido del documento se remite al proveedor de IA configurado (por ejemplo, OpenAI, Google Gemini, Anthropic Claude o DeepSeek) bajo el plan contratado, y los términos de ese proveedor pueden contemplar la retención o el uso del contenido conforme a su política, incluida la mejora de sus propios servicios.

- MultiOCR no controla la política de retención del proveedor: cuando corresponde, este aviso la informa y exige al proveedor condiciones de protección mediante acuerdos de procesamiento de datos (DPA) y cláusulas contractuales modelo aprobadas por la AAIP.
- El cliente que no desee que un tercero retenga el contenido debe solicitar el escenario B o utilizar el escenario C.
- Se aplican las reglas de datos sensibles de la sección 6 y la transferencia internacional de la sección 5.

### 2.2 Escenario B — El proveedor de IA no retiene el contenido (ZDR)

En este escenario el proveedor de IA está contratado y configurado bajo una modalidad de retención cero (zero data retention) o equivalente: el contenido se procesa para generar la respuesta y no se conserva para entrenamiento, mejora ni custodia posterior por parte del proveedor. Esta práctica es consistente con la de los principales proveedores de extracción documental del mercado (que retienen los resultados por ventanas acotadas de 24 a 48 horas y luego los eliminan automáticamente).

- La configuración de no retención es parte del plan contratado por el cliente con MultiOCR y se documenta en el Anexo Técnico.
- **La retención cero no es el comportamiento por defecto del proveedor**: debe contratarse y configurarse expresamente y verificarse con la documentación del proveedor antes de ofrecer este escenario (confirmado por el proveedor 17/09/2026). Si no se acredita esa condición en el plan contratado, corresponde aplicar el escenario A.
- MultiOCR no entrena ni reutiliza el contenido en ningún caso.
- Se aplican igualmente los metadatos operativos de la sección 3.5 y las reglas de datos sensibles de la sección 6.

### 2.3 Escenario C — MultiOCR como capa de extracción (modo puente, JSON devuelto)

En este escenario MultiOCR actúa como capa técnica pura: recibe el documento, arma la instrucción, llama al modelo de IA y devuelve el resultado en JSON al cliente. La data extraída se entrega al cliente (y al LLM del cliente que la consuma); MultiOCR solo la procesa en memoria y no la persiste en la extracción.

- No existe en este escenario un proveedor de IA de MultiOCR que custodie el contenido: el JSON se devuelve y el destino posterior (incluida su entrega a un LLM del cliente) es decisión y responsabilidad del cliente.
- La persistencia solo ocurre si el cliente decide enviar los datos confirmados vía `/submission` (sección 3.5).
- Este escenario es el que menores obligaciones de transferencia genera: sin remisión del contenido a un tercero de MultiOCR, no aplica sub-procesador del servicio.

## 3. Cómo procesa MultiOCR los datos

### 3.1 Autenticación (clave de API)

Cada operación autentica al cliente mediante los encabezados de la API (`x-api-id` y el secreto de la cuenta). El secreto se almacena como hash unidireccional bcrypt, nunca en claro, y su uso se registra en los logs del servicio. La clave valida la suscripción y delimita el alcance de la cuenta.

### 3.2 Seguridad del dato en tránsito

Todos los endpoints de la API usan HTTPS para cifrar la información durante la transmisión (aplica a los tres escenarios).

### 3.3 Cifrado y procesamiento de los datos de entrada

Cuando el cliente envía un documento, MultiOCR arma de forma dinámica la instrucción (prompt) con el esquema y las reglas especiales de la cuenta, y remite el contenido según el escenario seleccionado (sección 2) para extraer texto, estructura y valores. En los tres escenarios el backend de MultiOCR no persiste el contenido en la etapa de extracción: procesa en memoria y devuelve el resultado al cliente. El proveedor de IA, en tanto, puede procesar el contenido conforme a la modalidad contratada (retención posible en el escenario A, sin retención contractual en el B); según el proveedor, el contenido también puede ser parseado o indexado temporalmente cuando se utilizan determinadas features de plataforma (chat con archivos, bases de conocimiento), lo que se documenta en el Anexo Técnico del paquete.

### 3.4 Recuperación de los resultados

El resultado se devuelve al cliente en formato JSON, autenticando la operación contra la misma clave que la originó, de modo que ningún otro cliente pueda acceder a esos datos (aplica a los tres escenarios).

### 3.5 Datos almacenados por MultiOCR

- Durante la extracción (`/load`): no se almacena el contenido del documento ni el resultado intermedio; el procesamiento se realiza en memoria (aplica a los tres escenarios).
- Solo si el cliente lo envía (`/submission`): si el cliente decide persistir los datos confirmados, se conserva una copia en la base de datos, asociada a la cuenta (`apiKeyId`) que los envió. La persistencia es una decisión del cliente y no depende del escenario de proveedor.
- Múltiples clientes en la misma plataforma: los clientes comparten la infraestructura, pero sus datos están lógicamente aislados por `x-api-id`: cada cuenta solo puede acceder a sus propias configuraciones y submissions.
- Configuración y registros operativos: el servicio conserva la configuración de extracción de cada cuenta (esquema y reglas) y registros técnicos (proveedor de IA, modelo, conteo de tokens) sin contenido de los documentos. Estos registros se utilizan con fines de operación, facturación y diagnóstico del servicio.

### 3.6 Retención y borrado de datos

La política de retención actual del servicio es indefinida (no existe purga automática por tiempo de vida configurada en la base): los registros y submissions permanecen hasta su borrado explícito. El cliente puede eliminar sus datos de forma anticipada mediante la operación de borrado de la API (DELETE); esta eliminación es permanente y asociada a la cuenta que la solicita. El cliente puede asimismo solicitar la supresión de sus datos conforme a la sección 9.

## 4. Qué NO hace MultiOCR con los datos

- No entrena modelos con los documentos del cliente: el contenido procesado no se utiliza para entrenar, ajustar ni mejorar modelos de labIA.
- No utiliza los datos para otros fines: los documentos solo se procesan con la finalidad declarada de extracción.
- No conserva el contenido durante la extracción: en `/load` el documento y el resultado intermedio no se persisten.
- No bloquea ni anonimiza automáticamente: el servicio no cuenta con módulos DLP ni filtros previos de bloqueo/anonimización de contenido sensible (ver sección 6).

## 5. Proveedores de IA (sub-procesadores) y transferencia internacional

- Escenario A y B: MultiOCR remite el contenido del documento al proveedor de IA configurado para la cuenta del cliente a fin de realizar la extracción. Estos proveedores pueden ser OpenAI, Google Gemini, Anthropic Claude, DeepSeek u otro habilitado en el catálogo del servicio (el enrutado automático `auto` puede dirigir la llamada a cualquiera de ellos según el plan de la cuenta), y pueden estar situados fuera de la República Argentina: en ese caso, los datos pueden salir del país (art. 12, Ley 25.326). MultiOCR informa esta transferencia en este aviso y exige a sus proveedores condiciones de protección mediante acuerdos de procesamiento de datos (DPA) y, cuando corresponde, cláusulas contractuales modelo aprobadas por la AAIP.
- La política de retención, uso y entrenamiento de cada proveedor es la del propio proveedor para el plan configurado (retención posible en el escenario A, sin retención en el escenario B) y se documenta en el Anexo Técnico del paquete.
- Escenario C: no se remite el contenido a un proveedor de IA de MultiOCR. El cliente decide el destino posterior del JSON, incluida, si corresponde, la integración con un LLM propio; en ese caso las condiciones de ese LLM quedan fuera del ámbito de este aviso.

## 6. Datos sensibles: reglas de uso

- Regla general: no cargue documentos que contengan datos personales sensibles (art. 2º, Ley 25.326: origen racial o étnico, salud, ideología, religión, afiliación sindical, vida sexual, entre otros).
- Excepción: si el caso lo exige, solo con el consentimiento explícito, previo y documentado del titular, y restringido a la finalidad declarada (art. 7º, Ley 25.326).
- Conducta de la plataforma: MultiOCR informa al usuario sobre el manejo de los datos, pero no bloquea ni anonimiza la carga de forma automática. El cliente es responsable del tipo de datos enviados y de contar con base legal para su procesamiento. Esta regla aplica a los tres escenarios.

## 7. Medidas de seguridad

- Cifrado en tránsito obligatorio: todo el tráfico corre exclusivamente sobre HTTPS.
- No persistencia en extracción: el payload y el resultado intermedio no se guardan durante `/load`.
- Aislamiento multi-tenant: validación y alcance estricto por `x-api-id` en cada operación, impidiendo el acceso entre distintos clientes.
- Credenciales protegidas: los secretos de cliente se almacenan con hash unidireccional (`bcrypt`), nunca en claro.

## 8. Responsabilidad del cliente y de los usuarios

- El cliente define la finalidad, los documentos a procesar y el uso de los resultados: es el Responsable del Tratamiento.
- El resultado de la extracción es generado por IA y, por su naturaleza probabilística, puede contener errores u omisiones; por lo tanto debe ser revisado y validado por una persona antes de su uso. No constituye asesoramiento legal, contable ni financiero.
- El cliente es responsable de cumplir la legislación aplicable en su jurisdicción, de obtener el consentimiento que corresponda sobre los titulares de los datos y de decidir la retención interna de los resultados.
- En el escenario C, el cliente es responsable de las condiciones bajo las cuales su LLM recibe y trata el JSON devuelto.
- Antes de usar el servicio en casos sensibles o de alto riesgo, se recomienda contar con revisión legal del uso previsto.

## 9. Derechos del titular de los datos (ARCO)

Todo titular puede ejercer los derechos de Acceso, Rectificación, Supresión y Oposición (arts. 14, 16 y 27, Ley 25.326) ante:

- el cliente, como Responsable del Tratamiento; y/o
- labIA / Concentrix, como Encargado del Tratamiento, en el contacto indicado al pie, para dar traslado de la solicitud y ejecutar la supresión de los datos persistidos.

MultiOCR atenderá las solicitudes dentro de los plazos legales y dará traslado al responsable (cliente) cuando corresponda, incluida la supresión de datos al término del vínculo contractual.

## 10. Vigencia y cambios

Este aviso entra en vigencia el 16/09/2026 y se revisará ante cualquier cambio en: escenarios de despliegue ofrecidos, proveedores de IA, políticas de retención de proveedores, arquitectura del servicio o normativa aplicable. Las modificaciones se publicarán con aviso previo en la plataforma.

## 11. Contacto y responsable

- Encargado del Tratamiento: labIA / Concentrix · [RAZÓN SOCIAL / DOMICILIO / CONTACTO — a completar]
- Responsable del Tratamiento: [CLIENTE — nombre de la empresa contratante]
- Contacto de labIA: [EMAIL / TEL]
- Referencias normativas: Ley 25.326 y Decreto 1558/2001 · Disp. AAIP 60-E/2016 · Res. AAIP 159/2018 · Res. AAIP 198/2023 · Res. AAIP 47/2018 · Ley 26.388 · CCyC art. 1106.