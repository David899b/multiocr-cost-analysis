# MultiOCR Token Cost Analysis

Análisis de costos de tokens por esquema en MultiOCR, detectando patrones de consumo y drivers de costo.

## Objetivo

Analizar el consumo de tokens por esquema (Config) en MultiOCR para:
- Identificar qué tipos de campos y estructuras consumen más tokens
- Detectar patrones lineales vs exponenciales en el crecimiento de costos
- Generar recomendaciones de optimización para reducir costos
- Estimar costos por extracción y por volumen

## Resultados del Análisis (Datos Reales de Producción)

| Métrica | Valor |
|---------|-------|
| Esquemas analizados | 18 |
| Llamadas AI totales | 1,374 |
| Tokens totales consumidos | 11,515,779 |
| Costo total estimado | $10.98 USD / $13,177 ARS |
| Costo promedio por llamada | $0.008 USD / $9.60 ARS |
| Provider dominante | OpenAI (98.4%) |
| Modelo principal | gpt-5-mini-2025-08-07 (98.2%) |

### Correlación Complejidad vs Tokens

- **Correlación lineal:** 0.907 (muy alta)
- **Tipo de relación:** Lineal
- **Driver más fuerte:** Cantidad de campos (correlación: 0.873)

### Recomendación Principal

**Migrar a Gemini Flash** reduce costos un **92%**:
- Actual: $0.0077 USD/llamada (GPT-5-mini)
- Optimizado: $0.0006 USD/llamada (Gemini Flash)
- **Ahorro anual: ~$120 USD / $144,000 ARS**

## Estructura del Proyecto

```
multiocr-cost-analysis/
├── sample-data/                    # Datos de ejemplo
│   ├── sample_schema_invoice.json
│   ├── sample_schema_remision.json
│   ├── sample_schema_contrato_complejo.json
│   └── sample_token_logs.json
├── reports/                        # Reportes generados
│   ├── FINAL_REPORT.md             # Reporte completo
│   ├── schema_complexity_report.txt
│   ├── token_cost_report.txt
│   ├── schema_analysis.json
│   ├── token_cost_analysis.json
│   └── dashboard.html              # Dashboard interactivo
├── schema_analyzer.py              # Analiza complejidad de esquemas
├── token_cost_analyzer.py          # Analiza consumo de tokens
├── visualization_generator.py      # Genera visualizaciones
├── run_analysis.py                 # Script principal
└── README.md
```

## Uso

### Ejecutar Análisis con Datos de Ejemplo

```bash
python3 run_analysis.py
```

### Ejecutar Análisis con Datos de Producción

1. Exportar datos de MongoDB:
```bash
# Conectar a MongoDB y exportar configs
mongosh "mongodb://..." --eval "JSON.stringify(db.configs.find().toArray())" > production_data/configs.json

# Exportar ailogs
mongosh "mongodb://..." --eval "JSON.stringify(db.ailogs.find().toArray())" > production_data/ailogs.json
```

2. Ejecutar análisis:
```bash
python3 schema_analyzer.py
python3 token_cost_analyzer.py
```

3. Ver dashboard:
```bash
open reports/dashboard.html
```

## Tecnologías

- Python 3.x
- Chart.js (para visualizaciones)
- JSON (para datos y configuración)

## Licencia

Análisis interno para Concentrix Catalyst.
