# Evidencia web — DPAs publicados de iX Hello (Concentrix)

> Documento de trabajo (capa de evidencia del paquete). No se entrega al cliente.
> Propósito: contrastar las **5 necesidades de DPA** de iX Hello contra lo que está **publicado y verificable en la web** del proveedor (24/09/2026).

## 1. Qué se revisó (fuentes, versiones, fechas)

| Documento | URL | Versión / fecha | Estado del texto |
|---|---|---|---|
| Subscription Agreement | `https://www.ixhello.com/SubscriptionAgreement` | v1.2 · 28/03/2025 | Legible (requiere User-Agent de navegador; sin UA el WAF devuelve "Illegal request") |
| Data Protection Addendum (DPA) | `https://policies.ixplatform.ai/DataProtectionAddendum.pdf` | v1.1 · 28/03/2025 | Legible |
| Privacy Policy | `https://policies.ixplatform.ai/privacypolicy.pdf` | v1.1 · 28/03/2025 | Legible |
| Acceptable Use Policy | `https://policies.ixplatform.ai/acceptableusepolicy.pdf` | v1.1 · 28/03/2025 | Legible |
| Service Level Agreement | `https://policies.ixplatform.ai/ServiceLevelAgreement.pdf` | v1.1 · 12/09/2024 | Legible |

Adicional: LATAM local Privacy Policy referenciada en `https://www.concentrix.com/legal/` (sección LATAM) y `https://www.concentrix.com/wp-content/uploads/2024/04/CNX-California-Privacy-Policy-v2.0.pdf` (California).

## 2. Contraste: 5 necesidades DPA vs. documentación pública

| # | Necesidad | Estado | Qué hay público (cita clave) | Qué falta |
|---|---|---|---|---|
| 1 | DPA como procesador (no-entrenamiento, breach, borrado, retención) | ⚠️ **Parcial — hallazgo crítico** | DPA procesador completo: solo procesa según instrucciones documentadas (DPA §3.1.2); notifica breach "without undue delay" (DPA §8); devuelve/borra en 30 días post-cese con certificación (DPA §10); derecho de auditoría (DPA §11). SA §2.9 incorpora el DPA, §2.10 Concentrix = Processor (GDPR), §2.11 = service provider CCPA. SA §5.2: borrado post-término "unless legally required to retain it" | **El Subscription Agreement §5.3 permite explícitamente el ENTRENAMIENTO con los inputs** (ver §4). Sin aclaración escrita, NO puede afirmarse "no entrenamiento" |
| 2 | Lista de sub-procesadores | ❌ **GAP** | Mecanismo contractual sí está: autorización general escrita con aviso previo de 30 días para cambios (DPA Appendix 2.1, Clause 9 Option 2) + due diligence obligatoria (DPA §6) | El **Appendix 1 del DPA es una plantilla VACÍA** (lista de subprocesadores en blanco, "to be completed by the Parties"); el Privacy Policy §5 solo menciona categorías ("...and/or Artificial Intelligence providers") sin nombres; el SA §2.5 dice que los third-party **no actúan como sub-procesadores entre sí** y que el cliente es responsable. Falta la lista operativa rellenada (OpenAI / Anthropic / Google / DeepSeek / NVIDIA / Mistral…) |
| 3 | Retención cero (ZDR) | ❌ **No existe** | — | Ningún documento público contempla retención cero. SA §5.2: retención durante el término + 30 días posteriores (borrado si el cliente lo pide dentro de esos 30 días). Privacy §8: retención "only as necessary… or for other legitimate business purposes". **Confirma el ticket INC000029619478: ZDR solo por contratación expresa** |
| 4 | Transferencia internacional | ✅ **Cubierto** | Privacy §6: "some of your Personal Data is transferred and stored in the United States… may be accessed by Concentrix IT support team located in India, the Philippines and the US", cubierto por SCC 2021/914 + UK Addendum + Swiss Addendum. DPA §12 + BCRs → SCC 2021/914. Para LATAM: Privacy §1 remite a la política LATAM de `concentrix.com/legal/` (aplica solo donde Concentrix tiene presencia comercial) + "technical measures to limit the processing of this category of personal data" | — (cubierto de forma genérica; detalle por feature es opcional) |
| 5 | Logging / metadata | ⚠️ **Parcial** | Privacy §2: Log Data (IP, browser, fecha/hora, request, interacción), Usage Data, Device, Cookies, Analytics. SA §2.7: Analytics que NO identifica personalmente ("for avoidance of doubt, Analytical Information does not include any information that personally identifies the Client or any Authorized User") | No especifica **duración** del log ni si alguna feature retiene **contenido de prompts/outputs**; el DPA Appendix 1 (retención) está en blanco |

## 3. Citas textuales de referencia (capa evidencia)

