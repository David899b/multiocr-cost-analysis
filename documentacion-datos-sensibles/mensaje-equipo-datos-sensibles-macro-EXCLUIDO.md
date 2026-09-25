# Mensaje para el equipo — Datos sensibles · Multi OCR · Panorama Banco Macro · **[EXCLUIDO]**

> **ESTADO: EXCLUIDO del alcance (16/09/2026).** Las respuestas del equipo ya fueron recibidas y el panorama Banco Macro queda fuera del producto de demo. Documento archivado por trazabilidad; **no usar** como base para el aviso vigente. El aviso vigente es `disclaimer-oficial-puente-datos-sensibles.md` (genérico, para demo del laboratorio).

---

**Asunto:** [ARCHIVO — EXCLUIDO] Preguntas para cerrar el disclaimer de datos sensibles · Panorama Banco Macro

**Hola equipo,**

Estamos armando el disclaimer de datos sensibles para el panorama en el que ya venimos trabajando con **Banco Macro**. A diferencia de las pruebas anteriores (donde el documento se enviaba al LLM de terceros: OpenAI/Google/Mistral), en este modo **los modelos son del banco** y nuestro software solo hace el llamado de API: el documento pasa por nuestra herramienta y la respuesta se devuelve en JSON, pero **los datos no quedan en nuestro poder** — permanecen del lado del cliente.

Con lo que ya confirmaron, esto cambia el disclaimer en dos puntos centrales:
- Desaparece el bloque de "proveedor LLM" (retención/entrenamiento de terceros ya no aplica).
- Dejamos de ser "responsables del tratamiento" para ser una **capa de tránsito/orquestación**: el disclaimer pasa a declarar qué **no** hacemos (no custodiamos, no retenemos, no entrenamos).

Para redactarlo con precisión (sin suponer), necesito que confirmen los siguientes puntos:

## Preguntas

**1 · ¿Dónde queda el JSON de salida?**
El resultado del modelo (JSON) que nuestro software devuelve al banco, ¿queda **solo del lado de Macro** o nuestro software conserva también una copia (aunque sea temporal)? Esto define si declaramos "los datos (entrada y salida) permanecen íntegramente en el entorno del banco".

**2 · ¿Hay terceros en el tránsito de datos?**
En el camino `empleado de Macro → nuestro software → API del banco`, ¿existe **algún intermediario** que pueda tocar los bytes en tránsito (ej. hosting/cloud provider propio, VPN, gateway externo)? Si todo corre dentro de la infra del banco, se declara "sin transferencia a terceros".

**3 · ¿Qué metadatos guardamos y por cuánto tiempo?**
Confirmaron que solo se persisten **metadatos** (timestamps, IDs, tamaño, sin contenido). Necesito el detalle para el disclaimer: ¿qué campos exactamente, con qué fin y por cuánto tiempo (plazo de retención)? Si es posible, también si hay logs de auditoría con la operación (sin payload).

**4 · ¿Quién es jurídicamente "responsable del tratamiento" en esta relación?**
El banco es dueño de los modelos y de los datos. ¿Hay algún contrato/DPA firmado entre **Macro y labIA** (encargado/mero tránsito), o depende de legal? Necesitamos saber cómo nombrarnos en el disclaimer (ej. "procesador técnico interviniente", no "responsable").

**5 · ¿Bloqueamos, advertimos o solo informamos ante datos sensibles?**
En el modo Macro, ¿el sistema bloquea/advierte si detecta datos sensibles en el documento, o solo informa (igual que el modo general)? ¿Hay algún control de carga interna que debamos mencionar?

**6 · ¿El aviso es un texto previo a la carga (consentimiento del empleado/usuario) o solo un documento institucional Macro ↔ labIA?**
¿El empleado de Macro que sube el documento acepta un aviso al cargarlo, o el disclaimer es un anexo contractual entre las organizaciones? Esto define el formato (banner/consentimiento vs. cláusula anexa).

## Qué esperamos de ustedes
- Respuesta a **Q1–Q6** (si alguna no aplica, decirlo: no inventamos el dato).
- Confirmar si hay **documentación técnica** del flujo Macro (diagrama de red, DPA, contrato) para anclarlo.

## Contexto ya confirmado (para no volver a preguntarlo)
- Nuestro software corre **en la infraestructura del banco**.
- Se **persiste solo metadatos** (sin contenido del documento).
- El documento lo sube un **empleado de Macro**.
- Los modelos son del banco; nuestro software es capa de llamado de API (request → JSON).

Gracias. Con esto cerramos la redacción del disclaimer del panorama Macro.

**[Tu nombre]** · [rol] · [contacto]