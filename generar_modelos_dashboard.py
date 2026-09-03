#!/usr/bin/env python3
"""
Genera el dashboard de MODELOS de MultiOCR (3 vistas):
  1. Catalogo por pasos del pipeline de extraccion (modelos propios vs oferta a clientes)
  2. Comparativa de costos/calidad de modelos candidatos
  3. Gestion por cliente/esquema (que modelo usa cada cliente y su consumo)

Se alimenta de production_data/{configs,ailogs}.json reales.
Uso: python3 generar_modelos_dashboard.py [--salida path]
"""

import argparse
import json
import os
from collections import Counter, defaultdict

AQUI = os.path.dirname(os.path.abspath(__file__))
CONFIGS = os.path.join(AQUI, 'production_data', 'configs.json')
AILOGS = os.path.join(AQUI, 'production_data', 'ailogs.json')
SALIDA_DEF = os.path.join(AQUI, 'modelos_dashboard.html')

# ----------------------- Catalogo de modelos por paso -----------------------
# Pipeline de extraccion de MultiOCR: cada documento pasa por estos pasos.
# "propio" = modelo interno / edge (sin costo API, privacidad), 
# "cliente" = modelo cloud que se ofrece a los clientes como servicio.
PASOS = [
    {
        "id": "ocr",
        "n": 1,
        "nombre": "OCR / Captura de la imagen",
        "desc": "Convierte la imagen o PDF del documento en texto / bounding boxes. Paso previo cuando se usa un LLM no multimodal.",
        "propios": [
            {"modelo": "Tesseract (local)", "tipo": "OCR clásico",
             "modal": "Texto", "vel": "Rápido", "calidad": 3,
             "costo": "$0", "disp": "Interno (edge)", "nota": "Sin costo, offline, pero sensible a baja calidad de imagen."},
            {"modelo": "Paligemma (edge)", "tipo": "VLM local",
             "modal": "Multimodal", "vel": "Media", "calidad": 3,
             "costo": "$0", "disp": "Interno (edge)", "nota": "VLM liviano que puede leer imagen directamente en el dispositivo."},
        ],
        "cliente": [
            {"modelo": "Google Vision OCR", "tipo": "OCR cloud",
             "modal": "Multimodal", "vel": "Alta", "calidad": 5,
             "costo": "1.50 USD/1K páginas", "disp": "Cloud", "nota": "OCR maduro con muy buena precisión en documentos."},
            {"modelo": "Gemini / GPT-4o (nativo)", "tipo": "LLM multimodal",
             "modal": "Multimodal", "vel": "Media", "calidad": 5,
             "costo": "Según modelo", "disp": "Cloud", "nota": "Leen la imagen directamente; eliminan el paso OCR separado."},
        ],
        "recomendado": "Gemini-3-Flash (multimodal nativo) elimina la necesidad de OCR separado.",
    },
    {
        "id": "extraccion",
        "n": 2,
        "nombre": "Extracción LLM de campos",
        "desc": "Toma el texto/contexto y devuelve el JSON estructurado siguiendo el schema del cliente (configName + specialRules).",
        "propios": [
            {"modelo": "Qwen2.5:14b (Ollama)", "tipo": "LLM local",
             "modal": "Texto", "vel": "5-8 t/s", "calidad": 4,
             "costo": "$0", "disp": "Interno (servidor)", "nota": "Calidad muy buena local, sin costo API ni fuga de datos. No multimodal."},
            {"modelo": "Qwen2.5:32b (Ollama)", "tipo": "LLM local",
             "modal": "Texto", "vel": "2-4 t/s", "calidad": 4,
             "costo": "$0", "disp": "Interno (servidor)", "nota": "Calidad cercana a cloud, requiere GPU potente."},
            {"modelo": "Gemma2:9b (local)", "tipo": "LLM local",
             "modal": "Texto", "vel": "Rápida", "calidad": 3,
             "costo": "$0", "disp": "Interno (servidor)", "nota": "Alternativa liviana de Google."},
        ],
        "cliente": [
            {"modelo": "gpt-5-mini (OpenAI)", "tipo": "LLM cloud",
             "modal": "Multimodal", "vel": "~80 t/s", "calidad": 5,
             "costo": "0.15/0.60 USD M tokens", "disp": "Cloud (actual)", "nota": "MODELO ACTUAL en producción (98% de llamadas)."},
            {"modelo": "gemini-3-flash", "tipo": "LLM cloud",
             "modal": "Multimodal", "vel": "~200 t/s", "calidad": 4,
             "costo": "0.10/0.40 USD M tokens", "disp": "Cloud", "nota": "Recomendado por costo: hasta 92% más barato que gpt-5 mini."},
            {"modelo": "GPT-4o-mini", "tipo": "LLM cloud",
             "modal": "Multimodal", "vel": "~160 t/s", "calidad": 4,
             "costo": "0.15/0.60 USD M tokens", "disp": "Cloud", "nota": "Buen balance costo/calidad multimodal."},
            {"modelo": "DeepSeek-Chat", "tipo": "LLM cloud",
             "modal": "Texto", "vel": "~60 t/s", "calidad": 4,
             "costo": "Bajo", "disp": "Cloud", "nota": "Muy barato, sin multimodal."},
        ],
        "recomendado": "Mantener gpt-5-mini para calidad, valorar gemini-3-flash para ahorro de costo.",
    },
    {
        "id": "validacion",
        "n": 3,
        "nombre": "Estructuración / Validación",
        "desc": "Corrige el JSON: valida tipos, aplica specialRules, completa campos vacíos y detecta alucinaciones o inventos.",
        "propios": [
            {"modelo": "Reglas + schema (determinístico)", "tipo": "Lógica local",
             "modal": "Texto", "vel": "Instantáneo", "calidad": 5,
             "costo": "$0", "disp": "Interno", "nota": "Validación por schema/types sin costo. Primera línea de defensa."},
            {"modelo": "Qwen2.5:7b (lint)", "tipo": "LLM local",
             "modal": "Texto", "vel": "Rápida", "calidad": 3,
             "costo": "$0", "disp": "Interno", "nota": "Recorre el JSON en busca de inconsistencias."},
        ],
        "cliente": [
            {"modelo": "Juez LLM (gpt-4o-mini)", "tipo": "LLM cloud",
             "modal": "Multimodal", "vel": "Media", "calidad": 4,
             "costo": "Bajo", "disp": "Cloud", "nota": "Valida contra la imagen original para detectar alucinaciones."},
            {"modelo": "gpt-5-mini (recheck)", "tipo": "LLM cloud",
             "modal": "Multimodal", "vel": "~80 t/s", "calidad": 5,
             "costo": "Costo doble", "disp": "Cloud", "nota": "Segunda pasada para casos críticos (facturas/legales)."},
        ],
        "recomendado": "Validacion determinística por schema siempre; LLM-juez solo en esquemas críticos.",
    },
]

