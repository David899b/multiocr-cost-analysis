#!/usr/bin/env python3
"""
MultiOCR Token Cost Analyzer (Real Production Data)
Analyzes actual token consumption from ailogs and correlates with schema complexity.
"""

import json
import statistics
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
from datetime import datetime


@dataclass
class TokenConsumption:
    """Token consumption metrics for a single AI call"""
    log_id: str
    timestamp: str
    api_key: str
    provider: str  # "ai" field in DB
    ai_model: str
    action: str

    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


@dataclass
class SchemaTokenStats:
    """Aggregated token statistics for a provider/model combination"""
    provider: str
    ai_model: str
    call_count: int
    avg_prompt_tokens: float
    avg_completion_tokens: float
    avg_total_tokens: float
    min_tokens: int
    max_tokens: int
    std_dev_tokens: float
    total_tokens: int
    median_tokens: float


class TokenCostAnalyzer:
    """Analyzes token consumption from production ailogs"""

    EXCHANGE_RATE = 1520  # Dólar oficial BNA venta (ago 2026)

    # Provider pricing per 1M tokens (USD)
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
    }

    def __init__(self):
        self.consumptions: List[TokenConsumption] = []
        self.provider_stats: Dict[str, SchemaTokenStats] = {}

    def load_ailogs(self, file_path: str) -> List[TokenConsumption]:
        """Load ailogs from JSON file (exported from MongoDB)"""
        with open(file_path, 'r', encoding='utf-8') as f:
            logs = json.load(f)

        consumptions = []
        for log in logs:
            consumption = TokenConsumption(
                log_id=log.get("_id", ""),
                timestamp=log.get("timestamp", ""),
                api_key=log.get("apiKey", ""),
                provider=log.get("ai", "unknown"),
                ai_model=log.get("aiModel", "unknown"),
                action=log.get("action", "unknown"),
                prompt_tokens=log.get("promptTokens", 0),
                completion_tokens=log.get("completionTokens", 0),
                total_tokens=log.get("totalTokens", 0),
            )
            consumptions.append(consumption)

        self.consumptions.extend(consumptions)
        print(f"Loaded {len(consumptions)} AI log entries from {file_path}")
        return consumptions

    def calculate_provider_stats(self) -> Dict[str, SchemaTokenStats]:
        """Calculate aggregated statistics per provider/model"""
        model_data = {}

        for c in self.consumptions:
            key = f"{c.provider}|{c.ai_model}"
            if key not in model_data:
                model_data[key] = {
                    "provider": c.provider,
                    "ai_model": c.ai_model,
                    "prompt_tokens": [],
                    "completion_tokens": [],
                    "total_tokens": [],
                }
            model_data[key]["prompt_tokens"].append(c.prompt_tokens)
            model_data[key]["completion_tokens"].append(c.completion_tokens)
            model_data[key]["total_tokens"].append(c.total_tokens)

        self.provider_stats = {}
        for key, data in model_data.items():
            tokens = data["total_tokens"]
            if not tokens:
                continue

            stats = SchemaTokenStats(
                provider=data["provider"],
                ai_model=data["ai_model"],
                call_count=len(tokens),
                avg_prompt_tokens=statistics.mean(data["prompt_tokens"]),
                avg_completion_tokens=statistics.mean(data["completion_tokens"]),
                avg_total_tokens=statistics.mean(tokens),
                min_tokens=min(tokens),
                max_tokens=max(tokens),
                std_dev_tokens=statistics.stdev(tokens) if len(tokens) > 1 else 0,
                total_tokens=sum(tokens),
                median_tokens=statistics.median(tokens),
            )
            self.provider_stats[key] = stats

        return self.provider_stats

    def estimate_costs(self) -> List[Dict]:
        """Estimate costs based on provider pricing"""
        cost_estimates = []

        for key, stats in self.provider_stats.items():
            costs = self.PROVIDER_COSTS.get(stats.provider, {}).get(
                stats.ai_model,
                self.PROVIDER_COSTS.get(stats.provider, {}).get("default", {"prompt": 2.50, "completion": 10.00})
            )

            avg_prompt_cost = (stats.avg_prompt_tokens / 1_000_000) * costs["prompt"]
            avg_completion_cost = (stats.avg_completion_tokens / 1_000_000) * costs["completion"]
            avg_total_cost = avg_prompt_cost + avg_completion_cost

            total_prompt_cost = (sum(c.prompt_tokens for c in self.consumptions if c.provider == stats.provider and c.ai_model == stats.ai_model) / 1_000_000) * costs["prompt"]
            total_completion_cost = (sum(c.completion_tokens for c in self.consumptions if c.provider == stats.provider and c.ai_model == stats.ai_model) / 1_000_000) * costs["completion"]
            total_cost = total_prompt_cost + total_completion_cost

            cost_estimates.append({
                "provider": stats.provider,
                "ai_model": stats.ai_model,
                "call_count": stats.call_count,
                "avg_prompt_tokens": round(stats.avg_prompt_tokens),
                "avg_completion_tokens": round(stats.avg_completion_tokens),
                "avg_total_tokens": round(stats.avg_total_tokens),
                "avg_cost_per_call_usd": avg_total_cost,
                "avg_cost_per_call_ars": avg_total_cost * self.EXCHANGE_RATE,
                "total_cost_usd": total_cost,
                "total_cost_ars": total_cost * self.EXCHANGE_RATE,
                "cost_per_1000_calls_usd": avg_total_cost * 1000,
                "cost_per_1000_calls_ars": avg_total_cost * 1000 * self.EXCHANGE_RATE,
            })

        return sorted(cost_estimates, key=lambda x: x["total_cost_usd"], reverse=True)

    def detect_patterns(self) -> Dict[str, Any]:
        """Detect patterns in token consumption"""
        all_tokens = [c.total_tokens for c in self.consumptions]
        all_prompt = [c.prompt_tokens for c in self.consumptions]
        all_completion = [c.completion_tokens for c in self.consumptions]

        if not all_tokens:
            return {}

        # Token distribution
        mean_tokens = statistics.mean(all_tokens)
        std_tokens = statistics.stdev(all_tokens) if len(all_tokens) > 1 else 0

        # Percentiles
        sorted_tokens = sorted(all_tokens)
        n = len(sorted_tokens)
        p50 = sorted_tokens[n // 2]
        p90 = sorted_tokens[int(n * 0.9)]
        p99 = sorted_tokens[int(n * 0.99)]

        # Prompt vs Completion ratio
        prompt_ratio = statistics.mean(all_prompt) / mean_tokens if mean_tokens > 0 else 0

        # Outliers (>2 std dev)
        outliers = [c for c in self.consumptions if c.total_tokens > mean_tokens + 2 * std_tokens]

        # Provider distribution
        provider_counts = {}
        for c in self.consumptions:
            provider_counts[c.provider] = provider_counts.get(c.provider, 0) + 1

        # Model distribution
        model_counts = {}
        for c in self.consumptions:
            model_counts[c.ai_model] = model_counts.get(c.ai_model, 0) + 1

        # Time-based patterns (calls per day)
        daily_counts = {}
        for c in self.consumptions:
            if c.timestamp:
                day = c.timestamp[:10]
                daily_counts[day] = daily_counts.get(day, 0) + 1

        avg_daily = statistics.mean(daily_counts.values()) if daily_counts else 0

        return {
            "total_calls": len(self.consumptions),
            "total_tokens": sum(all_tokens),
            "avg_tokens_per_call": round(mean_tokens),
            "std_tokens": round(std_tokens),
            "min_tokens": min(all_tokens),
            "max_tokens": max(all_tokens),
            "median_tokens": p50,
            "p90_tokens": p90,
            "p99_tokens": p99,
            "prompt_ratio": round(prompt_ratio, 3),
            "completion_ratio": round(1 - prompt_ratio, 3),
            "outlier_count": len(outliers),
            "provider_distribution": provider_counts,
            "model_distribution": model_counts,
            "unique_days": len(daily_counts),
            "avg_daily_calls": round(avg_daily, 1),
        }

    def generate_report(self) -> str:
        """Generate comprehensive cost analysis report"""
        report = []
        report.append("=" * 90)
        report.append("MULTIOCR TOKEN COST ANALYSIS (Production Data)")
        report.append("=" * 90)
        report.append("")

        if not self.consumptions:
            report.append("No consumption data loaded.")
            return "\n".join(report)

        # Overall summary
        patterns = self.detect_patterns()
        total_cost_usd = sum(c.total_tokens for c in self.consumptions) / 1_000_000 * 1.0  # rough avg
        total_tokens = patterns.get("total_tokens", 0)

        report.append("OVERALL SUMMARY")
        report.append("-" * 50)
        report.append(f"Total AI calls analyzed: {patterns.get('total_calls', 0):,}")
        report.append(f"Total tokens consumed: {total_tokens:,}")
        report.append(f"Average tokens per call: {patterns.get('avg_tokens_per_call', 0):,}")
        report.append(f"Median tokens per call: {patterns.get('median_tokens', 0):,}")
        report.append(f"Token range: {patterns.get('min_tokens', 0):,} - {patterns.get('max_tokens', 0):,}")
        report.append(f"P90 tokens: {patterns.get('p90_tokens', 0):,}")
        report.append(f"P99 tokens: {patterns.get('p99_tokens', 0):,}")
        report.append(f"Prompt/Completion ratio: {patterns.get('prompt_ratio', 0):.1%} / {patterns.get('completion_ratio', 0):.1%}")
        report.append(f"Average daily calls: {patterns.get('avg_daily_calls', 0)}")
        report.append(f"Date range: {patterns.get('unique_days', 0)} days")
        report.append("")

        # Provider distribution
        report.append("PROVIDER DISTRIBUTION")
        report.append("-" * 50)
        for provider, count in sorted(patterns.get("provider_distribution", {}).items(), key=lambda x: x[1], reverse=True):
            pct = count / patterns.get("total_calls", 1) * 100
            bar = "█" * int(pct / 2)
            report.append(f"  {provider:15s}: {count:5d} calls ({pct:.1f}%) {bar}")
        report.append("")

        # Model distribution
        report.append("MODEL DISTRIBUTION")
        report.append("-" * 50)
        for model, count in sorted(patterns.get("model_distribution", {}).items(), key=lambda x: x[1], reverse=True):
            pct = count / patterns.get("total_calls", 1) * 100
            report.append(f"  {model:35s}: {count:5d} calls ({pct:.1f}%)")
        report.append("")

        # Per provider/model stats
        report.append("PER PROVIDER/MODEL STATISTICS")
        report.append("-" * 50)
        stats = self.calculate_provider_stats()
        for key, s in sorted(stats.items(), key=lambda x: x[1].total_tokens, reverse=True):
            report.append(f"\n  {s.provider} / {s.ai_model}")
            report.append(f"    Calls: {s.call_count:,}")
            report.append(f"    Avg tokens: {s.avg_total_tokens:,.0f} (std: {s.std_dev_tokens:,.0f})")
            report.append(f"    Range: {s.min_tokens:,} - {s.max_tokens:,}")
            report.append(f"    Median: {s.median_tokens:,.0f}")
            report.append(f"    Avg prompt: {s.avg_prompt_tokens:,.0f} | Avg completion: {s.avg_completion_tokens:,.0f}")
        report.append("")

        # Cost estimates
        report.append("COST ESTIMATES (USD / ARS)")
        report.append("-" * 50)
        costs = self.estimate_costs()
        total_usd = 0
        for c in costs:
            report.append(f"\n  {c['provider']} / {c['ai_model']}")
            report.append(f"    Calls: {c['call_count']:,}")
            report.append(f"    Avg cost/call: ${c['avg_cost_per_call_usd']:.6f} USD / ${c['avg_cost_per_call_ars']:.4f} ARS")
            report.append(f"    Total cost: ${c['total_cost_usd']:.4f} USD / ${c['total_cost_ars']:.2f} ARS")
            report.append(f"    Cost per 1,000 calls: ${c['cost_per_1000_calls_usd']:.2f} USD / ${c['cost_per_1000_calls_ars']:.2f} ARS")
            total_usd += c["total_cost_usd"]

        report.append(f"\n  TOTAL ESTIMATED COST: ${total_usd:.4f} USD / ${total_usd * self.EXCHANGE_RATE:.2f} ARS")
        report.append("")

        # Outliers
        outliers = [c for c in self.consumptions if c.total_tokens > patterns.get("avg_tokens_per_call", 0) + 2 * patterns.get("std_tokens", 0)]
        if outliers:
            report.append(f"OUTLIERS ({len(outliers)} calls with >2 std dev tokens)")
            report.append("-" * 50)
            for o in sorted(outliers, key=lambda x: x.total_tokens, reverse=True)[:10]:
                report.append(f"  {o.timestamp[:19]} | {o.provider}/{o.ai_model} | {o.total_tokens:,} tokens")
            if len(outliers) > 10:
                report.append(f"  ... and {len(outliers) - 10} more")
            report.append("")

        # Optimization recommendations
        report.append("OPTIMIZATION RECOMMENDATIONS")
        report.append("-" * 50)

        # Check if one provider is dominant
        provider_dist = patterns.get("provider_distribution", {})
        if provider_dist:
            dominant = max(provider_dist, key=provider_dist.get)
            dominant_pct = provider_dist[dominant] / patterns.get("total_calls", 1) * 100
            report.append(f"  1. Primary provider: {dominant} ({dominant_pct:.0f}% of calls)")

        # Check prompt/completion ratio
        prompt_ratio = patterns.get("prompt_ratio", 0)
        if prompt_ratio > 0.8:
            report.append(f"  2. High prompt ratio ({prompt_ratio:.0%}): Consider optimizing schema complexity to reduce prompt tokens")
        elif prompt_ratio < 0.5:
            report.append(f"  2. Balanced prompt/completion ratio ({prompt_ratio:.0%})")

        # Check for high token variance
        cv = patterns.get("std_tokens", 0) / patterns.get("avg_tokens_per_call", 1) if patterns.get("avg_tokens_per_call", 1) > 0 else 0
        if cv > 0.5:
            report.append(f"  3. High token variance (CV={cv:.2f}): Some schemas consume significantly more tokens than others")
            report.append(f"     Consider simplifying complex schemas or splitting large documents")

        # Cost per 1000 comparison
        if costs:
            cheapest = min(costs, key=lambda x: x["avg_cost_per_call_usd"])
            most_expensive = max(costs, key=lambda x: x["avg_cost_per_call_usd"])
            if most_expensive["avg_cost_per_call_usd"] > 0:
                ratio = most_expensive["avg_cost_per_call_usd"] / cheapest["avg_cost_per_call_usd"]
                report.append(f"  4. Cost ratio (most/least expensive model): {ratio:.1f}x")
                report.append(f"     Cheapest: {cheapest['provider']}/{cheapest['ai_model']}")
                report.append(f"     Most expensive: {most_expensive['provider']}/{most_expensive['ai_model']}")

        report.append("")
        return "\n".join(report)


def main():
    """Main function"""
    analyzer = TokenCostAnalyzer()

    # Load production ailogs
    ailogs_path = Path(__file__).parent / "production_data" / "ailogs.json"
    if ailogs_path.exists():
        analyzer.load_ailogs(str(ailogs_path))
    else:
        print(f"No ailogs found at {ailogs_path}")
        return

    # Calculate stats
    analyzer.calculate_provider_stats()

    # Generate report
    report = analyzer.generate_report()
    print(report)

    # Save report
    report_path = Path(__file__).parent / "reports" / "token_cost_report.txt"
    report_path.parent.mkdir(exist_ok=True)
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"\nReport saved to: {report_path}")

    # Save JSON
    costs = analyzer.estimate_costs()
    json_path = Path(__file__).parent / "reports" / "token_cost_analysis.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump({
            "summary": analyzer.detect_patterns(),
            "cost_estimates": costs,
        }, f, indent=2, ensure_ascii=False)
    print(f"JSON saved to: {json_path}")


if __name__ == "__main__":
    main()
