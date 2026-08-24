#!/usr/bin/env python3
"""
MultiOCR Schema Complexity Analyzer (Real OpenAPI Structure)
Analyzes FormConfig documents from MongoDB to calculate complexity metrics and predict token costs.
Matches the real SchemaField structure from the OpenAPI spec.
"""

import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict, field
from pathlib import Path


@dataclass
class SchemaFieldMetrics:
    """Metrics for a single SchemaField"""
    name: str
    label: str
    field_type: str  # text, number, select, array, group
    required: bool
    options_count: int = 0
    child_fields_count: int = 0
    depth: int = 1
    estimated_tokens: int = 0


@dataclass
class SchemaComplexity:
    """Full complexity metrics for a Config"""
    config_id: str
    config_name: str
    config_name_plural: str

    # Field counts by type
    total_fields: int = 0
    text_fields: int = 0
    number_fields: int = 0
    select_fields: int = 0
    array_fields: int = 0
    group_fields: int = 0

    # Nesting
    max_depth: int = 0
    avg_depth: float = 0.0

    # Options
    total_select_options: int = 0
    avg_options_per_select: float = 0.0

    # Required fields
    required_fields: int = 0
    optional_fields: int = 0

    # Special rules
    special_rules_count: int = 0
    total_rules_chars: int = 0
    avg_rules_chars: float = 0.0

    # Complexity scores (0-100)
    structural_complexity: float = 0.0
    rules_complexity: float = 0.0
    total_complexity: float = 0.0

    # Token estimation
    estimated_schema_tokens: int = 0
    estimated_rules_tokens: int = 0
    estimated_prompt_tokens: int = 0

    # All field details
    field_details: List[Dict] = field(default_factory=list)