# ----------------------- Comparativa de modelos (Vista 2) -----------------------
# Basada en MODEL_COMPARISON_DEEP.md (17 modelos) + datos reales de produccion.
COMPARATIVA = [
    # (modelo, provider, calidad, velocidad, costo_usd_mes, multimodal, tipo, estado)
    ("Qwen2.5:7b", "Ollama local", 3, "10-15 t/s", 0.0, "No", "Propio", "Oferta"),
    ("Qwen2.5:14b", "Ollama local", 4, "5-8 t/s", 0.0, "No", "Propio", "Oferta"),
    ("Qwen2.5:32b", "Ollama local", 4, "2-4 t/s", 0.0, "No", "Propio", "Oferta"),
    ("Llama-3.1-8b", "Groq", 3, "721 t/s", 0.51, "No", "Cliente", "Oferta"),
    ("Gemma2-9b", "Groq", 3, "400 t/s", 1.62, "No", "Cliente", "Oferta"),
    ("Gemini-1.5-Flash", "Google", 4, "190 t/s", 1.39, "Sí", "Cliente", "Oferta"),
    ("DeepSeek-Chat", "DeepSeek", 4, "60 t/s", 1.62, "No", "Cliente", "Oferta"),
    ("Mixtral-8x7b", "Groq", 3, "300 t/s", 1.94, "No", "Cliente", "Oferta"),
    ("GPT-4o-mini", "OpenAI", 4, "160 t/s", 2.79, "Sí", "Cliente", "Oferta"),
    ("gemini-3-flash-preview", "Google", 4, "200 t/s", 2.79, "Sí", "Cliente", "EN PROD"),
    ("Llama-3.1-70b", "Groq", 4, "316 t/s", 5.47, "No", "Cliente", "Oferta"),
    ("Claude-3-Haiku", "Anthropic", 4, "100 t/s", 5.52, "Sí", "Cliente", "Oferta"),
    ("gpt-5-mini-2025-08-07", "OpenAI", 5, "80 t/s", 7.43, "Sí", "Cliente", "EN PROD"),
    ("Claude-3.5-Haiku", "Anthropic", 5, "80 t/s", 17.66, "Sí", "Cliente", "Oferta"),
    ("Gemini-1.5-Pro", "Google", 5, "100 t/s", 23.23, "Sí", "Cliente", "Oferta"),
    ("GPT-4o", "OpenAI", 5, "50 t/s", 46.45, "Sí", "Cliente", "Oferta"),
    ("Claude-Sonnet-4", "Anthropic", 5, "40 t/s", 66.24, "Sí", "Cliente", "Oferta"),
    ("mistral-large-3-675b", "Mistral", 5, "40 t/s", 40.0, "Sí", "Cliente", "Uso puntual"),
    ("Paligemma", "Google (edge)", 3, "Media", 0.0, "Sí", "Propio", "EN PROD (edge)"),
]

# ----------------------- Paquetes propuestos (Vista 4) -----------------------
# Basado en investigacion web 2026 (OCR de ultima generacion + precios oficiales).
#
# A) Modelos OCR especializados de ultima generacion (self-host, costo de inferencia ~$0,
#    SOTA en OmniDocBench v1.6). Son los candidatos para reemplazar el paso 1 (OCR) y
#    parte del paso 2 (extraccion) sobre imagenes/PDFs directamente.
OCR_SOTA_2026 = [
    # (modelo, params, OmniDocBench, Real5, tipo_paradigma, enfoque)
    ("NaviDC-OCR", "1.2B", 96.87, 90.72, "Decoupled VLM", "Layout segmentation + deformation-aware; digital y camara"),
    ("OvisOCR2", "0.8B", 96.58, 92.29, "End-to-end VLM", "Markdown en orden de lectura; 1 pasada, SOTA e2e"),
    ("PaddleOCR-VL-1.6", "0.9B", 96.33, 93.19, "Pipeline VLM", "SOTA en Real5 (escaneo real); 100+ idiomas, sellos/tablas"),
    ("Qianfan-OCR", "4B", 93.90, "—", "Pipeline VLM", "Mejor en KIE (extraccion estructurada de campos)"),
    ("MinerU2.5-Pro", "1.2B", 95.75, "—", "Pipeline VLM", "Fusion multi-modelo, robusto"),
    ("GLM-OCR", "0.9B", 95.22, 90.32, "Pipeline VLM", "Buen balance estabilidad/precision"),
]
# (nota: NaviDC/OvisOCR2/PaddleOCR-VL estan dentro del top de la liderazgo OmniDocBench v1.6 2026)

