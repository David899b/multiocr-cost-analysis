#!/usr/bin/env python3
"""
MultiOCR Complete Token Cost Analysis
Consolidates configs, apilogs (load endpoints), and ailogs to correlate
schema complexity with token consumption.
"""

import json
import re
import statistics
import math
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict, field
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict


@dataclass
class SchemaFieldMetrics:
    """Metrics for a single SchemaField"""
    name: str
    label: str
    field_type: str
    required: bool
    options_count: int = 0
    child_fields_count: int = 0
    depth: int = 1
    chars_in_name: int = 0
    chars_in_label: int = 0


@dataclass
class SchemaComplexity:
    """Full complexity metrics for a Config"""
    config_id: str
    config_name: str
    config_name_plural: str

    # Field counts
    total_fields: int = 0
    text_fields: int = 0
    number_fields: int = 0
    select_fields: int = 0
    array_fields: int = 0
    group_fields: int = 0

    # Nesting
    max_depth: int = 0

    # Options
    total_select_options: int = 0

    # Required
    required_fields: int = 0
    optional_fields: int = 0

    # Special rules
    special_rules_count: int = 0
    total_rules_chars: int = 0
    avg_rules_chars: float = 0.0
    max_rule_chars: int = 0

    # Complexity scores
    structural_score: float = 0.0
    rules_score: float = 0.0
    total_complexity: float = 0.0

    # Token estimation
    estimated_schema_tokens: int = 0
    estimated_rules_tokens: int = 0
    estimated_prompt_tokens: int = 0


@dataclass
class ExtractionRecord:
    """A single extraction (load) event correlated with config and tokens"""
    config_id: str
    config_name: str
    timestamp: str
    provider: str
    ai_model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    # Schema complexity fields
    total_fields: int = 0
    max_depth: int = 0
    total_select_options: int = 0
    special_rules_count: int = 0
    total_rules_chars: int = 0
    total_complexity: float = 0.0