**Subscription Agreement v1.2 (28/03/2025) — `https://www.ixhello.com/SubscriptionAgreement`**

- §2.5 Third-Party Services: *"Concentrix and Third-Party providers do not act as processors or sub-processors of Personal Data for each other. The Client assumes all liability for the use of Third-Party Services… The Client is responsible for instructing Third-Party providers on the use and protection of Client Data."*
- §2.9 *"the data policies outlined in the Data Protection Addendum, which is incorporated by reference into this Agreement… If Concentrix discovers or is notified of a security breach involving Client Data, it will promptly notify the Client."*
- §2.10 *"Concentrix will act as a Processor as defined under GDPR and applicable data protection laws. The terms in the Data Protection Addendum will govern the processing of this Personal Data."*
- §2.11 CCPA: Concentrix puede ser considerada *"service provider"* bajo CCPA.
- §5.1: "Concentrix Data" incluye *"training datasets, model parameters, output data"* (evidencia de que el ecosistema contempla entrenamiento).
- §5.2 Client Data: *"Client Data is owned solely by the Client… Upon the Client's request within 30 days after termination or expiration of this Agreement, Concentrix will provide access to Client Data. After this period, Concentrix is not obligated to maintain the Client Data and will delete or destroy all copies unless legally required to retain it."*
- §5.3 Outputs (**hallazgo crítico**): *"Concentrix and its third-party providers may utilize Inputs to train and artificial intelligence ("AI") and/or generative artificial intelligence ("GenAI") models to improve Services as specified in this Agreement."*

**Data Protection Addendum v1.1 (28/03/2025) — `https://policies.ixplatform.ai/DataProtectionAddendum.pdf`**

- Modelo: Company = Controller / Vendor (Concentrix) = Processor.
- §3.1.2: *"not Process Company Personal Data other than on the relevant Company Group Member's documented instructions"* (excepto exigencia legal).
- §8: notificación de breach "without undue delay"; §10: devolución/borrado en 30 días con certificación; retención solo "to the extent required by Applicable Laws" (§10.3).
- §12 + Appendix 2: EU SCC 2021/914 (Module 2), UK Addendum, Swiss Addendum; Clause 9 Option 2 → aviso previo escrito de 30 días para cambio de sub-procesadores (Appendix 2.1, 2B); §6.3 due diligence previa.
- Appendix 1 (detalles de procesamiento + **lista de sub-procesadores**): **plantilla sin completar**.
- Annex II (2J): medidas TOMs *"[To be completed with Product owner and operations]"* — en blanco.
- §13.3 Order of Precedence: el DPA prevalece en caso de inconsistencia con otros acuerdos.

**Privacy Policy v1.1 (28/03/2025) — `https://policies.ixplatform.ai/privacypolicy.pdf`**

- §1 LATAM: remite a la política local LATAM de `concentrix.com/legal/`; *"Concentrix has established technical measures to limit the processing of this category of personal data"* (datos sensibles); aplica solo donde Concentrix tiene presencia comercial.
- §2: Log Data / Usage Data / Device / Cookies / Analytics.
- §5: proveedores incluyen *"other information technology and/or Artificial Intelligence providers"*.
- §6: transferencias (ver §2 fila 4); §8 retención "only as necessary".
- Contactos: DPO global `DPO@Concentrix.com`; LATAM `proteccion.dedatos@concentrix.com`. SA §10.4 adicional: `legalnotices@concentrix.com`; soporte iX Hello: `ix_hello_support@concentrix.com`.

**Acceptable Use Policy v1.1 (28/03/2025)**

- §4.a: *"Any attempt to Jailbreak or Manipulate the underlying LLM model serving the Services are strictly prohibited."* → **confirma la existencia de un LLM de terceros subyacente**.
- §7: el cliente no puede usar Outputs para desarrollar modelos competidores (no limita a Concentrix usar Inputs para entrenar — sentido inverso).

## 4. Hallazgo crítico: SA §5.3 vs. DPA §3.1.2 (ambigüedad contractual)

- El **DPA §3.1.2** limita el procesamiento a instrucciones documentadas del controlador, y el **DPA §13.3** da precedencia al DPA sobre otros acuerdos en caso de inconsistencia.
- El **SA §5.3** habilita de forma expresa a Concentrix *y a sus terceros proveedores* a usar los Inputs para **entrenar modelos de IA/GenAI** ("as specified in this Agreement").
- La cláusula §5.3 no aparece condicionada a planes "enterprise/ZDR", ni ofrece opt-out, ni excluye datos personales — es una habilitación genérica por defecto.
- Impacto en disclaimers (resuelto 24/09/2026 con Legal — Joaquín): la redacción vigente de los avisos es la aprobada y no se modificó. Este hallazgo queda documentado como observación contractual para tener presente en negociaciones futuras (planes enterprise, cláusulas de exclusión de entrenamiento si el cliente lo exige).

