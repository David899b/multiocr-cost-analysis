#!/usr/bin/env python3
"""
MultiOCR Complete Cost Analysis
Main script that runs all analysis components and generates comprehensive reports.
"""

import json
import os
import sys
from pathlib import Path
from dataclasses import asdict

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from schema_analyzer import SchemaAnalyzer
from token_cost_analyzer import TokenCostAnalyzer
from visualization_generator import VisualizationGenerator


def main():
    """Run complete MultiOCR cost analysis"""
    print("=" * 80)
    print("MULTIOCR TOKEN COST ANALYSIS")
    print("=" * 80)
    print()
    
    # Initialize analyzers
    schema_analyzer = SchemaAnalyzer()
    token_analyzer = TokenCostAnalyzer()
    
    # Load sample data
    sample_dir = Path(__file__).parent / "sample-data"
    
    print("1. Loading schema configurations...")
    schemas = schema_analyzer.load_schemas_from_directory(str(sample_dir))
    print(f"   Loaded {len(schemas)} schemas")
    
    print("\n2. Loading token consumption logs...")
    logs_path = sample_dir / "sample_token_logs.json"
    if logs_path.exists():
        consumptions = token_analyzer.load_logs_from_file(str(logs_path))
        print(f"   Loaded {len(consumptions)} consumption logs")
    else:
        print("   No logs found, skipping token analysis")
    
    print("\n3. Analyzing schema complexity...")
    schema_analyses = schema_analyzer.analyze_all_schemas()
    print(f"   Analyzed {len(schema_analyses)} schemas")
    
    print("\n4. Calculating token statistics...")
    token_stats = token_analyzer.calculate_schema_statistics()
    print(f"   Calculated statistics for {len(token_stats)} schemas")
    
    # Generate reports
    print("\n5. Generating reports...")
    
    # Schema complexity report
    schema_report = schema_analyzer.generate_report()
    schema_report_path = Path(__file__).parent / "reports" / "schema_complexity_report.txt"
    schema_report_path.parent.mkdir(exist_ok=True)
    with open(schema_report_path, 'w', encoding='utf-8') as f:
        f.write(schema_report)
    print(f"   Schema complexity report: {schema_report_path}")
    
    # Token cost report
    token_report = token_analyzer.generate_cost_report()
    token_report_path = Path(__file__).parent / "reports" / "token_cost_report.txt"
    with open(token_report_path, 'w', encoding='utf-8') as f:
        f.write(token_report)
    print(f"   Token cost report: {token_report_path}")
    
    # JSON exports
    print("\n6. Exporting JSON data...")
    
    # Schema analysis JSON
    schema_json_path = Path(__file__).parent / "reports" / "schema_analysis.json"
    with open(schema_json_path, 'w', encoding='utf-8') as f:
        json.dump([asdict(a) for a in schema_analyses], f, indent=2, ensure_ascii=False)
    print(f"   Schema analysis JSON: {schema_json_path}")
    
    # Token analysis JSON
    token_json_path = Path(__file__).parent / "reports" / "token_cost_analysis.json"
    token_analyzer.export_to_json(str(token_json_path))
    print(f"   Token cost analysis JSON: {token_json_path}")
    
    # Generate dashboard
    print("\n7. Generating interactive dashboard...")
    viz_generator = VisualizationGenerator(schema_analyzer, token_analyzer)
    dashboard_path = Path(__file__).parent / "reports" / "dashboard.html"
    viz_generator.generate_dashboard_html(str(dashboard_path))
    print(f"   Dashboard: {dashboard_path}")
    
    # Print summary
    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)
    print()
    
    # Print key findings
    print("KEY FINDINGS:")
    print("-" * 40)
    
    if schema_analyses:
        avg_complexity = sum(a.total_complexity for a in schema_analyses) / len(schema_analyses)
        avg_tokens = sum(a.estimated_prompt_tokens for a in schema_analyses) / len(schema_analyses)
        print(f"• Average schema complexity: {avg_complexity:.2f}")
        print(f"• Average estimated tokens: {avg_tokens:,.0f}")
        
        # Find most complex schema
        most_complex = max(schema_analyses, key=lambda x: x.total_complexity)
        print(f"• Most complex schema: {most_complex.config_name} (score: {most_complex.total_complexity:.2f})")
        
        # Find highest token consumer
        highest_tokens = max(schema_analyses, key=lambda x: x.estimated_prompt_tokens)
        print(f"• Highest token consumer: {highest_tokens.config_name} ({highest_tokens.estimated_prompt_tokens:,} tokens)")
    
    if token_stats:
        total_cost_usd = sum(s.avg_cost_usd * s.extraction_count for s in token_stats.values())
        total_cost_ars = total_cost_usd * 1520  # Dólar oficial BNA venta (ago 2026)
        print(f"• Total cost analyzed: ${total_cost_usd:.4f} USD / ${total_cost_ars:.2f} ARS")
        
        # Most expensive schema
        most_expensive = max(token_stats.values(), key=lambda x: x.avg_cost_usd)
        print(f"• Most expensive per extraction: {most_expensive.config_id} (${most_expensive.avg_cost_usd:.6f} USD)")
    
    print()
    print("RECOMMENDATIONS:")
    print("-" * 40)
    print("1. Simplify deeply nested schemas (reduce depth < 3 levels)")
    print("2. Consolidate special rules to reduce token overhead")
    print("3. Use Gemini for simple schemas, OpenAI for complex ones")
    print("4. Preprocess large documents to extract relevant pages")
    print("5. Implement cost monitoring and alerts per client")
    print()
    print("Files generated:")
    print(f"  - {schema_report_path}")
    print(f"  - {token_report_path}")
    print(f"  - {schema_json_path}")
    print(f"  - {token_json_path}")
    print(f"  - {dashboard_path}")
    print()
    print("Open dashboard.html in a browser for interactive visualizations.")


if __name__ == "__main__":
    main()