# B) Costo LLM-OCR por 1.000 paginas (2026) - cifras verificadas de precios oficiales.
#    Ref: conversiones page->token (258 entradas/pagina) + output por pagina (~750 tok).
COSTO_OCR_PAGINA = [
    # (modelo, proveedor, usd_1000_pag, multimodal, nota)
    ("Gemini 2.5 Flash-Lite", "Google", 0.33, "Sí", "El camino pagina->texto mas barato publicado"),
    ("GPT-5.4-nano (batch)", "OpenAI", 0.84, "Sí", "Bajo el OCR dedicado; turno 24h"),
    ("GPT-5.4-nano", "OpenAI", 1.67, "Sí", "Primer LLM que iguala al OCR dedicado ($1.50)"),
    ("OCR dedicado (AWS/Azure/Google)", "Cloud", 1.50, "—", "Referencia clasica, plana por pagina"),
    ("GPT-5.4-mini", "OpenAI", 5.19, "Sí", "Eleccion habitual para extraccion por volumen"),
    ("Claude Haiku 4.5", "Anthropic", 5.31, "Sí", "JSON confiable a costo medio"),
    ("Claude Sonnet 4.6", "Anthropic", 15.93, "Sí", "Requiere razonamiento real sobre el doc"),
]

# D) Paquetes costo/efectivos propuestos (recomendados por investigacion web 2026).
#
# CLAVE DE DISEÑO: el poder del modelo ESCALA con la COMPLEJIDAD del documento/esquema.
# No todos los documentos necesitan el mismo modelo. Se agrupan por complejidad usando
# el numero de specialRules como proxy (1-2 reglas = sencillo; 3-5 = medio; 6+ = alto/complejo)
# y se asignan ejemplos reales de los esquemas de produccion de cada cliente.
#
# Precios expresados en USD (marcador internacional) y en ARS (dolar oficial venta BNA 2026-09-02).
TIPO_CAMBIO_ARS = 1535.0  # ARS por 1 USD (dolar oficial venta, BNA)

# Complejidad de un esquema segun su cantidad de specialRules (proxy real de produccion).
# Cada esquema de la base MultiOCR encaja en uno de estos bandos:
#  - sencillo  (1-2 reglas): Ticket Supermercado, Ticket espectaculos, CV (1 rule), Figurita, Test
#  - medio     (3-5 reglas): Servicios Publicos, Expense, Factura, Demo Banco Macro (5), CV (2-3)
#  - complejo  (6+ reglas):  Comprobante de pago (8), Demo Banco Macro (8), Comprobante de pago demo (8)
NIVEL_COMPLEJIDAD = {
    "sencillo": {
        "etiqueta": "Sencillo",
        "rango": "1-2 reglas",
        "ejemplos": ["Ticket Supermercado", "Ticket espectáculos", "CV", "Figurita Mundial 2026", "Test"],
        "modelos": [
            {"m": "Gemini 2.5 Flash-Lite", "paso": "OCR + extracción (1 pasada)", "usd": "$0.33/1K pág"},
            {"m": "GPT-5.4-nano (batch)", "paso": "OCR + extracción (batch)", "usd": "$0.84/1K pág"},
            {"m": "PaddleOCR-VL-1.6 (self-host)", "paso": "Paso 1 · OCR local SOTA", "usd": "$0 / GPU"},
        ],
        "costo_usd_final": "≈ $0.33-0.84 por 1.000 pág",
        "ventaja": "Input barato ($0.10/M); el modelo liviano basta para campos simples.",
        "riesgo": "Si la imagen está degradada, el LLM barato pierde precisión; usar OCR self-host.",
        "volumen_objetivo": "Alto / masivo (10K+ extracciones/mes).",
    },
    "medio": {
        "etiqueta": "Medio",
        "rango": "3-5 reglas",
        "ejemplos": ["Servicios Públicos", "Expense", "Factura (5 reglas)", "Demo Banco Macro (5)"],
        "modelos": [
            {"m": "OvisOCR2 / NaviDC-OCR (self-host)", "paso": "Paso 1 · OCR premium SOTA", "usd": "$0 / GPU"},
            {"m": "GPT-5.4-mini", "paso": "Paso 2 · extracción JSON", "usd": "$5.19/1K pág"},
            {"m": "Claude Haiku 4.5", "paso": "Paso 2 · extracción JSON", "usd": "$5.31/1K pág"},
        ],
        "costo_usd_final": "≈ $5.19-5.31 por 1.000 pág",
        "ventaja": "OCR SOTA local reduce el error de base; el LLM medio garantiza JSON fiable.",
        "riesgo": "Dos pasos suman latencia; el OCR local exige GPU (capex).",
        "volumen_objetivo": "Medio (1K-10K extracciones/mes).",
    },
    "complejo": {
        "etiqueta": "Complejo / crítico",
        "rango": "6+ reglas",
        "ejemplos": ["Comprobante de pago (8)", "Demo Banco Macro (8)", "Comprobante de pago demo (8)"],
        "modelos": [
            {"m": "Claude Sonnet 4.6", "paso": "Paso 2 · extracción de alta precisión", "usd": "$15.93/1K pág"},
            {"m": "Qianfan-OCR (4B, self-host)", "paso": "Paso 2 · KIE avanzado (campos)", "usd": "$0 / GPU"},
            {"m": "gpt-5-mini (juez)", "paso": "Paso 3 · validación anti-alucinación", "usd": "adicional"},
        ],
        "costo_usd_final": "≈ $15.93+ por 1.000 pág",
        "ventaja": "Máxima precisión en campos críticos (montos, impuestos, condiciones) + detección de inventos.",
        "riesgo": "Costo alto por documento; solo justificable en esquemas de alto valor.",
        "volumen_objetivo": "Bajo / selectivo (solo esquemas críticos).",
    },
}

# Proyeccion de costo por 1.000 extracciones (volumen medio de produccion), en USD y ARS.
# Nota: MultiOCR promedia ~8.080 tokens/extraccion con gpt-5-mini (costo estimado ~$7.43/1K).
# Los paquetes abaratan ese numero al escalar el modelo segun la complejidad del esquema.
PROYECCION_COSTO = {
    "sencillo":  {"pct_ahorro_actual": "≈ 95%",   "usd_1k": 0.84,  "ars_1k": 0.84 * TIPO_CAMBIO_ARS},
    "medio":     {"pct_ahorro_actual": "≈ 28%",   "usd_1k": 5.31,  "ars_1k": 5.31 * TIPO_CAMBIO_ARS},
    "complejo":  {"pct_ahorro_actual": "+116%",   "usd_1k": 15.93, "ars_1k": 15.93 * TIPO_CAMBIO_ARS},
}
# Costo actual (referencia): gpt-5-mini ~ $7.43 USD / 1.000 extracciones = $11.405 ARS aprox.
COSTO_ACTUAL_USD_1K = 7.43
COSTO_ACTUAL_ARS_1K = round(COSTO_ACTUAL_USD_1K * TIPO_CAMBIO_ARS)