class SchemaAnalyzer:
    """Analyzes MultiOCR FormConfig schemas (real OpenAPI structure)"""

    # Approximate tokens per character
    CHARS_PER_TOKEN = 3.5

    # Token multipliers by field type
    FIELD_TYPE_WEIGHTS = {
        "text": 1.0,
        "number": 1.0,
        "select": 1.5,
        "group": 1.2,
        "array": 2.5,
    }

    def __init__(self):
        self.configs: List[Dict] = []
        self.analyses: List[SchemaComplexity] = []

    def load_configs_from_file(self, file_path: str) -> List[Dict]:
        """Load FormConfig documents from JSON file (exported from MongoDB)"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Handle both array and {configs: [...]} formats
        if isinstance(data, list):
            configs = data
        elif isinstance(data, dict) and 'configs' in data:
            configs = data['configs']
        else:
            configs = [data]

        self.configs.extend(configs)
        print(f"Loaded {len(configs)} configs from {file_path}")
        return configs

    def _count_tokens(self, text: str) -> int:
        """Estimate token count for text"""
        if not text:
            return 0
        return max(1, len(text) // self.CHARS_PER_TOKEN)

    def _analyze_field(self, field: Dict, depth: int = 1) -> Dict[str, Any]:
        """Recursively analyze a SchemaField and return metrics"""
        field_type = field.get("type", "text")
        weight = self.FIELD_TYPE_WEIGHTS.get(field_type, 1.0)

        metrics = {
            "name": field.get("name", ""),
            "label": field.get("label", ""),
            "type": field_type,
            "required": field.get("required", False),
            "depth": depth,
            "options_count": 0,
            "child_fields_count": 0,
            "child_fields": [],
            "estimated_tokens": 0,
        }

        # Count select options
        if field_type == "select":
            options = field.get("options", [])
            metrics["options_count"] = len(options) if isinstance(options, list) else 0

        # Base tokens for this field
        tokens = 0
        tokens += self._count_tokens(field.get("name", ""))
        tokens += self._count_tokens(field.get("label", ""))
        tokens += 2  # type declaration

        # Select options add tokens
        if field_type == "select" and isinstance(field.get("options"), list):
            for option in field["options"]:
                tokens += self._count_tokens(str(option))

        # Recurse into nested fields (group or array)
        nested_fields = field.get("fields", [])
        if isinstance(nested_fields, list) and nested_fields:
            metrics["child_fields_count"] = len(nested_fields)
            for child in nested_fields:
                child_metrics = self._analyze_field(child, depth + 1)
                metrics["child_fields"].append(child_metrics)
                tokens += child_metrics["estimated_tokens"]

        metrics["estimated_tokens"] = int(tokens * weight)
        return metrics

    def _estimate_schema_tokens(self, schema_fields: List[Dict]) -> int:
        """Estimate tokens to represent the full schema in a prompt"""
        tokens = 0
        for field in schema_fields:
            field_metrics = self._analyze_field(field)
            tokens += field_metrics["estimated_tokens"]
        return int(tokens)

    def _estimate_rules_tokens(self, rules: List[str]) -> int:
        """Estimate tokens for specialRules array"""
        tokens = 0
        for rule in rules:
            tokens += self._count_tokens(rule)
        return int(tokens)

    def _collect_field_stats(self, fields: List[Dict], depth: int = 1) -> Dict[str, Any]:
        """Recursively collect field type counts, depths, and options"""
        stats = {
            "total": 0,
            "text": 0,
            "number": 0,
            "select": 0,
            "array": 0,
            "group": 0,
            "max_depth": depth,
            "depths": [depth],
            "select_options": 0,
            "required": 0,
            "optional": 0,
        }

        for field in fields:
            ftype = field.get("type", "text")
            stats["total"] += 1
            stats[ftype] = stats.get(ftype, 0) + 1

            if field.get("required", False):
                stats["required"] += 1
            else:
                stats["optional"] += 1

            if ftype == "select" and isinstance(field.get("options"), list):
                stats["select_options"] += len(field["options"])

            nested = field.get("fields", [])
            if isinstance(nested, list) and nested:
                child = self._collect_field_stats(nested, depth + 1)
                for key in ["total", "text", "number", "select", "array", "group", "select_options", "required", "optional"]:
                    stats[key] += child[key]
                stats["max_depth"] = max(stats["max_depth"], child["max_depth"])
                stats["depths"].extend(child["depths"])

        return stats

    def analyze_config(self, config: Dict) -> SchemaComplexity:
        """Analyze a single FormConfig and return complexity metrics"""
        config_id = config.get("_id", config.get("configId", "unknown"))
        config_name = config.get("configName", config.get("name", "Unknown"))
        config_name_plural = config.get("configNamePlural", config.get("namePlural", ""))

        # Handle nested config structure (some exports wrap in {config: {...}})
        actual_config = config.get("config", config)

        schema_fields = actual_config.get("schema", actual_config.get("fields", []))
        special_rules = actual_config.get("specialRules", [])

        # Collect field stats
        field_stats = self._collect_field_stats(schema_fields)

        # Special rules metrics
        total_rules_chars = sum(len(rule) for rule in special_rules if isinstance(rule, str))

        # Calculate structural complexity (0-100 scale)
        structural_score = (
            field_stats["total"] * 2 +
            field_stats["max_depth"] * 12 +
            field_stats["group"] * 4 +
            field_stats["array"] * 6 +
            field_stats["select_options"] * 0.5
        )

        # Calculate rules complexity (0-100 scale)
        rules_score = (
            len(special_rules) * 5 +
            total_rules_chars * 0.01
        )

        # Total complexity (weighted)
        total_score = (structural_score * 0.65) + (rules_score * 0.35)

        # Estimate tokens
        estimated_schema_tokens = self._estimate_schema_tokens(schema_fields)
        estimated_rules_tokens = self._estimate_rules_tokens(special_rules)
        estimated_prompt_tokens = estimated_schema_tokens + estimated_rules_tokens + 500  # base overhead

        # Averages
        avg_depth = sum(field_stats["depths"]) / len(field_stats["depths"]) if field_stats["depths"] else 0
        avg_options = field_stats["select_options"] / field_stats["select"] if field_stats["select"] > 0 else 0

        # Field details (flattened)
        field_details = []
        for sf in schema_fields:
            detail = self._analyze_field(sf)
            field_details.append(detail)

        analysis = SchemaComplexity(
            config_id=str(config_id),
            config_name=config_name,
            config_name_plural=config_name_plural,
            total_fields=field_stats["total"],
            text_fields=field_stats["text"],
            number_fields=field_stats["number"],
            select_fields=field_stats["select"],
            array_fields=field_stats["array"],
            group_fields=field_stats["group"],
            max_depth=field_stats["max_depth"],
            avg_depth=avg_depth,
            total_select_options=field_stats["select_options"],
            avg_options_per_select=avg_options,
            required_fields=field_stats["required"],
            optional_fields=field_stats["optional"],
            special_rules_count=len(special_rules),
            total_rules_chars=total_rules_chars,
            avg_rules_chars=total_rules_chars / len(special_rules) if special_rules else 0,
            structural_complexity=structural_score,
            rules_complexity=rules_score,
            total_complexity=total_score,
            estimated_schema_tokens=estimated_schema_tokens,
            estimated_rules_tokens=estimated_rules_tokens,
            estimated_prompt_tokens=estimated_prompt_tokens,
            field_details=field_details,
        )

        self.analyses.append(analysis)
        return analysis

    def analyze_all(self) -> List[SchemaComplexity]:
        """Analyze all loaded configs"""
        self.analyses = []
        for config in self.configs:
            self.analyze_config(config)
        return self.analyses

    def get_ranking(self) -> List[SchemaComplexity]:
        """Return schemas ranked by total complexity (descending)"""
        return sorted(self.analyses, key=lambda x: x.total_complexity, reverse=True)

    def get_cost_estimation(self, provider_costs: Dict = None) -> List[Dict]:
        """Estimate costs per schema based on provider pricing"""
        if provider_costs is None:
            provider_costs = {
                "Gemini": {"prompt": 1.25, "completion": 5.00},
                "OpenAI": {"prompt": 2.50, "completion": 10.00},
            }

        estimations = []
        for analysis in self.analyses:
            # Find original config to get provider
            config = next((c for c in self.configs
                          if str(c.get("_id", c.get("configId", ""))) == analysis.config_id), None)
            if not config:
                continue

            provider = config.get("provider", config.get("config", {}).get("provider", "Gemini"))
            costs = provider_costs.get(provider, provider_costs["Gemini"])

            estimated_completion = int(analysis.estimated_prompt_tokens * 0.3)

            prompt_cost = (analysis.estimated_prompt_tokens / 1_000_000) * costs["prompt"]
            completion_cost = (estimated_completion / 1_000_000) * costs["completion"]
            total_cost = prompt_cost + completion_cost

            estimations.append({
                "config_id": analysis.config_id,
                "config_name": analysis.config_name,
                "provider": provider,
                "estimated_prompt_tokens": analysis.estimated_prompt_tokens,
                "estimated_completion_tokens": estimated_completion,
                "cost_per_extraction_usd": total_cost,
                "cost_per_extraction_ars": total_cost * 1520,  # Dólar oficial BNA venta (ago 2026)
                "cost_per_1000_usd": total_cost * 1000,
                "cost_per_1000_ars": total_cost * 1000 * 1520,  # Dólar oficial BNA venta (ago 2026)
            })

        return sorted(estimations, key=lambda x: x["cost_per_extraction_usd"], reverse=True)

    def detect_patterns(self) -> Dict[str, Any]:
        """Detect cost patterns across schemas"""
        if len(self.analyses) < 2:
            return {"error": "Need at least 2 schemas for pattern detection"}

        complexities = [a.total_complexity for a in self.analyses]
        tokens = [a.estimated_prompt_tokens for a in self.analyses]
        depths = [a.max_depth for a in self.analyses]
        fields = [a.total_fields for a in self.analyses]
        rules = [a.special_rules_count for a in self.analyses]

        # Simple linear regression: complexity vs tokens
        n = len(complexities)
        mean_c = sum(complexities) / n
        mean_t = sum(tokens) / n
        cov_ct = sum((c - mean_c) * (t - mean_t) for c, t in zip(complexities, tokens)) / n
        var_c = sum((c - mean_c) ** 2 for c in complexities) / n
        correlation = cov_ct / (var_c ** 0.5 * (sum((t - mean_t) ** 2 for t in tokens) / n) ** 0.5) if var_c > 0 else 0

        # Check for exponential patterns (log-linear correlation)
        import math
        log_tokens = [math.log(t) if t > 0 else 0 for t in tokens]
        mean_lt = sum(log_tokens) / n
        cov_cl = sum((c - mean_c) * (lt - mean_lt) for c, lt in zip(complexities, log_tokens)) / n
        var_lt = sum((lt - mean_lt) ** 2 for lt in log_tokens) / n
        exp_correlation = cov_cl / (var_c ** 0.5 * var_lt ** 0.5) if var_c > 0 and var_lt > 0 else 0

        # Identify cost drivers
        driver_correlations = {}
        for name, values in [("fields", fields), ("depth", depths), ("rules", rules)]:
            mean_v = sum(values) / n
            var_v = sum((v - mean_v) ** 2 for v in values) / n
            cov_vt = sum((v - mean_v) * (t - mean_t) for v, t in zip(values, tokens)) / n
            corr = cov_vt / (var_v ** 0.5 * (sum((t - mean_t) ** 2 for t in tokens) / n) ** 0.5) if var_v > 0 else 0
            driver_correlations[name] = round(corr, 3)

        # Identify anomalies (>2 std dev from mean)
        mean_tokens = sum(tokens) / n
        std_tokens = (sum((t - mean_tokens) ** 2 for t in tokens) / n) ** 0.5
        anomalies = []
        for a in self.analyses:
            if std_tokens > 0 and abs(a.estimated_prompt_tokens - mean_tokens) > 2 * std_tokens:
                anomalies.append({
                    "config_id": a.config_id,
                    "config_name": a.config_name,
                    "tokens": a.estimated_prompt_tokens,
                    "deviation": round((a.estimated_prompt_tokens - mean_tokens) / std_tokens, 2)
                })

        return {
            "linear_correlation": round(correlation, 3),
            "exponential_correlation": round(exp_correlation, 3),
            "relationship_type": "linear" if correlation > 0.7 else ("exponential" if exp_correlation > 0.7 else "non-linear"),
            "driver_correlations": driver_correlations,
            "strongest_driver": max(driver_correlations, key=driver_correlations.get) if driver_correlations else "unknown",
            "anomalies": anomalies,
        }

    def generate_report(self) -> str:
        """Generate a text report"""
        report = []
        report.append("=" * 90)
        report.append("MULTIOCR SCHEMA COMPLEXITY ANALYSIS (Production Data)")
        report.append("=" * 90)
        report.append("")

        if not self.analyses:
            report.append("No schemas analyzed.")
            return "\n".join(report)

        # Summary
        avg_complexity = sum(a.total_complexity for a in self.analyses) / len(self.analyses)
        avg_tokens = sum(a.estimated_prompt_tokens for a in self.analyses) / len(self.analyses)
        avg_fields = sum(a.total_fields for a in self.analyses) / len(self.analyses)
        avg_depth = sum(a.max_depth for a in self.analyses) / len(self.analyses)

        report.append("SUMMARY")
        report.append("-" * 50)
        report.append(f"Total schemas analyzed: {len(self.analyses)}")
        report.append(f"Average fields per schema: {avg_fields:.1f}")
        report.append(f"Average max depth: {avg_depth:.1f}")
        report.append(f"Average complexity score: {avg_complexity:.2f}")
        report.append(f"Average estimated tokens: {avg_tokens:,.0f}")
        report.append("")

        # Distribution
        report.append("COMPLEXITY DISTRIBUTION")
        report.append("-" * 50)
        buckets = {"low (0-30)": 0, "medium (30-60)": 0, "high (60-100)": 0, "very high (100+)": 0}
        for a in self.analyses:
            if a.total_complexity < 30:
                buckets["low (0-30)"] += 1
            elif a.total_complexity < 60:
                buckets["medium (30-60)"] += 1
            elif a.total_complexity < 100:
                buckets["high (60-100)"] += 1
            else:
                buckets["very high (100+)"] += 1
        for bucket, count in buckets.items():
            bar = "█" * count
            report.append(f"  {bucket:20s}: {count:4d} {bar}")
        report.append("")

        # Top 20 most complex
        report.append("TOP 20 MOST COMPLEX SCHEMAS")
        report.append("-" * 50)
        ranking = self.get_ranking()
        for i, a in enumerate(ranking[:20], 1):
            report.append(f"{i:3d}. {a.config_name}")
            report.append(f"     ID: {a.config_id}")
            report.append(f"     Fields: {a.total_fields} (text:{a.text_fields} num:{a.number_fields} select:{a.select_fields} array:{a.array_fields} group:{a.group_fields})")
            report.append(f"     Depth: {a.max_depth} | Rules: {a.special_rules_count} | Complexity: {a.total_complexity:.2f}")
            report.append(f"     Estimated tokens: {a.estimated_prompt_tokens:,}")
            report.append("")

        # Top 20 cheapest
        report.append("TOP 20 SIMPLEST SCHEMAS (lowest token cost)")
        report.append("-" * 50)
        for i, a in enumerate(reversed(ranking[-20:]), 1):
            report.append(f"{i:3d}. {a.config_name} | Fields: {a.total_fields} | Tokens: {a.estimated_prompt_tokens:,} | Complexity: {a.total_complexity:.2f}")

        report.append("")

        # Pattern detection
        patterns = self.detect_patterns()
        report.append("PATTERN ANALYSIS")
        report.append("-" * 50)
        report.append(f"Complexity vs Tokens correlation: {patterns.get('linear_correlation', 'N/A')}")
        report.append(f"Relationship type: {patterns.get('relationship_type', 'N/A')}")
        report.append(f"Strongest cost driver: {patterns.get('strongest_driver', 'N/A')}")
        report.append("Driver correlations:")
        for driver, corr in patterns.get("driver_correlations", {}).items():
            report.append(f"  {driver}: {corr}")
        if patterns.get("anomalies"):
            report.append(f"\nAnomalies ({len(patterns['anomalies'])}):")
            for anomaly in patterns["anomalies"]:
                report.append(f"  - {anomaly['config_name']}: {anomaly['tokens']:,} tokens ({anomaly['deviation']}x std dev)")
        report.append("")

        # Cost estimation
        report.append("COST ESTIMATION (per extraction, USD / ARS)")
        report.append("-" * 50)
        costs = self.get_cost_estimation()
        for c in costs[:20]:
            report.append(f"  {c['config_name'][:40]:40s} | ${c['cost_per_extraction_usd']:.6f} USD | ${c['cost_per_extraction_ars']:.4f} ARS | {c['estimated_prompt_tokens']:,} tokens")
        if len(costs) > 20:
            report.append(f"  ... and {len(costs) - 20} more")
        report.append("")

        # Optimization recommendations
        report.append("OPTIMIZATION RECOMMENDATIONS")
        report.append("-" * 50)

        deep = [a for a in self.analyses if a.max_depth >= 4]
        many_rules = [a for a in self.analyses if a.special_rules_count >= 8]
        many_arrays = [a for a in self.analyses if a.array_fields >= 3]
        high_options = [a for a in self.analyses if a.total_select_options >= 20]

        report.append(f"  Schemas with deep nesting (depth >= 4): {len(deep)}")
        report.append(f"  Schemas with many rules (>= 8): {len(many_rules)}")
        report.append(f"  Schemas with many arrays (>= 3): {len(many_arrays)}")
        report.append(f"  Schemas with many select options (>= 20): {len(high_options)}")
        report.append("")

        return "\n".join(report)


def main():
    """Main function for standalone execution"""
    analyzer = SchemaAnalyzer()

    # Try to load from production_data first, then sample-data
    production_path = Path(__file__).parent / "production_data" / "configs.json"
    sample_path = Path(__file__).parent / "sample-data" / "sample_configs.json"

    if production_path.exists():
        analyzer.load_configs_from_file(str(production_path))
    elif sample_path.exists():
        analyzer.load_configs_from_file(str(sample_path))
    else:
        print("No config files found. Run fetch_mongodb_data.py first.")
        return

    # Analyze
    analyses = analyzer.analyze_all()
    print(f"Analyzed {len(analyses)} schemas")

    # Report
    report = analyzer.generate_report()
    print(report)

    # Save
    report_path = Path(__file__).parent / "reports" / "schema_complexity_report.txt"
    report_path.parent.mkdir(exist_ok=True)
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"\nReport saved to: {report_path}")

    # Save JSON
    json_path = Path(__file__).parent / "reports" / "schema_analysis.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump([asdict(a) for a in analyses], f, indent=2, ensure_ascii=False, default=str)
    print(f"JSON saved to: {json_path}")


if __name__ == "__main__":
    main()
