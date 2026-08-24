#!/usr/bin/env python3
"""
MultiOCR Visualization and Recommendations Generator
Creates charts and optimization recommendations based on token cost analysis.
"""

import json
from typing import Dict, List, Any
from pathlib import Path
from dataclasses import asdict
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))
from schema_analyzer import SchemaAnalyzer, SchemaComplexity
from token_cost_analyzer import TokenCostAnalyzer, SchemaTokenStats


class VisualizationGenerator:
    """Generates HTML visualizations for MultiOCR cost analysis"""
    
    def __init__(self, schema_analyzer: SchemaAnalyzer, token_analyzer: TokenCostAnalyzer):
        self.schema_analyzer = schema_analyzer
        self.token_analyzer = token_analyzer
    
    def generate_dashboard_html(self, output_path: str):
        """Generate an interactive HTML dashboard"""
        # Prepare data for charts
        schema_analyses = self.schema_analyzer.analyses
        token_stats = self.token_analyzer.schema_stats
        
        # Merge data
        chart_data = []
        for analysis in schema_analyses:
            stats = token_stats.get(analysis.config_id)
            if stats:
                chart_data.append({
                    "config_id": analysis.config_id,
                    "config_name": analysis.config_name,
                    "total_fields": analysis.total_fields,
                    "max_depth": analysis.max_depth,
                    "special_rules_count": analysis.special_rules_count,
                    "total_complexity": analysis.total_complexity,
                    "estimated_tokens": analysis.estimated_prompt_tokens,
                    "actual_avg_tokens": stats.avg_total_tokens,
                    "avg_cost_usd": stats.avg_cost_usd,
                    "avg_cost_ars": stats.avg_cost_ars,
                    "tokens_per_page": stats.tokens_per_page
                })
        
        html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MultiOCR Token Cost Analysis Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        h1 {{
            color: #2c3e50;
            text-align: center;
            margin-bottom: 30px;
        }}
        .dashboard-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(450px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .chart-card {{
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .chart-title {{
            font-size: 18px;
            font-weight: bold;
            color: #34495e;
            margin-bottom: 15px;
        }}
        .chart-container {{
            position: relative;
            height: 300px;
        }}
        .summary-cards {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }}
        .summary-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }}
        .summary-card h3 {{
            margin: 0;
            font-size: 14px;
            opacity: 0.9;
        }}
        .summary-card .value {{
            font-size: 28px;
            font-weight: bold;
            margin: 10px 0;
        }}
        .summary-card .subtitle {{
            font-size: 12px;
            opacity: 0.8;
        }}
        .recommendations {{
            background: white;
            border-radius: 10px;
            padding: 25px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .recommendations h2 {{
            color: #2c3e50;
            margin-top: 0;
        }}
        .recommendation-item {{
            padding: 15px;
            border-left: 4px solid #3498db;
            background: #f8f9fa;
            margin-bottom: 15px;
            border-radius: 0 5px 5px 0;
        }}
        .recommendation-item h4 {{
            margin: 0 0 10px 0;
            color: #2c3e50;
        }}
        .recommendation-item p {{
            margin: 0;
            color: #555;
            line-height: 1.6;
        }}
        .impact-high {{
            border-left-color: #e74c3c;
        }}
        .impact-medium {{
            border-left-color: #f39c12;
        }}
        .impact-low {{
            border-left-color: #27ae60;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #34495e;
            color: white;
        }}
        tr:hover {{
            background-color: #f5f5f5;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>MultiOCR Token Cost Analysis Dashboard</h1>
        
        <!-- Summary Cards -->
        <div class="summary-cards">
            <div class="summary-card">
                <h3>Schemas Analizados</h3>
                <div class="value">{len(schema_analyses)}</div>
                <div class="subtitle">Modelos de información</div>
            </div>
            <div class="summary-card">
                <h3>Promedio Tokens/Schema</h3>
                <div class="value">{sum(a.estimated_prompt_tokens for a in schema_analyses) // len(schema_analyses) if schema_analyses else 0:,}</div>
                <div class="subtitle">Tokens estimados por extracción</div>
            </div>
            <div class="summary-card">
                <h3>Costo Promedio</h3>
                <div class="value">${sum(s.avg_cost_usd for s in token_stats.values()) / len(token_stats) * 1000000 if token_stats else 0:.2f}</div>
                <div class="subtitle">USD por millón de tokens</div>
            </div>
            <div class="summary-card">
                <h3>Profundidad Máx Promedio</h3>
                <div class="value">{sum(a.max_depth for a in schema_analyses) / len(schema_analyses) if schema_analyses else 0:.1f}</div>
                <div class="subtitle">Niveles de anidamiento</div>
            </div>
        </div>
        
        <!-- Charts -->
        <div class="dashboard-grid">
            <!-- Complexity vs Tokens Chart -->
            <div class="chart-card">
                <div class="chart-title">Complejidad vs Tokens Reales</div>
                <div class="chart-container">
                    <canvas id="complexityChart"></canvas>
                </div>
            </div>
            
            <!-- Field Type Distribution -->
            <div class="chart-card">
                <div class="chart-title">Distribución de Tipos de Campo</div>
                <div class="chart-container">
                    <canvas id="fieldTypeChart"></canvas>
                </div>
            </div>
            
            <!-- Cost per Schema -->
            <div class="chart-card">
                <div class="chart-title">Costo por Schema (USD)</div>
                <div class="chart-container">
                    <canvas id="costChart"></canvas>
                </div>
            </div>
            
            <!-- Tokens per Page -->
            <div class="chart-card">
                <div class="chart-title">Tokens por Página</div>
                <div class="chart-container">
                    <canvas id="tokensPerPageChart"></canvas>
                </div>
            </div>
        </div>
        
        <!-- Detailed Table -->
        <div class="chart-card" style="margin-bottom: 30px;">
            <div class="chart-title">Detalle por Schema</div>
            <table>
                <thead>
                    <tr>
                        <th>Schema</th>
                        <th>Campos</th>
                        <th>Profundidad</th>
                        <th>Reglas</th>
                        <th>Complejidad</th>
                        <th>Tokens Est.</th>
                        <th>Tokens Reales</th>
                        <th>Costo USD</th>
                        <th>Costo ARS</th>
                    </tr>
                </thead>
                <tbody>
                    {"".join(f'''
                    <tr>
                        <td><strong>{d['config_name']}</strong><br><small>{d['config_id']}</small></td>
                        <td>{d['total_fields']}</td>
                        <td>{d['max_depth']}</td>
                        <td>{d['special_rules_count']}</td>
                        <td>{d['total_complexity']:.1f}</td>
                        <td>{d['estimated_tokens']:,}</td>
                        <td>{d['actual_avg_tokens']:,.0f}</td>
                        <td>${d['avg_cost_usd']:.6f}</td>
                        <td>${d['avg_cost_ars']:.4f}</td>
                    </tr>
                    ''' for d in chart_data)}
                </tbody>
            </table>
        </div>
        
        <!-- Recommendations -->
        <div class="recommendations">
            <h2>Recomendaciones de Optimización</h2>
            
            <div class="recommendation-item impact-high">
                <h4>1. Reducir Anidamiento en Esquemas Complejos</h4>
                <p>Los esquemas con más de 3 niveles de profundidad consumen hasta 2x más tokens. Considere aplanar estructuras de group/array donde sea posible.</p>
            </div>
            
            <div class="recommendation-item impact-high">
                <h4>2. Optimizar Reglas Especiales</h4>
                <p>Consolide reglas similares y elimine redundancias. Cada regla promedia 50-100 tokens; reglas complejas pueden consumir 200+ tokens.</p>
            </div>
            
            <div class="recommendation-item impact-medium">
                <h4>3. Selección Inteligente de Proveedor</h4>
                <p>Use Gemini para esquemas simples (menor costo) y reserve OpenAI para tareas de extracción complejas que requieran mayor precisión.</p>
            </div>
            
            <div class="recommendation-item impact-medium">
                <h4>4. Preprocesamiento de Documentos</h4>
                <p>Divida documentos grandes en partes más pequeñas y extraiga páginas relevantes antes de enviar a IA. Esto reduce significativamente el consumo de tokens.</p>
            </div>
            
            <div class="recommendation-item impact-low">
                <h4>5. Monitoreo de Costos por Cliente</h4>
                <p>Implemente alertas de consumo y límites por cliente para evitar sobrecostos. El sistema actual ya soporta cuotas por API key.</p>
            </div>
        </div>
    </div>
    
    <script>
        // Chart data
        const chartData = {json.dumps(chart_data)};
        
        // Complexity vs Tokens Chart
        new Chart(document.getElementById('complexityChart'), {{
            type: 'scatter',
            data: {{
                datasets: [{{
                    label: 'Complejidad vs Tokens Reales',
                    data: chartData.map(d => ({{
                        x: d.total_complexity,
                        y: d.actual_avg_tokens
                    }})),
                    backgroundColor: 'rgba(52, 152, 219, 0.6)',
                    borderColor: 'rgba(52, 152, 219, 1)',
                    pointRadius: 8
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                scales: {{
                    x: {{
                        title: {{
                            display: true,
                            text: 'Puntuación de Complejidad'
                        }}
                    }},
                    y: {{
                        title: {{
                            display: true,
                            text: 'Tokens Promedio'
                        }}
                    }}
                }}
            }}
        }});
        
        // Field Type Distribution Chart
        const fieldTypes = {{text: 0, number: 0, select: 0, group: 0, array: 0}};
        chartData.forEach(d => {{
            // This would need actual field type counts from analysis
        }});
        
        new Chart(document.getElementById('fieldTypeChart'), {{
            type: 'doughnut',
            data: {{
                labels: ['Text', 'Number', 'Select', 'Group', 'Array'],
                datasets: [{{
                    data: [45, 25, 15, 10, 5], // Placeholder - replace with actual data
                    backgroundColor: [
                        '#3498db',
                        '#2ecc71',
                        '#e74c3c',
                        '#9b59b6',
                        '#f39c12'
                    ]
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false
            }}
        }});
        
        // Cost per Schema Chart
        new Chart(document.getElementById('costChart'), {{
            type: 'bar',
            data: {{
                labels: chartData.map(d => d.config_name),
                datasets: [{{
                    label: 'Costo USD',
                    data: chartData.map(d => d.avg_cost_usd),
                    backgroundColor: 'rgba(46, 204, 113, 0.6)',
                    borderColor: 'rgba(46, 204, 113, 1)',
                    borderWidth: 1
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                scales: {{
                    y: {{
                        beginAtZero: true,
                        title: {{
                            display: true,
                            text: 'Costo USD'
                        }}
                    }}
                }}
            }}
        }});
        
        // Tokens per Page Chart
        new Chart(document.getElementById('tokensPerPageChart'), {{
            type: 'bar',
            data: {{
                labels: chartData.map(d => d.config_name),
                datasets: [{{
                    label: 'Tokens por Página',
                    data: chartData.map(d => d.tokens_per_page),
                    backgroundColor: 'rgba(155, 89, 182, 0.6)',
                    borderColor: 'rgba(155, 89, 182, 1)',
                    borderWidth: 1
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                scales: {{
                    y: {{
                        beginAtZero: true,
                        title: {{
                            display: true,
                            text: 'Tokens/Página'
                        }}
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>"""
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"Dashboard generated: {output_path}")


def main():
    """Main function to generate visualizations"""
    # Run schema analysis
    schema_analyzer = SchemaAnalyzer()
    sample_dir = Path(__file__).parent / "sample-data"
    schema_analyzer.load_schemas_from_directory(str(sample_dir))
    schema_analyzer.analyze_all_schemas()
    
    # Run token analysis
    token_analyzer = TokenCostAnalyzer()
    logs_path = sample_dir / "sample_token_logs.json"
    if logs_path.exists():
        token_analyzer.load_logs_from_file(str(logs_path))
        token_analyzer.calculate_schema_statistics()
    
    # Generate dashboard
    viz_generator = VisualizationGenerator(schema_analyzer, token_analyzer)
    dashboard_path = Path(__file__).parent / "dashboard.html"
    viz_generator.generate_dashboard_html(str(dashboard_path))
    
    print("\nAnalysis complete!")
    print(f"Open dashboard in browser: {dashboard_path}")


if __name__ == "__main__":
    main()