# Resumen de acciones de ahorro recomendadas (estrategia balanceada).
AHORRO_SUGERENCIAS = [
    "Mover los esquemas SENCILLOS (Ticket, CV, Figurita) de gpt-5-mini a Gemini 2.5 Flash-Lite / GPT-5.4-nano: ahorro de hasta ~95% en esos documentos.",
    "Mantener o subir calidad solo en esquemas MEDIO/COMPLEJO; los paquetes ya no son 'un modelo para todo' sino por densidad de reglas.",
    "En esquemas COMPLEJOS mantener gpt-5-mini o Claude Sonnet y activar el paso 3 (juez) solo aquí, donde el error es más costoso.",
    "Los OCR SOTA self-host (OvisOCR2/NaviDC/PaddleOCR-VL-1.6) eliminan el paso 1 en la nube a costo $0 de API (requieren GPU propia o edge).",
]

EMOJI_CAL = ["", "⭐", "⭐⭐", "⭐⭐⭐", "⭐⭐⭐⭐", "⭐⭐⭐⭐⭐"]

def _fmt_ars(usd):
    """USD -> ARS formateado (dolar oficial venta)."""
    return f"${usd * TIPO_CAMBIO_ARS:,.0f}"


def _tabla_paso(items):
    filas = ""
    for it in items:
        filas += (
            f'<tr><td style="padding:10px 12px;font-weight:600;color:#e2e8f0">{it["modelo"]}</td>'
            f'<td style="padding:10px 12px;color:#94a3b8;font-size:12px">{it["tipo"]}</td>'
            f'<td style="padding:10px 12px;text-align:center;font-size:12px">{it["modal"]}</td>'
            f'<td style="padding:10px 12px;text-align:center;font-size:12px">{it["vel"]}</td>'
            f'<td style="padding:10px 12px;text-align:center;font-size:13px">{EMOJI_CAL[it["calidad"]]}</td>'
            f'<td style="padding:10px 12px;color:#6ee7b7">{it["costo"]}</td>'
            f'<td style="padding:10px 12px;color:#64748b;font-size:12px">{it["nota"]}</td></tr>'
        )
    return filas


def cargar_datos():
    cfgs = json.load(open(CONFIGS, encoding="utf-8"))
    ail = json.load(open(AILOGS, encoding="utf-8"))
    return cfgs, ail


def resumir_cliente(ail):
    """agrega por apiKey: llamadas, tokens, modelos y costo estimado"""
    por_clave = defaultdict(lambda: {"calls": 0, "tokens": 0, "models": Counter()})
    for l in ail:
        k = l.get("apiKey")
        por_clave[k]["calls"] += 1
        por_clave[k]["tokens"] += l.get("totalTokens", 0)
        por_clave[k]["models"][l.get("aiModel")] += 1
    # tasa mixta USD por token (costo promedio ponderado general)
    total_tok = sum(v["tokens"] for v in por_clave.values())
    total_costo = 10.98  # USD real del análisis de producción
    tasa = total_costo / total_tok if total_tok else 0
    for k, v in por_clave.items():
        v["costo_usd"] = v["tokens"] * tasa
    return por_clave