class CompleteAnalyzer:
    """Complete analysis correlating schema complexity with token consumption"""

    CHARS_PER_TOKEN = 3.5
    EXCHANGE_RATE = 1200

    FIELD_WEIGHTS = {
        "text": 1.0, "number": 1.0, "select": 1.5,
        "group": 1.2, "array": 2.5,
    }

    PROVIDER_COSTS = {
        "openai": {
            "gpt-5-mini-2025-08-07": {"prompt": 0.40, "completion": 1.60},
            "gpt-4o": {"prompt": 2.50, "completion": 10.00},
            "gpt-4o-mini": {"prompt": 0.15, "completion": 0.60},
            "default": {"prompt": 2.50, "completion": 10.00},
        },
        "gemini": {
            "gemini-3-flash-preview": {"prompt": 0.15, "completion": 0.60},
            "gemini-2.5-flash": {"prompt": 0.15, "completion": 0.60},
            "gemini-1.5-pro": {"prompt": 1.25, "completion": 5.00},
            "gemini-1.5-flash": {"prompt": 0.075, "completion": 0.30},
            "default": {"prompt": 1.25, "completion": 5.00},
        },
        "ollama": {
            "qwen2.5:7b": {"prompt": 0.0, "completion": 0.0, "note": "local, cost=hardware only"},
            "qwen2.5:14b": {"prompt": 0.0, "completion": 0.0, "note": "local, cost=hardware only"},
            "qwen2.5:32b": {"prompt": 0.0, "completion": 0.0, "note": "local, cost=hardware only"},
            "qwen2.5-coder:7b": {"prompt": 0.0, "completion": 0.0, "note": "local, cost=hardware only"},
            "llama3.1:8b": {"prompt": 0.0, "completion": 0.0, "note": "local, cost=hardware only"},
            "llama3.1:70b": {"prompt": 0.0, "completion": 0.0, "note": "local, cost=hardware only"},
            "mistral:7b": {"prompt": 0.0, "completion": 0.0, "note": "local, cost=hardware only"},
            "default": {"prompt": 0.0, "completion": 0.0, "note": "local, cost=hardware only"},
        },
        "groq": {
            "llama-3.1-70b-versatile": {"prompt": 0.59, "completion": 0.79},
            "llama-3.1-8b-instant": {"prompt": 0.05, "completion": 0.08},
            "llama-3.3-70b-versatile": {"prompt": 0.59, "completion": 0.79},
            "mixtral-8x7b-32768": {"prompt": 0.24, "completion": 0.24},
            "gemma2-9b-it": {"prompt": 0.20, "completion": 0.20},
            "default": {"prompt": 0.59, "completion": 0.79},
        },
        "anthropic": {
            "claude-3-5-haiku-20241022": {"prompt": 0.80, "completion": 4.00},
            "claude-3-haiku-20240307": {"prompt": 0.25, "completion": 1.25},
            "claude-sonnet-4-20250514": {"prompt": 3.00, "completion": 15.00},
            "default": {"prompt": 3.00, "completion": 15.00},
        },
        "deepseek": {
            "deepseek-chat": {"prompt": 0.14, "completion": 0.28},
            "deepseek-coder": {"prompt": 0.14, "completion": 0.28},
            "default": {"prompt": 0.14, "completion": 0.28},
        },
    }

    def __init__(self):
        self.configs: List[Dict] = []
        self.ailogs: List[Dict] = []
        self.apilogs_load: List[Dict] = []
        self.complexities: Dict[str, SchemaComplexity] = {}
        self.extractions: List[ExtractionRecord] = []

    # ─── DATA LOADING ─────────────────────────────────────────────

    def load_configs(self, path: str):
        with open(path, 'r', encoding='utf-8') as f:
            self.configs = json.load(f)
        print(f"Loaded {len(self.configs)} configs")

    def load_ailogs(self, path: str):
        with open(path, 'r', encoding='utf-8') as f:
            self.ailogs = json.load(f)
        print(f"Loaded {len(self.ailogs)} ailogs")

    def load_apilogs(self, path: str):
        with open(path, 'r', encoding='utf-8') as f:
            self.apilogs_load = json.load(f)
        print(f"Loaded {len(self.apilogs_load)} load apilogs")

    # ─── SCHEMA COMPLEXITY ────────────────────────────────────────

    def _count_tokens(self, text: str) -> int:
        if not text:
            return 0
        return max(1, len(text) // self.CHARS_PER_TOKEN)

    def _analyze_field(self, field: Dict, depth: int = 1) -> Dict:
        ftype = field.get("type", "text")
        weight = self.FIELD_WEIGHTS.get(ftype, 1.0)

        tokens = self._count_tokens(field.get("name", ""))
        tokens += self._count_tokens(field.get("label", ""))
        tokens += 2

        options_count = 0
        if ftype == "select":
            opts = field.get("options", [])
            options_count = len(opts) if isinstance(opts, list) else 0
            for o in (opts if isinstance(opts, list) else []):
                tokens += self._count_tokens(str(o))

        child_count = 0
        nested = field.get("fields", [])
        if isinstance(nested, list) and nested:
            child_count = len(nested)
            for child in nested:
                child_m = self._analyze_field(child, depth + 1)
                tokens += child_m["_raw_tokens"]

        return {
            "name": field.get("name", ""),
            "label": field.get("label", ""),
            "type": ftype,
            "required": field.get("required", False),
            "depth": depth,
            "options_count": options_count,
            "child_fields_count": child_count,
            "_raw_tokens": int(tokens * weight),
        }

    def _collect_stats(self, fields: List[Dict], depth: int = 1) -> Dict:
        stats = {
            "total": 0, "text": 0, "number": 0, "select": 0,
            "array": 0, "group": 0, "max_depth": depth,
            "select_options": 0, "required": 0, "optional": 0,
        }
        for f in fields:
            ft = f.get("type", "text")
            stats["total"] += 1
            stats[ft] = stats.get(ft, 0) + 1
            if f.get("required"):
                stats["required"] += 1
            else:
                stats["optional"] += 1
            if ft == "select" and isinstance(f.get("options"), list):
                stats["select_options"] += len(f["options"])
            nested = f.get("fields", [])
            if isinstance(nested, list) and nested:
                child = self._collect_stats(nested, depth + 1)
                for k in ["total", "text", "number", "select", "array", "group", "select_options", "required", "optional"]:
                    stats[k] += child[k]
                stats["max_depth"] = max(stats["max_depth"], child["max_depth"])
        return stats

    def _estimate_schema_tokens(self, fields: List[Dict]) -> int:
        total = 0
        for f in fields:
            m = self._analyze_field(f)
            total += m["_raw_tokens"]
        return total

    def _estimate_rules_tokens(self, rules: List[str]) -> int:
        return sum(self._count_tokens(r) for r in rules if isinstance(r, str))

    def analyze_config(self, config: Dict) -> SchemaComplexity:
        cid = str(config.get("_id", "unknown"))
        cname = config.get("configName", "Unknown")
        cname_p = config.get("configNamePlural", "")

        schema_fields = config.get("schema", [])
        special_rules = config.get("specialRules", [])

        stats = self._collect_stats(schema_fields)

        total_rules_chars = sum(len(r) for r in special_rules if isinstance(r, str))
        max_rule_chars = max((len(r) for r in special_rules if isinstance(r, str)), default=0)

        structural = (stats["total"] * 2 + stats["max_depth"] * 12 +
                      stats["group"] * 4 + stats["array"] * 6 +
                      stats["select_options"] * 0.5)
        rules_s = len(special_rules) * 5 + total_rules_chars * 0.01
        total_c = structural * 0.65 + rules_s * 0.35

        est_schema = self._estimate_schema_tokens(schema_fields)
        est_rules = self._estimate_rules_tokens(special_rules)

        analysis = SchemaComplexity(
            config_id=cid, config_name=cname, config_name_plural=cname_p,
            total_fields=stats["total"],
            text_fields=stats["text"], number_fields=stats["number"],
            select_fields=stats["select"], array_fields=stats["array"],
            group_fields=stats["group"],
            max_depth=stats["max_depth"],
            total_select_options=stats["select_options"],
            required_fields=stats["required"], optional_fields=stats["optional"],
            special_rules_count=len(special_rules),
            total_rules_chars=total_rules_chars,
            avg_rules_chars=total_rules_chars / len(special_rules) if special_rules else 0,
            max_rule_chars=max_rule_chars,
            structural_score=structural, rules_score=rules_s,
            total_complexity=total_c,
            estimated_schema_tokens=est_schema,
            estimated_rules_tokens=est_rules,
            estimated_prompt_tokens=est_schema + est_rules + 500,
        )
        self.complexities[cid] = analysis
        return analysis

    def analyze_all_configs(self):
        for c in self.configs:
            self.analyze_config(c)
        print(f"Analyzed {len(self.complexities)} schemas")

    # ─── CORRELATION: apilogs → ailogs → config ──────────────────

    def correlate_extractions(self):
        """Match apilogs (load endpoint) with ailogs by timestamp to get config + tokens"""
        # Build timestamp → ailog index
        ailog_by_ts = {}
        for i, al in enumerate(self.ailogs):
            ts = al.get("timestamp", "")[:19]
            ailog_by_ts[ts] = al

        # Sort ailogs by timestamp for nearest-match
        ailog_timestamps = sorted(ailog_by_ts.keys())

        def parse_ts(ts_str: str) -> datetime:
            """Parse timestamp string, handle both naive and aware"""
            ts = ts_str.replace("Z", "+00:00")
            dt = datetime.fromisoformat(ts)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=None)
            return dt

        def find_nearest_ailog(target_ts: str, max_diff_seconds: int = 60) -> Optional[Dict]:
            """Find ailog within max_diff_seconds of target timestamp"""
            if not ailog_timestamps:
                return None
            target_dt = parse_ts(target_ts)
            best = None
            best_diff = max_diff_seconds + 1
            for ats in ailog_timestamps:
                ats_dt = parse_ts(ats)
                # Make both naive for comparison
                t_naive = target_dt.replace(tzinfo=None) if target_dt.tzinfo else target_dt
                a_naive = ats_dt.replace(tzinfo=None) if ats_dt.tzinfo else ats_dt
                diff = abs((t_naive - a_naive).total_seconds())
                if diff < best_diff:
                    best_diff = diff
                    best = ailog_by_ts[ats]
                    if diff == 0:
                        break
            return best if best_diff <= max_diff_seconds else None

        # Extract configId from endpoint
        config_pattern = re.compile(r'/api/config/([a-f0-9]+)/load')

        matched = 0
        unmatched = 0
        for apilog in self.apilogs_load:
            endpoint = apilog.get("endpoint", "")
            ts = apilog.get("timestamp", "")
            m = config_pattern.search(endpoint)
            if not m:
                continue
            config_id = m.group(1)

            ailog = find_nearest_ailog(ts)
            if not ailog:
                unmatched += 1
                continue

            matched += 1
            complexity = self.complexities.get(config_id)

            record = ExtractionRecord(
                config_id=config_id,
                config_name=complexity.config_name if complexity else "Unknown",
                timestamp=ts,
                provider=ailog.get("ai", "unknown"),
                ai_model=ailog.get("aiModel", "unknown"),
                prompt_tokens=ailog.get("promptTokens", 0),
                completion_tokens=ailog.get("completionTokens", 0),
                total_tokens=ailog.get("totalTokens", 0),
                total_fields=complexity.total_fields if complexity else 0,
                max_depth=complexity.max_depth if complexity else 0,
                total_select_options=complexity.total_select_options if complexity else 0,
                special_rules_count=complexity.special_rules_count if complexity else 0,
                total_rules_chars=complexity.total_rules_chars if complexity else 0,
                total_complexity=complexity.total_complexity if complexity else 0,
            )
            self.extractions.append(record)

        print(f"Correlated {matched} extractions ({unmatched} unmatched)")

    # ─── STATISTICS ───────────────────────────────────────────────

    def _stats_for(self, values: List[float]) -> Dict:
        if not values:
            return {}
        n = len(values)
        s = sorted(values)
        return {
            "count": n,
            "mean": statistics.mean(values),
            "median": statistics.median(values),
            "stdev": statistics.stdev(values) if n > 1 else 0,
            "min": min(values),
            "max": max(values),
            "p10": s[int(n * 0.1)],
            "p25": s[int(n * 0.25)],
            "p75": s[int(n * 0.75)],
            "p90": s[int(n * 0.9)],
            "p95": s[int(n * 0.95)],
            "p99": s[min(int(n * 0.99), n - 1)],
        }

    def per_schema_statistics(self) -> Dict[str, Dict]:
        """Calculate per-schema token statistics"""
        schema_data = defaultdict(lambda: {
            "prompt": [], "completion": [], "total": [],
            "provider": set(), "model": set(), "timestamps": [],
        })
        for e in self.extractions:
            d = schema_data[e.config_id]
            d["prompt"].append(e.prompt_tokens)
            d["completion"].append(e.completion_tokens)
            d["total"].append(e.total_tokens)
            d["provider"].add(e.provider)
            d["model"].add(e.ai_model)
            d["timestamps"].append(e.timestamp)

        result = {}
        for cid, data in schema_data.items():
            complexity = self.complexities.get(cid)
            result[cid] = {
                "config_name": complexity.config_name if complexity else "Unknown",
                "total_fields": complexity.total_fields if complexity else 0,
                "max_depth": complexity.max_depth if complexity else 0,
                "total_complexity": complexity.total_complexity if complexity else 0,
                "estimated_tokens": complexity.estimated_prompt_tokens if complexity else 0,
                "providers": list(data["provider"]),
                "models": list(data["model"]),
                "prompt_tokens": self._stats_for(data["prompt"]),
                "completion_tokens": self._stats_for(data["completion"]),
                "total_tokens": self._stats_for(data["total"]),
                "first_extraction": min(data["timestamps"]) if data["timestamps"] else "",
                "last_extraction": max(data["timestamps"]) if data["timestamps"] else "",
            }
        return result

    # ─── CORRELATION ANALYSIS ────────────────────────────────────

    def _pearson(self, x: List[float], y: List[float]) -> float:
        n = len(x)
        if n < 3:
            return 0
        mx, my = statistics.mean(x), statistics.mean(y)
        num = sum((xi - mx) * (yi - my) for xi, yi in zip(x, y))
        den_x = math.sqrt(sum((xi - mx) ** 2 for xi in x))
        den_y = math.sqrt(sum((yi - my) ** 2 for yi in y))
        if den_x == 0 or den_y == 0:
            return 0
        return num / (den_x * den_y)

    def _r_squared(self, x: List[float], y: List[float]) -> float:
        return self._pearson(x, y) ** 2

    def _log_pearson(self, x: List[float], y: List[float]) -> Tuple[float, float]:
        """Test exponential relationship: correlate x with log(y)"""
        log_y = [math.log(v) if v > 0 else 0 for v in y]
        return self._pearson(x, log_y), self._pearson(x, log_y) ** 2

    def correlation_analysis(self) -> Dict[str, Any]:
        """Analyze correlation between schema factors and token consumption"""
        if len(self.extractions) < 5:
            return {"error": "Need at least 5 extractions for correlation"}

        # Per-schema averages
        schema_avgs = {}
        for cid, data in self.per_schema_statistics().items():
            if data["total_tokens"]["count"] >= 1:
                schema_avgs[cid] = {
                    "avg_total": data["total_tokens"]["mean"],
                    "avg_prompt": data["prompt_tokens"]["mean"],
                    "avg_completion": data["completion_tokens"]["mean"],
                    "total_fields": data["total_fields"],
                    "max_depth": data["max_depth"],
                    "total_complexity": data["total_complexity"],
                    "estimated_tokens": data["estimated_tokens"],
                }

        if len(schema_avgs) < 3:
            return {"error": "Need at least 3 schemas with extractions"}

        # Vectors
        cids = list(schema_avgs.keys())
        avg_totals = [schema_avgs[c]["avg_total"] for c in cids]
        fields = [schema_avgs[c]["total_fields"] for c in cids]
        depths = [schema_avgs[c]["max_depth"] for c in cids]
        complexities = [schema_avgs[c]["total_complexity"] for c in cids]
        estimated = [schema_avgs[c]["estimated_tokens"] for c in cids]

        # Linear correlations
        corr_fields = self._pearson(fields, avg_totals)
        corr_depth = self._pearson(depths, avg_totals)
        corr_complexity = self._pearson(complexities, avg_totals)
        corr_estimated = self._pearson(estimated, avg_totals)

        # R² values
        r2_fields = corr_fields ** 2
        r2_depth = corr_depth ** 2
        r2_complexity = corr_complexity ** 2
        r2_estimated = corr_estimated ** 2

        # Test exponential (log) relationships
        log_r2_fields, _ = self._log_pearson(fields, avg_totals)
        log_r2_depth, _ = self._log_pearson(depths, avg_totals)

        # Determine relationship type
        best_linear = max(r2_fields, r2_depth, r2_complexity)
        best_exponential = max(log_r2_fields, log_r2_depth)

        if best_linear > 0.7:
            relationship = "LINEAL"
            confidence = best_linear
        elif best_exponential > 0.7 and best_exponential > best_linear:
            relationship = "EXPONENCIAL"
            confidence = best_exponential
        else:
            relationship = "NO LINEAL"
            confidence = max(best_linear, best_exponential)

        # Anomalies (>2 std dev from regression line)
        anomalies = []
        if best_linear > 0.3:
            # Simple linear regression on strongest predictor
            strongest_idx = [r2_fields, r2_depth, r2_complexity].index(best_linear)
            x_vals = [fields, depths, complexities][strongest_idx]
            x_labels = ["fields", "depth", "complexity"][strongest_idx]

            mx = statistics.mean(x_vals)
            my = statistics.mean(avg_totals)
            slope = sum((x - mx) * (y - my) for x, y in zip(x_vals, avg_totals)) / max(sum((x - mx) ** 2 for x in x_vals), 1)
            intercept = my - slope * mx

            residuals = [y - (slope * x + intercept) for x, y in zip(x_vals, avg_totals)]
            std_resid = statistics.stdev(residuals) if len(residuals) > 1 else 0
            mean_resid = statistics.mean(residuals)

            for i, cid in enumerate(cids):
                if std_resid > 0 and abs(residuals[i]) > 2 * std_resid:
                    anomalies.append({
                        "config_id": cid,
                        "config_name": schema_avgs[cid]["total_fields"],  # placeholder
                        "actual_tokens": avg_totals[i],
                        "predicted_tokens": slope * x_vals[i] + intercept,
                        "residual": residuals[i],
                        "deviation_sigma": residuals[i] / std_resid,
                    })

        return {
            "n_schemas": len(cids),
            "n_extractions": len(self.extractions),
            "linear_correlations": {
                "fields_vs_tokens": {"r": round(corr_fields, 4), "r2": round(r2_fields, 4)},
                "depth_vs_tokens": {"r": round(corr_depth, 4), "r2": round(r2_depth, 4)},
                "complexity_vs_tokens": {"r": round(corr_complexity, 4), "r2": round(r2_complexity, 4)},
                "estimated_vs_actual": {"r": round(corr_estimated, 4), "r2": round(r2_estimated, 4)},
            },
            "exponential_correlations": {
                "fields_vs_log_tokens": round(log_r2_fields, 4),
                "depth_vs_log_tokens": round(log_r2_depth, 4),
            },
            "relationship_type": relationship,
            "confidence_r2": round(confidence, 4),
            "strongest_linear_predictor": ["fields", "depth", "complexity"][strongest_idx] if best_linear > 0.3 else "none",
            "anomalies": anomalies,
        }

    # ─── PROVIDER COMPARISON ─────────────────────────────────────

    def provider_comparison(self) -> Dict[str, Any]:
        """Compare costs between providers and models"""
        by_model = defaultdict(lambda: {
            "prompt": [], "completion": [], "total": [], "count": 0
        })
        for e in self.extractions:
            key = f"{e.provider}/{e.ai_model}"
            by_model[key]["prompt"].append(e.prompt_tokens)
            by_model[key]["completion"].append(e.completion_tokens)
            by_model[key]["total"].append(e.total_tokens)
            by_model[key]["count"] += 1

        result = {}
        for model_key, data in by_model.items():
            provider, model = model_key.split("/", 1)
            costs = self.PROVIDER_COSTS.get(provider, {}).get(
                model, self.PROVIDER_COSTS.get(provider, {}).get("default", {"prompt": 2.50, "completion": 10.00})
            )

            avg_prompt = statistics.mean(data["prompt"])
            avg_completion = statistics.mean(data["completion"])
            avg_total = statistics.mean(data["total"])

            avg_cost = (avg_prompt / 1_000_000) * costs["prompt"] + (avg_completion / 1_000_000) * costs["completion"]

            result[model_key] = {
                "provider": provider,
                "model": model,
                "calls": data["count"],
                "avg_prompt_tokens": round(avg_prompt),
                "avg_completion_tokens": round(avg_completion),
                "avg_total_tokens": round(avg_total),
                "min_total": min(data["total"]),
                "max_total": max(data["total"]),
                "median_total": statistics.median(data["total"]),
                "stdev_total": round(statistics.stdev(data["total"])) if len(data["total"]) > 1 else 0,
                "cost_per_call_usd": avg_cost,
                "cost_per_call_ars": avg_cost * self.EXCHANGE_RATE,
                "total_cost_usd": avg_cost * data["count"],
                "total_cost_ars": avg_cost * data["count"] * self.EXCHANGE_RATE,
                "prompt_price_per_1M": costs["prompt"],
                "completion_price_per_1M": costs["completion"],
            }

        return dict(sorted(result.items(), key=lambda x: x[1]["total_cost_usd"], reverse=True))

    # ─── COST DRIVERS ────────────────────────────────────────────

    def identify_cost_drivers(self) -> List[Dict]:
        """Identify which schema factors most strongly predict token consumption"""
        schema_avgs = {}
        for cid, data in self.per_schema_statistics().items():
            if data["total_tokens"]["count"] >= 1:
                c = self.complexities.get(cid)
                if c:
                    schema_avgs[cid] = {
                        "avg_tokens": data["total_tokens"]["mean"],
                        "total_fields": c.total_fields,
                        "text_fields": c.text_fields,
                        "number_fields": c.number_fields,
                        "select_fields": c.select_fields,
                        "array_fields": c.array_fields,
                        "group_fields": c.group_fields,
                        "max_depth": c.max_depth,
                        "total_select_options": c.total_select_options,
                        "required_fields": c.required_fields,
                        "special_rules_count": c.special_rules_count,
                        "total_rules_chars": c.total_rules_chars,
                        "structural_score": c.structural_score,
                        "rules_score": c.rules_score,
                    }

        if len(schema_avgs) < 3:
            return []

        cids = list(schema_avgs.keys())
        tokens = [schema_avgs[c]["avg_tokens"] for c in cids]

        factors = [
            ("total_fields", "Cantidad total de campos"),
            ("text_fields", "Campos de tipo text"),
            ("number_fields", "Campos de tipo number"),
            ("select_fields", "Campos de tipo select"),
            ("array_fields", "Campos de tipo array"),
            ("group_fields", "Campos de tipo group"),
            ("max_depth", "Profundidad de anidamiento"),
            ("total_select_options", "Total opciones en selects"),
            ("required_fields", "Campos requeridos"),
            ("special_rules_count", "Cantidad de specialRules"),
            ("total_rules_chars", "Caracteres totales en reglas"),
            ("structural_score", "Score estructural"),
            ("rules_score", "Score de reglas"),
        ]

        drivers = []
        for factor_key, factor_name in factors:
            values = [schema_avgs[c][factor_key] for c in cids]
            r = self._pearson(values, tokens)
            r2 = r ** 2

            # Test log relationship
            log_r, log_r2 = self._log_pearson(values, tokens)

            best_type = "lineal" if r2 >= log_r2 else "exponencial"
            best_r2 = max(r2, log_r2)

            drivers.append({
                "factor": factor_key,
                "factor_name": factor_name,
                "pearson_r": round(r, 4),
                "r2_linear": round(r2, 4),
                "r2_exponential": round(log_r2, 4),
                "best_relationship": best_type,
                "best_r2": round(best_r2, 4),
                "correlation_strength": (
                    "muy fuerte" if best_r2 > 0.7 else
                    "fuerte" if best_r2 > 0.5 else
                    "moderada" if best_r2 > 0.3 else
                    "débil" if best_r2 > 0.1 else
                    "muy débil"
                ),
            })

        return sorted(drivers, key=lambda x: x["best_r2"], reverse=True)

    # ─── REPORT ───────────────────────────────────────────────────

    def generate_report(self) -> str:
        r = []
        r.append("=" * 95)
        r.append("MULTIOCR – ANÁLISIS DE COSTO DE TOKENS POR ESQUEMA")
        r.append("=" * 95)
        r.append("")

        # ── 1. DATA SUMMARY ──
        r.append("1. RESUMEN DE DATOS")
        r.append("-" * 60)
        r.append(f"   Configs (esquemas):          {len(self.configs)}")
        r.append(f"   AiLogs (llamadas AI):        {len(self.ailogs)}")
        r.append(f"   Load API calls (extracciones): {len(self.apilogs_load)}")
        r.append(f"   Extracciones correlacionadas:  {len(self.extractions)}")
        r.append("")

        # ── 2. PER-SCHEMA STATISTICS ──
        r.append("2. ESTADÍSTICAS POR ESQUEMA")
        r.append("-" * 60)
        stats = self.per_schema_statistics()
        for cid, s in sorted(stats.items(), key=lambda x: x[1]["total_tokens"]["mean"], reverse=True):
            r.append(f"\n   {s['config_name']} ({cid})")
            r.append(f"   Campos: {s['total_fields']} | Depth: {s['max_depth']} | Complejidad: {s['total_complexity']:.1f}")
            r.append(f"   Extracciones: {s['total_tokens']['count']}")
            r.append(f"   Tokens totales:  media={s['total_tokens']['mean']:,.0f}  mediana={s['total_tokens']['median']:,.0f}  std={s['total_tokens']['stdev']:,.0f}")
            r.append(f"   Rango: {s['total_tokens']['min']:,} – {s['total_tokens']['max']:,}")
            r.append(f"   P10={s['total_tokens']['p10']:,.0f}  P25={s['total_tokens']['p25']:,.0f}  P75={s['total_tokens']['p75']:,.0f}  P90={s['total_tokens']['p90']:,.0f}")
            r.append(f"   Prompt: media={s['prompt_tokens']['mean']:,.0f}  |  Completion: media={s['completion_tokens']['mean']:,.0f}")
            r.append(f"   Providers: {', '.join(s['providers'])}  |  Models: {', '.join(s['models'])}")
        r.append("")

        # ── 3. CORRELATION ANALYSIS ──
        r.append("3. ANÁLISIS DE CORRELACIÓN (¿Qué hace más caro un esquema?)")
        r.append("-" * 60)
        corr = self.correlation_analysis()
        if "error" in corr:
            r.append(f"   {corr['error']}")
        else:
            r.append(f"   Esquemas analizados: {corr['n_schemas']}")
            r.append(f"   Extracciones totales: {corr['n_extractions']}")
            r.append(f"")
            r.append(f"   RELACIÓN DETERMINADA: {corr['relationship_type']} (confianza R²={corr['confidence_r2']})")
            r.append(f"")
            r.append(f"   Correlaciones lineales (Pearson R / R²):")
            lc = corr["linear_correlations"]
            for name, vals in lc.items():
                r.append(f"     {name:30s}  R={vals['r']:+.4f}  R²={vals['r2']:.4f}")
            r.append(f"")
            r.append(f"   Correlaciones exponenciales (R² con log(tokens)):")
            ec = corr["exponential_correlations"]
            for name, vals in ec.items():
                r.append(f"     {name:30s}  R²={vals:.4f}")
            r.append(f"")
            r.append(f"   Predictor lineal más fuerte: {corr['strongest_linear_predictor']}")
            if corr["anomalies"]:
                r.append(f"   Anomalías detectadas: {len(corr['anomalies'])}")
                for a in corr["anomalies"]:
                    r.append(f"     - {a['config_id']}: real={a['actual_tokens']:,.0f} predicho={a['predicted_tokens']:,.0f} ({a['deviation_sigma']:+.1f}σ)")
        r.append("")

        # ── 4. COST DRIVERS ──
        r.append("4. DRIVERS DE COSTO (factores que explican el consumo de tokens)")
        r.append("-" * 60)
        drivers = self.identify_cost_drivers()
        for i, d in enumerate(drivers[:10], 1):
            r.append(f"   {i:2d}. {d['factor_name']:40s}  R²={d['best_r2']:.4f}  ({d['correlation_strength']})  [{d['best_relationship']}]")
        r.append("")

        # ── 5. PROVIDER COMPARISON (real usage) ──
        r.append("5. COMPARACIÓN POR PROVEEDOR Y MODELO (uso real)")
        r.append("-" * 60)
        prov = self.provider_comparison()
        for model_key, p in prov.items():
            r.append(f"\n   {p['provider']} / {p['model']}")
            r.append(f"   Llamadas: {p['calls']}")
            r.append(f"   Tokens promedio: {p['avg_total_tokens']:,} (prompt={p['avg_prompt_tokens']:,} completion={p['avg_completion_tokens']:,})")
            r.append(f"   Rango: {p['min_total']:,} – {p['max_total']:,}  (mediana={p['median_total']:,})")
            r.append(f"   Costo por llamada: ${p['cost_per_call_usd']:.6f} USD / ${p['cost_per_call_ars']:.4f} ARS")
            r.append(f"   Costo total: ${p['total_cost_usd']:.4f} USD / ${p['total_cost_ars']:.2f} ARS")
            r.append(f"   Pricing: prompt=${p['prompt_price_per_1M']}/1M  completion=${p['completion_price_per_1M']}/1M")
        r.append("")

        # ── 5b. COST PROJECTION: all available models ──
        r.append("5b. PROYECCIÓN DE COSTOS: Todos los modelos disponibles")
        r.append("-" * 60)
        r.append("   Usando consumo promedio real: prompt=4,580 tokens, completion=3,500 tokens")
        r.append("   Proyección para 1,000 extracciones mensuales:")
        r.append("")

        avg_prompt = 4580
        avg_completion = 3500
        monthly_extractions = 1000

        all_models = []
        for provider, models in self.PROVIDER_COSTS.items():
            for model_name, pricing in models.items():
                if model_name == "default":
                    continue
                cost = (avg_prompt / 1_000_000) * pricing["prompt"] + (avg_completion / 1_000_000) * pricing["completion"]
                monthly_usd = cost * monthly_extractions
                monthly_ars = monthly_usd * self.EXCHANGE_RATE
                note = pricing.get("note", "")
                all_models.append({
                    "provider": provider,
                    "model": model_name,
                    "cost_per_call": cost,
                    "monthly_usd": monthly_usd,
                    "monthly_ars": monthly_ars,
                    "note": note,
                })

        all_models.sort(key=lambda x: x["monthly_usd"])

        r.append(f"   {'Modelo':45s} {'Costo/1K llamadas':>20s} {'USD/mes':>12s} {'ARS/mes':>15s}")
        r.append(f"   {'-'*45} {'-'*20} {'-'*12} {'-'*15}")
        for m in all_models:
            note = f" ({m['note']})" if m['note'] else ""
            r.append(f"   {m['provider']+'/'+m['model']:45s} ${m['monthly_usd']:>10.2f} USD  ${m['monthly_usd']:>8.2f}  ${m['monthly_ars']:>12,.0f}{note}")
        r.append("")

        # Best option per category
        cloud_models = [m for m in all_models if m['monthly_usd'] > 0]
        local_models = [m for m in all_models if m['monthly_usd'] == 0]

        if cloud_models:
            best_cloud = cloud_models[0]
            worst_cloud = cloud_models[-1]
            r.append(f"   MEJOR OPCIÓN CLOUD: {best_cloud['provider']}/{best_cloud['model']}")
            r.append(f"     Costo mensual: ${best_cloud['monthly_usd']:.2f} USD / ${best_cloud['monthly_ars']:,.0f} ARS")
            r.append(f"     vs opción más cara: {worst_cloud['provider']}/{worst_cloud['model']} (${worst_cloud['monthly_usd']:.2f} USD)")
            if worst_cloud['monthly_usd'] > 0:
                savings = (1 - best_cloud['monthly_usd'] / worst_cloud['monthly_usd']) * 100
                r.append(f"     Ahorro: {savings:.0f}%")
            r.append("")

        if local_models:
            r.append(f"   MEJOR OPCIÓN LOCAL (Ollama): {local_models[0]['provider']}/{local_models[0]['model']}")
            r.append(f"     Costo API: $0.00 USD (solo hardware)")
            r.append(f"     Requisitos: GPU con 8-16GB VRAM para 7B, 24GB+ para 14B-32B")
            r.append(f"     Trade-off: Sin costo variable, pero costo fijo de hardware y mantenimiento")
        r.append("")

        # ── 6. ANOMALIES ──
        r.append("6. ESQUEMAS CON CONSUMO ANÓMALO")
        r.append("-" * 60)
        all_totals = [e.total_tokens for e in self.extractions]
        if all_totals:
            mu = statistics.mean(all_totals)
            sigma = statistics.stdev(all_totals) if len(all_totals) > 1 else 0
            outliers = [e for e in self.extractions if sigma > 0 and e.total_tokens > mu + 2 * sigma]
            r.append(f"   Umbral: > {mu + 2 * sigma:,.0f} tokens (media + 2σ)")
            r.append(f"   Outliers detectados: {len(outliers)}")
            for o in sorted(outliers, key=lambda x: x.total_tokens, reverse=True)[:10]:
                r.append(f"     {o.timestamp[:19]} | {o.config_name:30s} | {o.provider}/{o.ai_model} | {o.total_tokens:,} tokens ({(o.total_tokens - mu) / sigma:+.1f}σ)")
        r.append("")

        # ── 7. CONCLUSIONS ──
        r.append("7. CONCLUSIONES")
        r.append("-" * 60)
        if "error" not in corr:
            r.append(f"   Relación entre complejidad y tokens: {corr['relationship_type']} (R²={corr['confidence_r2']})")
            strongest = corr["strongest_linear_predictor"]
            r.append(f"   Factor que más impacta el costo: {strongest}")
            driver_names = {
                "fields": "cantidad de campos",
                "depth": "profundidad de anidamiento",
                "complexity": "score de complejidad total",
            }
            r.append(f"   Esto significa que la {driver_names.get(strongest, strongest)} es el principal determinante del costo.")
            r.append("")

            if corr["relationship_type"] == "LINEAL":
                r.append("   IMPLICACIÓN: El costo crece proporcionalmente con la complejidad.")
                r.append("   Cada campo adicional agrega un costo predecible y constante.")
            elif corr["relationship_type"] == "EXPONENCIAL":
                r.append("   IMPLICACIÓN: El costo crece exponencialmente con la complejidad.")
                r.append("   Esquemas complejos son desproporcionadamente más caros.")
            else:
                r.append("   IMPLICACIÓN: No hay relación clara; otros factores (tamaño del documento, contenido) dominan.")

            r.append("")
            r.append("   RECOMENDACIONES:")
            r.append("   1. Priorizar simplificar esquemas con más campos (mayor impacto)")
            r.append("   2. Evaluar si arrays anidados son necesarios (costo 2.5x por array)")
            r.append("   3. Consolidar specialRules redundantes")
            r.append("   4. Investigar outliers de >100K tokens (posibles documentos problemáticos)")
        r.append("")

        return "\n".join(r)


def main():
    base = Path(__file__).parent
    prod = base / "production_data"

    analyzer = CompleteAnalyzer()
    analyzer.load_configs(str(prod / "configs.json"))
    analyzer.load_ailogs(str(prod / "ailogs.json"))
    analyzer.load_apilogs(str(prod / "apilogs_load.json"))

    analyzer.analyze_all_configs()
    analyzer.correlate_extractions()

    report = analyzer.generate_report()
    print(report)

    # Save
    reports = base / "reports"
    reports.mkdir(exist_ok=True)
    with open(reports / "COMPLETE_ANALYSIS.txt", 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"\nSaved to: {reports / 'COMPLETE_ANALYSIS.txt'}")

    # Save JSON
    json_data = {
        "per_schema_stats": analyzer.per_schema_statistics(),
        "correlation": analyzer.correlation_analysis(),
        "cost_drivers": analyzer.identify_cost_drivers(),
        "provider_comparison": analyzer.provider_comparison(),
    }
    with open(reports / "complete_analysis.json", 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False, default=str)
    print(f"Saved JSON to: {reports / 'complete_analysis.json'}")


if __name__ == "__main__":
    main()
