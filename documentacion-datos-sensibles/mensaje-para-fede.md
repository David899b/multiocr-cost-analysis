# Mensaje para Fede — Tratamiento de datos vía ixHELLO para el aviso de privacidad de MultiOCR

> Listo para copiar/pegar. Completar saludo y ajustar tono si hace falta.

---

**Asunto:** ixHELLO y el tratamiento de datos de MultiOCR — 4 puntos para cerrar el aviso de privacidad

**Hola Fede,**

Estamos cerrando el **aviso de privacidad y seguridad de datos de MultiOCR** (ley 25.326, datos sensibles y tratamiento por terceros). Como ixHELLO es el asistente que usamos para conectar MultiOCR a los modelos de LLM, me ayudaría que me confirmes **cómo se trata el contenido de los documentos en la práctica**, para que el aviso y el Anexo Técnico digan algo verificable (hoy describo retención por proveedor, pero necesito validarlo contra el flujo real).

## Qué te pido (4 puntos)

1. **Qué proveedores/modelos** se alcanzan vía ixHELLO hoy y cuál usaríamos en la demo. El aviso contempla OpenAI, Google Gemini y NVIDIA — confirmame si es así o si hay otros.
2. **Retención real por proveedor/plan**: los términos actuales que tengamos contratados ¿garantizan **retención cero** (respaldaría el escenario B) o hay retención acotada de 24-48 hs (escenario A)?
3. **¿ixHELLO persiste o loguea el contenido del documento** en algún punto del flujo, o solo pasa la instrucción al modelo y devuelve el resultado? Esto define si podemos afirmar el escenario C (capa pura, sin persistencia del contenido).
4. Si ixHELLO debe **figurar por nombre** en el aviso como parte de la infraestructura, o lo dejamos solo dentro del Anexo Técnico.

## Contexto

- El aviso promete: no entrenamiento con datos de clientes, cifrado en tránsito, no persistencia del contenido durante la extracción (`/load`), aislamiento por `x-api-id` y derechos ARCO.
- Hay 3 escenarios documentados según qué pasa con el contenido del lado del proveedor (A: retiene · B: sin retención/ZDR · C: JSON directo al cliente).
- Esto **no reemplaza** los datos legales que precisa contratación (razón social de labIA/Concentrix y del cliente final) — eso va por otra vía.

## Bloqueador

Sin la confirmación de retención real por proveedor (punto 2) **no podemos ofrecer el escenario B como configurado**: sería una promesa sin basar. El resto (puntos 1, 3 y 4) ajusta la redacción, pero no la bloquea.

Cuando me pases los datos, actualizo aviso + Anexo Técnico, regenero PDF/HTML y queda listo para la demo.

¡Gracias!

**[Tu nombre]** · [rol] · [contacto]