def generar_html(cfgs, ail, por_clave):
    # ----- Vista 3: tabla por cliente/esquema -----
    # nombre legible por apiKey
    nombres = {
        "0b6644818c26dfb0609df4023d6190d7": "Cliente A",
        "b25551581eb99bec3a6292cd65d60275": "Cliente B (principal)",
        "cb388cd906af1d420a72a9610bf31863": "Cliente C",
        "e0652c688a1eade56d77b7b550018d74": "Cliente D",
        "d5fb7a13cebc775170fa6ea6f78057f8": "Cliente E",
        "2679c7abbd3c8a590061ff59b6cc4578": "Cliente F",
    }
    # agrupar configs por apiKeyId
    cfg_por_clave = defaultdict(list)
    for c in cfgs:
        cfg_por_clave[str(c.get("apiKeyId"))].append(c)

    filas_cliente = []
    total_llamadas = 0
    total_tok = 0
    total_costo = 0
    for clave, v in sorted(por_clave.items(), key=lambda x: -x[1]["tokens"]):
        nombre = nombres.get(clave, "Cliente " + clave[:6])
        modelos = ", ".join(f"{m} ({n})" for m, n in v["models"].most_common())
        esquemas = ", ".join(c.get("configName", "?") for c in cfg_por_clave.get(clave, [])) or "—"
        total_llamadas += v["calls"]
        total_tok += v["tokens"]
        total_costo += v["costo_usd"]
        filas_cliente.append(
            f'<tr><td style="padding:10px 14px;font-weight:600;color:#f8fafc">{nombre}</td>'
            f'<td style="padding:10px 14px;color:#94a3b8">{esquemas}</td>'
            f'<td style="padding:10px 14px;color:#cbd5e1">{modelos}</td>'
            f'<td style="padding:10px 14px;text-align:center">{v["calls"]}</td>'
            f'<td style="padding:10px 14px;text-align:center">{v["tokens"]:,}</td>'
            f'<td style="padding:10px 14px;text-align:center">${v["costo_usd"]:.2f}</td></tr>'
        )

    # ----- Vista 1: pasos -----
    html_pasos = ""
    for p in PASOS:
        propios = _tabla_paso(p["propios"])
        clientes = _tabla_paso(p["cliente"])
        html_pasos += f"""
        <div class="paso">
          <div class="paso-head">
            <span class="paso-num">{p['n']}</span>
            <div><h3 class="paso-title">{p['nombre']}</h3>
            <p class="paso-desc">{p['desc']}</p></div>
          </div>
          <div class="paso-sub">Modelos propios (internos / edge)</div>
          <table class="mt-tab"><thead><tr><th>Modelo</th><th>Tipo</th><th>Modalidad</th><th>Velocidad</th><th>Calidad</th><th>Costo</th><th>Nota</th></tr></thead>
          <tbody>{propios}</tbody></table>
          <div class="paso-sub" style="margin-top:14px">Modelos ofrecidos a clientes (cloud)</div>
          <table class="mt-tab"><thead><tr><th>Modelo</th><th>Tipo</th><th>Modalidad</th><th>Velocidad</th><th>Calidad</th><th>Costo</th><th>Nota</th></tr></thead>
          <tbody>{clientes}</tbody></table>
          <div class="reco">💡 <strong>Recomendación:</strong> {p['recomendado']}</div>
        </div>
        """

    # ----- Vista 2: comparativa -----
    filas_comp = ""
    for (m, prov, cal, vel, costo, multi, tipo, estado) in COMPARATIVA:
        badge_est = ""
        if estado == "EN PROD":
            badge_est = '<span class="badge badge-blue">EN PRODUCCIÓN</span>'
        elif estado == "EN PROD (edge)":
            badge_est = '<span class="badge badge-blue">EN PROD (edge)</span>'
        elif estado == "Uso puntual":
            badge_est = '<span class="badge badge-yellow">Uso puntual</span>'
        else:
            badge_est = '<span class="badge badge-green">Oferta</span>'
        tipo_b = '<span class="badge badge-yellow">Propio</span>' if tipo == "Propio" else '<span class="badge badge-green">Cliente</span>'
        filas_comp += (
            f'<tr><td style="padding:10px 14px;font-weight:600;color:#e2e8f0">{m}</td>'
            f'<td style="padding:10px 14px;color:#94a3b8;font-size:12px">{prov}</td>'
            f'<td style="padding:10px 14px;text-align:center">{tipo_b}</td>'
            f'<td style="padding:10px 14px;text-align:center;font-size:13px">{EMOJI_CAL[cal]}</td>'
            f'<td style="padding:10px 14px;color:#cbd5e1;font-size:12px">{vel}</td>'
            f'<td style="padding:10px 14px;text-align:center">{multi}</td>'
            f'<td style="padding:10px 14px;text-align:center;color:#fbd38d">${costo:.2f}</td>'
            f'<td style="padding:10px 14px">{badge_est}</td></tr>'
        )

    # ----- Vista 4: paquetes por complejidad (escala de modelos) -----
    badges_nivel = {
        "sencillo": '<span class="badge badge-green">Sencillo · 1-2 reglas</span>',
        "medio": '<span class="badge badge-yellow">Medio · 3-5 reglas</span>',
        "complejo": '<span class="badge badge-red">Complejo · 6+ reglas</span>',
    }
    html_paquetes = ""
    for nivel, d in NIVEL_COMPLEJIDAD.items():
        filas_mod = ""
        for x in d["modelos"]:
            filas_mod += (
                f'<tr><td style="padding:8px 14px;color:#e2e8f0;font-weight:500">{x["m"]}</td>'
                f'<td style="padding:8px 14px;color:#94a3b8;font-size:12px">{x["paso"]}</td>'
                f'<td style="padding:8px 14px;text-align:center;color:#fbd38d">{x["usd"]}</td></tr>'
            )
        ejemplos_html = " · ".join(f"<code>{e}</code>" for e in d["ejemplos"])
        proy = PROYECCION_COSTO[nivel]
        html_paquetes += f"""
        <div class="paso" id="paq-{nivel}">
          <div class="paso-head">
            <span class="paso-num" style="background:#8b5cf6">{nivel.capitalize()}</span>
            <div>
              <h3 class="paso-title">{d['etiqueta']} <span style="margin-left:8px">{badges_nivel[nivel]}</span></h3>
              <p class="paso-desc">Esquemas con {d['rango']} de reglas. Ejemplos reales de producción: {ejemplos_html}</p>
            </div>
          </div>
          <div class="paso-sub">Modelos recomendados (el poder escala con la complejidad)</div>
          <table class="mt-tab"><thead><tr><th>Modelo</th><th>Rol en el pipeline</th><th>Costo</th></tr></thead>
          <tbody>{filas_mod}</tbody></table>
          <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:14px;margin-top:16px">
            <div class="stat-card"><div class="label">Proyección USD / 1K extracc.</div><div class="value">${proy['usd_1k']:.2f}</div><div class="sub">vs actual gpt-5-mini ${COSTO_ACTUAL_USD_1K:.2f}</div></div>
            <div class="stat-card"><div class="label">Proyección ARS / 1K extracc.</div><div class="value">${proy['ars_1k']:,.0f}</div><div class="sub">dólar oficial {TIPO_CAMBIO_ARS:,.0f} ARS/USD</div></div>
            <div class="stat-card"><div class="label">Ahorro vs actual</div><div class="value" style="font-size:18px">{proy['pct_ahorro_actual']}</div><div class="sub">{d['volumen_objetivo']}</div></div>
          </div>
          <div class="reco">✅ <strong>Ventaja:</strong> {d['ventaja']}<br>⚠️ <strong>Riesgo:</strong> {d['riesgo']}</div>
        </div>
        """

    # tabla resumen de ahorro
    filas_ahorro = ""
    orden = [("sencillo", "Sencillo"), ("medio", "Medio"), ("complejo", "Complejo")]
    for nivel, etiqueta in orden:
        d = NIVEL_COMPLEJIDAD[nivel]
        proy = PROYECCION_COSTO[nivel]
        filas_ahorro += (
            f'<tr><td style="padding:10px 14px;font-weight:600;color:#e2e8f0">{etiqueta}</td>'
            f'<td style="padding:10px 14px;color:#94a3b8;font-size:12px">{d["rango"]}</td>'
            f'<td style="padding:10px 14px;text-align:center">${COSTO_ACTUAL_USD_1K:.2f} · {COSTO_ACTUAL_ARS_1K:,.0f}</td>'
            f'<td style="padding:10px 14px;text-align:center;color:#6ee7b7">${proy["usd_1k"]:.2f} · {proy["ars_1k"]:,.0f}</td>'
            f'<td style="padding:10px 14px;text-align:center;color:#fbd38d">{proy["pct_ahorro_actual"]}</td></tr>'
        )

    filas_sug = "".join(f'<li style="margin-bottom:10px;line-height:1.6">{s}</li>' for s in AHORRO_SUGERENCIAS)

    # cards resumen
    modelos_set = set()
    for v in por_clave.values():
        modelos_set.update(v["models"].keys())
    n_clientes = len(por_clave)
    top_modelo = Counter(m for v in por_clave.values() for m, n in v["models"].items() for _ in range(n)).most_common(1)
    top_modelo_nombre = top_modelo[0][0] if top_modelo else "—"
    pct_top = round(100 * sum(n for v in por_clave.values() for m, n in v["models"].items() if m == top_modelo_nombre) / max(1, total_llamadas))

    hoy = "2026-09-02"
    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>MultiOCR · Catálogo de Modelos por Paso de Extracción</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ font-family:'Segoe UI',system-ui,sans-serif; background:#0f172a; color:#e2e8f0; }}