## 5. Preguntas esperadas con respuestas para la demo

- **"¿No dice el DPA que solo procesa según instrucciones?"** — Sí (DPA §3.1.2) y el DPA prevalece sobre el SA (§13.3). Pero §5.3 del SA habilita entrenamiento con inputs y la relación entre ambas cláusulas no está resuelta en los documentos públicos → se requiere aclaración de Legal + del proveedor. Ver §4.
- **"¿Quién es el sub-procesador real del LLM?"** — No consta públicamente: el Anexo 1 del DPA está vacío y el SA §2.5 exime a Concentrix de responsabilidad sobre terceros. Verificado indirectamente: la AUP §4.a confirma un "underlying LLM" de terceros.
- **"¿Puedo exigir retención cero o residencia de datos?"** — No por contrato estándar: el SA §5.2 retiene durante el término (+30 días post), Privacy §8 retención "as necessary", y los datos residen en US con acceso desde India/Filipinas/US (Privacy §6). Cualquier ZDR/residency es **negociación expresa**, no default.
- **"¿Qué pasa si el cliente es de LATAM / hay datos personales sensibles?"** — Privacy Policy LATAM aplica donde Concentrix tiene presencia comercial y declara medidas técnicas para "limitar el procesamiento" de esa categoría; CCPA → Concentrix service provider (no vende, §2 del DPA). La extracción `/load` de MultiOCR se mantiene como sin-persistencia; features de plataforma (knowledge bases) pueden indexar (matiz ya agregado a los avisos el 17/09/2026).

## 6. Bloqueadores / decisiones abiertas (con responsable)

> **Actualización 24/09/2026:** Legal (Joaquín) ya fue consultado y la lista de proveedores es el catálogo `vnextRuntime` provisto por el usuario (34 modelos iniciales de OpenAI/Anthropic/Gemini/DeepSeek + `auto`). Los puntos 1 y 2 quedan **cerrados**; el matiz de SA §5.3 queda documentado como observación (no como bloqueador de redacción, que ya fue aprobada).

| # | Punto | Estado | Responsable |
|---|---|---|---|
| 1 | SA §5.3 (entrenamiento con inputs) vs. DPA §3.1.2: interpretación | **Cerrado 24/09/2026** — resuelto con Legal (Joaquín) con la info disponible; redacción vigente de los avisos es la aprobada | Legal (Joaquín) |
| 2 | Lista de sub-procesadores | **Cerrado 24/09/2026** — catálogo `vnextRuntime` provisto por el usuario; secciones 5 de puente y escenarios A/B alineadas (sin NVIDIA/Mistral, mencionado el enrutado `auto`) | Usuario / Operaciones |
| 3 | Confirmar ZDR por plan/contrato concreto antes de ofrecer Escenario B | Vigente como **condición de oferta**: el Escenario B ya la expresa ("verificar plan", confirmado 17/09/2026) | Operaciones + Comercial |
| 4 | Regenerar HTML/PDF/DOCX de los avisos desde los .md editados | En curso 24/09/2026 | — |

## 7. Tickets / dependencias

- **Ticket INC000029619478** (ixHello, 17/09/2026) — ya respondido: no retención cero por default, no es pass-through puro. Este anexo complementa la parte **contractual pública**.
- **Nueva consulta pendiente al proveedor** (proponer ticket vía Federico Albertengo): (a) lista rellenada de sub-procesadores; (b) aclaración de SA §5.3 sobre entrenamiento; (c) DPA/ZDR plan enterprise si aplica.
- Ticket de disclaimer ↔ consulta legal (Joaquín) sobre la ambigüedad §5.3: **dependiente una de la otra** para fijar la redacción final de los escenarios A/B.

## 8. Checklist de cierre

- [x] Descargadas y leídas las 5 fuentes públicas (SA, DPA, Privacy, AUP, SLA) + verificación de WAF (User-Agent requerido en ixhello.com).
- [x] Contraste 5 necesidades vs. lo público (tabla §2).
- [x] Hallazgo crítico documentado (§4).
- [x] Legal (Joaquín) consultado 24/09/2026 — redacción vigente aprobada (punto 1 de bloqueadores cerrado).
- [x] Lista de sub-procesadores = catálogo `vnextRuntime` provisto por el usuario; secciones 5 de puente y escenarios A/B alineadas (sin NVIDIA/Mistral; enrutado `auto` mencionado).
- [ ] ZDR del Escenario B: mantiene la condición de "verificar plan" antes de ofrecerlo (depende de Operaciones/Comercial al momento de contratar).
- [x] HTML/PDF/DOCX regenerados desde los .md actualizados (24/09/2026) — puente (HTML/PDF), escenarios A y B (HTML/PDF/DOCX).