.header {{ background:linear-gradient(135deg,#1e293b 0%,#0f172a 100%); padding:28px 40px; border-bottom:1px solid #334155; }}
.header h1 {{ font-size:26px; font-weight:700; color:#f8fafc; }}
.header p {{ color:#94a3b8; margin-top:6px; font-size:13px; }}
.badge {{ display:inline-block; padding:2px 8px; border-radius:4px; font-size:11px; font-weight:600; }}
.badge-green {{ background:#065f46; color:#6ee7b7; }}
.badge-yellow {{ background:#713f12; color:#fcd34d; }}
.badge-blue {{ background:#1e3a5f; color:#93c5fd; }}
.badge-red {{ background:#7f1d1d; color:#fca5a5; }}
.tabs {{ display:flex; gap:0; background:#1e293b; border-bottom:2px solid #334155; padding:0 20px; overflow-x:auto; }}
.tab {{ padding:14px 20px; cursor:pointer; color:#94a3b8; font-size:13px; font-weight:500; border-bottom:2px solid transparent; transition:all .2s; white-space:nowrap; }}
.tab:hover {{ color:#e2e8f0; }}
.tab.active {{ color:#3b82f6; border-bottom-color:#3b82f6; }}
.content {{ padding:30px 40px; max-width:1440px; margin:0 auto; }}
.tab-panel {{ display:none; }}
.tab-panel.active {{ display:block; }}
.stats-grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(200px,1fr)); gap:14px; margin-bottom:28px; }}
.stat-card {{ background:#1e293b; border-radius:12px; padding:18px; border:1px solid #334155; }}
.stat-card .label {{ font-size:11px; color:#64748b; text-transform:uppercase; letter-spacing:.5px; }}
.stat-card .value {{ font-size:24px; font-weight:700; color:#f8fafc; margin-top:6px; }}
.stat-card .sub {{ font-size:12px; color:#94a3b8; margin-top:4px; }}
.stat-card.highlight {{ border-color:#3b82f6; background:linear-gradient(135deg,#1e293b 0%,#172554 100%); }}
table {{ width:100%; border-collapse:collapse; background:#1e293b; border-radius:10px; overflow:hidden; }}
th {{ background:#334155; color:#94a3b8; font-size:11px; text-transform:uppercase; letter-spacing:.5px; padding:11px 14px; text-align:left; }}
td {{ border-bottom:1px solid #1e293b; font-size:13px; }}
tr:hover {{ background:#172033; }}
.section-title {{ font-size:20px; font-weight:700; color:#f8fafc; margin-bottom:8px; }}
.section-desc {{ font-size:13px; color:#94a3b8; margin-bottom:22px; line-height:1.6; }}
.paso {{ background:#1e293b; border:1px solid #334155; border-radius:14px; padding:22px; margin-bottom:22px; }}
.paso-head {{ display:flex; gap:14px; align-items:flex-start; margin-bottom:16px; }}
.paso-num {{ background:#3b82f6; color:#fff; border-radius:8px; min-width:34px; height:34px; display:flex; align-items:center; justify-content:center; font-weight:700; font-size:18px; }}
.paso-title {{ font-size:17px; color:#f8fafc; font-weight:600; }}
.paso-desc {{ font-size:12.5px; color:#94a3b8; margin-top:4px; line-height:1.5; }}
.paso-sub {{ font-size:12px; color:#60a5fa; font-weight:600; text-transform:uppercase; letter-spacing:.5px; margin-bottom:8px; }}
.reco {{ background:linear-gradient(135deg,#1e3a5f 0%,#172554 100%); border:1px solid #3b82f6; border-radius:10px; padding:12px 16px; margin-top:16px; color:#cbd5e1; font-size:13px; }}
.mt-tab {{ border-radius:10px; }}
</style>
</head>
<body>
<div class="header">
  <h1>🧠 MultiOCR · Catálogo de Modelos por Paso de Extracción</h1>
  <p>Modelos propios (internos/edge) vs. modelos ofrecidos a clientes, para cada paso del pipeline · Datos reales de producción · Generado {hoy}</p>
</div>

<div class="tabs">
  <div class="tab active" onclick="showTab(0)">Catálogo por Pasos</div>
  <div class="tab" onclick="showTab(1)">Comparativa Costo / Calidad</div>
  <div class="tab" onclick="showTab(2)">Gestión por Cliente / Esquema</div>
  <div class="tab" onclick="showTab(3)">Paquetes por Complejidad</div>
</div>

<div class="content">
  <!-- ============ TAB 1: CATALOGO POR PASOS ============ -->
  <div class="tab-panel active" id="tp0">
    <div class="stats-grid">
      <div class="stat-card highlight"><div class="label">Documento → Pipeline</div><div class="value">{len(PASOS)}</div><div class="sub">pasos de extracción</div></div>
      <div class="stat-card"><div class="label">Modelos propios</div><div class="value">{sum(len(p['propios']) for p in PASOS)}</div><div class="sub">internos / edge</div></div>
      <div class="stat-card"><div class="label">Modelos para clientes</div><div class="value">{sum(len(p['cliente']) for p in PASOS)}</div><div class="sub">cloud</div></div>
      <div class="stat-card"><div class="label">Modelo en producción</div><div class="value">{top_modelo_nombre}</div><div class="sub">{pct_top}% de llamadas</div></div>
    </div>
    <div class="section-title">Los 3 pasos de extracción de MultiOCR</div>
    <div class="section-desc">Cada documento (factura, ticket, CV, comprobante) recorre estos pasos. Por cada paso se ofrece una cartera de modelos, distinguiendo entre <strong>propios</strong> (corren en infraestructura interna, sin costo por token, mayor privacidad) y <strong>cliente</strong> (cloud, cobrados por uso al cliente).</div>
    {html_pasos}
  </div>

  <!-- ============ TAB 2: COMPARATIVA ============ -->
  <div class="tab-panel" id="tp1">
    <div class="section-title">Comparativa de Modelos · Costo vs Calidad</div>
    <div class="section-desc">Consumo promedio real: <strong>~8.080 tokens/llamada</strong>. Costo estimado a <strong>1.000 extracciones/mes</strong>. Los modelos <span class="badge badge-yellow">Propio</span> son internos (costo $0 de API, requieren hardware); los <span class="badge badge-green">Cliente</span> se ofrecen como servicio cloud.</div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-bottom:24px">
      <div class="stat-card"><div class="label">Costo actual gpt-5-mini</div><div class="value">$7.43</div><div class="sub">USD / 1.000 extracciones</div></div>
      <div class="stat-card"><div class="label">Costo optimizado gemini-3-flash</div><div class="value">$2.79</div><div class="sub">USD / 1.000 extracciones · −62%</div></div>
    </div>
    <canvas id="chartCost" style="height:360px;max-height:460px"></canvas>
    <div style="height:24px"></div>
    <table><thead><tr><th>Modelo</th><th>Provider</th><th>Tipo</th><th>Calidad</th><th>Velocidad</th><th>Multimodal</th><th>Costo/mes</th><th>Estado</th></tr></thead>
    <tbody>{filas_comp}</tbody></table>
  </div>

  <!-- ============ TAB 3: CLIENTES ============ -->
  <div class="tab-panel" id="tp2">
    <div class="stats-grid">
      <div class="stat-card highlight"><div class="label">Clientes activos</div><div class="value">{n_clientes}</div><div class="sub">{total_llamadas} llamadas AI</div></div>
      <div class="stat-card"><div class="label">Tokens consumidos</div><div class="value">{(total_tok/1e6):.1f}M</div><div class="sub">token totales</div></div>
      <div class="stat-card"><div class="label">Costo total estimado</div><div class="value">${total_costo:.2f}</div><div class="sub">USD</div></div>
      <div class="stat-card"><div class="label">Modelos distintos</div><div class="value">{len(modelos_set)}</div><div class="sub">usados en prod</div></div>
    </div>
    <div class="section-title">Modelo por Cliente y Esquema</div>
    <div class="section-desc">Qué modelo usa cada cliente (apiKey), cuántas extracciones realizó y su consumo real de tokens. La mayoría usa el modelo por defecto <code>gpt-5-mini</code>; algunos clientes ya cambian a <code>gemini-3-flash</code>.</div>
    <table><thead><tr><th>Cliente</th><th>Esquemas (configName)</th><th>Modelos</th><th style="text-align:center">Llamadas</th><th style="text-align:center">Tokens</th><th style="text-align:center">Costo USD</th></tr></thead>
    <tbody>{''.join(filas_cliente)}</tbody></table>
    <div class="section-title" style="margin-top:30px">Evolución de tokens por modelo</div>
    <canvas id="chartModelos" style="height:320px"></canvas>
  </div>

  <!-- ============ TAB 4: PAQUETES POR COMPLEJIDAD ============ -->
  <div class="tab-panel" id="tp3">
    <div class="stats-grid">
      <div class="stat-card highlight"><div class="label">Estrategia</div><div class="value">Escalar por reglas</div><div class="sub">el modelo se elige por complejidad del esquema, no 1 solo para todo</div></div>
      <div class="stat-card"><div class="label">Costo actual gpt-5-mini</div><div class="value">${COSTO_ACTUAL_USD_1K:.2f}</div><div class="sub">USD / 1.000 extracc. · {COSTO_ACTUAL_ARS_1K:,.0f} ARS</div></div>
      <div class="stat-card"><div class="label">Esquemas sencillos</div><div class="value" style="font-size:18px;color:#6ee7b7">−95%</div><div class="sub">con Gemini Flash-Lite / gpt-5.4-nano</div></div>
      <div class="stat-card"><div class="label">Dólar referencia</div><div class="value" style="font-size:20px">{TIPO_CAMBIO_ARS:,.0f}</div><div class="sub">ARS/USD · dólar oficial venta 2026-09-02</div></div>
    </div>
    <div class="section-title">Paquetes costo/efectivos · el poder del modelo escala con la complejidad</div>
    <div class="section-desc">No todos los documentos exigen el mismo modelo. Basado en <strong>investigación web 2026</strong> (OCR SOTA de última generación + precios oficiales LLM). Cada paquete agrupa modelos por <strong>número de reglas del esquema</strong> (proxy real de complejidad) y muestra su costo en <strong>USD y ARS</strong>.</div>
    {html_paquetes}

    <div class="section-title" style="margin-top:30px">Ahorro proyectado por complejidad (vs gpt-5-mini actual)</div>
    <div class="section-desc">Referencia actual: <code>gpt-5-mini</code> ~ ${COSTO_ACTUAL_USD_1K:.2f} USD / 1.000 extracciones ({COSTO_ACTUAL_ARS_1K:,.0f} ARS). Los paquetes abaratan al usar el modelo justo para cada densidad de reglas.</div>
    <table><thead><tr><th>Complejidad</th><th>Reglas</th><th style="text-align:center">Actual (USD · ARS)</th><th style="text-align:center">Paquete (USD · ARS)</th><th style="text-align:center">Impacto</th></tr></thead>
    <tbody>{filas_ahorro}</tbody></table>

    <div class="section-title" style="margin-top:30px">Acciones de ahorro recomendadas</div>
    <ul style="background:#1e293b;border:1px solid #334155;border-radius:12px;padding:18px 26px;color:#cbd5e1;font-size:13px;list-style:none">
      {filas_sug}
    </ul>

    <div class="section-title" style="margin-top:30px">OCR especializado de última generación (2026)</div>
    <div class="section-desc">Modelos SOTA de parsing de documentos, evaluados en <strong>OmniDocBench v1.6</strong> (96+ puntos) y <strong>Real5-OmniDocBench</strong> (robustez ante escaneo real). Son self-host (costo de API $0, requieren GPU/edge) y pueden reemplazar el paso 1 de OCR y simplificar la extracción.</div>
    <table><thead><tr><th>Modelo</th><th>Parámetros</th><th style="text-align:center">OmniDocBench</th><th style="text-align:center">Real5</th><th>Paradigma</th><th>Enfoque</th></tr></thead>
    <tbody>{''.join(f'<tr><td style="padding:10px 14px;font-weight:600;color:#e2e8f0">{m}</td><td style="padding:10px 14px;color:#94a3b8;font-size:12px">{p}</td><td style="padding:10px 14px;text-align:center;color:#6ee7b7;font-weight:600">{o}</td><td style="padding:10px 14px;text-align:center;color:#93c5fd">{r}</td><td style="padding:10px 14px;color:#cbd5e1;font-size:12px">{t}</td><td style="padding:10px 14px;color:#64748b;font-size:12px">{e}</td></tr>' for m,p,o,r,t,e in OCR_SOTA_2026)}</tbody></table>

    <div class="section-title" style="margin-top:30px">Costo LLM-OCR por 1.000 páginas (2026)</div>
    <div class="section-desc">Conversión verificada de precios de tokens (258 entradas/página + ~750 salida/página). Muestra USD (internacional) y ARS (dólar oficial venta BNA). El OCR dedicado clásico (AWS/Azure/Google) es la referencia plana de <strong>$1.50 / 1.000 páginas</strong>.</div>
    <table><thead><tr><th>Modelo</th><th>Proveedor</th><th style="text-align:center">USD / 1.000 pág</th><th style="text-align:center">ARS / 1.000 pág</th><th>Multimodal</th><th>Nota</th></tr></thead>
    <tbody>{''.join(f'<tr><td style="padding:10px 14px;font-weight:600;color:#e2e8f0">{m}</td><td style="padding:10px 14px;color:#94a3b8;font-size:12px">{p}</td><td style="padding:10px 14px;text-align:center;color:#fbd38d">${u:.2f}</td><td style="padding:10px 14px;text-align:center;color:#fbd38d">${u*TIPO_CAMBIO_ARS:,.0f}</td><td style="padding:10px 14px;text-align:center">{ml}</td><td style="padding:10px 14px;color:#64748b;font-size:12px">{n}</td></tr>' for m,p,u,ml,n in COSTO_OCR_PAGINA)}</tbody></table>
  </div>
</div>

<script>
function showTab(i){{
  document.querySelectorAll('.tab').forEach((t,idx)=>t.classList.toggle('active',idx===i));
  document.querySelectorAll('.tab-panel').forEach((p,idx)=>p.classList.toggle('active',idx===i));
}}
// datos para charts (excluyen costo 0 de modelos propios)
const comp = {json.dumps(COMPARATIVA)};
const filtrados = comp.filter(c => c[5] > 0).sort((a,b)=>a[5]-b[5]);
new Chart(document.getElementById('chartCost'), {{
  type:'bar',
  data:{{labels:filtrados.map(c=>c[0]), datasets:[{{label:'Costo USD/mes',data:filtrados.map(c=>c[5]),backgroundColor:filtrados.map(c=>c[1].includes('local')?'#f59e0b':(c[0].includes('gpt-5-mini')||c[0].includes('gemini-3-flash-preview')?'#3b82f6':'#a855f7'))}}]}},
  options:{{indexAxis:'y',plugins:{{legend:{{display:false}},tooltip:{{callbacks:{{label:(ctx)=>'$'+ctx.parsed.x.toFixed(2)+' / 1000 ext.'}}}}}},scales:{{x:{{beginAtZero:true}}}}}}
}});
// datos por modelo real (tokens)
const modeloDist = {json.dumps(dict(Counter(m for v in por_clave.values() for m,n in v['models'].items() for _ in range(n))))};
new Chart(document.getElementById('chartModelos'), {{
  type:'bar',
  data:{{labels:Object.keys(modeloDist), datasets:[{{label:'Llamadas AI por modelo',data:Object.values(modeloDist),backgroundColor:'#3b82f6'}}]}},
  options:{{plugins:{{legend:{{display:false}}}},scales:{{y:{{beginAtZero:true}}}}}}
}});
</script>
</body>
</html>
"""
    return html


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--salida", default=SALIDA_DEF)
    args = ap.parse_args()
    cfgs, ail = cargar_datos()
    por_clave = resumir_cliente(ail)
    html = generar_html(cfgs, ail, por_clave)
    with open(args.salida, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Dashboard de modelos generado: {args.salida}")
    print(f"  clientes: {len(por_clave)} | llamadas: {sum(v['calls'] for v in por_clave.values())}"
          f" | tokens: {sum(v['tokens'] for v in por_clave.values()):,}")


if __name__ == "__main__":
    main()
