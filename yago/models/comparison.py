"""
YAGO v8.0 - Model Comparison
Compare different AI models side-by-side
"""

import logging
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime

from .base import Model, ModelRequest, ModelResponse
from .registry import ModelRegistry, get_registry

logger = logging.getLogger(__name__)


class ModelComparison:
    """
    Compare multiple AI models

    Responsibilities:
    - Run same prompt on multiple models
    - Compare responses
    - Benchmark performance
    - Generate comparison reports
    """

    def __init__(self, registry: Optional[ModelRegistry] = None):
        """Initialize model comparison"""
        self.registry = registry or get_registry()

    async def compare(
        self,
        model_ids: List[str],
        request: ModelRequest,
        timeout: float = 30.0
    ) -> Dict[str, Any]:
        """
        Compare multiple models with same request

        Args:
            model_ids: List of model IDs to compare
            request: Model request
            timeout: Timeout for each model

        Returns:
            Comparison results
        """
        try:
            results = {}
            errors = {}

            # Run models in parallel
            tasks = []
            for model_id in model_ids:
                model = self.registry.get(model_id)
                if model:
                    tasks.append(self._run_model(model, request, timeout))
                else:
                    errors[model_id] = "Model not found"

            # Wait for all tasks
            responses = await asyncio.gather(*tasks, return_exceptions=True)

            # Process results
            for model_id, response in zip(model_ids, responses):
                if isinstance(response, Exception):
                    errors[model_id] = str(response)
                elif response:
                    results[model_id] = response

            # Generate comparison
            comparison = self._generate_comparison(results, errors)

            return comparison

        except Exception as e:
            logger.error(f"Error comparing models: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    async def _run_model(
        self,
        model: Model,
        request: ModelRequest,
        timeout: float
    ) -> Optional[ModelResponse]:
        """Run a single model"""
        try:
            # Run with timeout
            response = await asyncio.wait_for(
                model.generate(request),
                timeout=timeout
            )
            return response

        except asyncio.TimeoutError:
            logger.warning(f"Model {model.metadata.id} timed out")
            return None
        except Exception as e:
            logger.error(f"Error running model {model.metadata.id}: {e}")
            raise

    def _generate_comparison(
        self,
        results: Dict[str, ModelResponse],
        errors: Dict[str, str]
    ) -> Dict[str, Any]:
        """Generate comparison report"""

        comparison = {
            "timestamp": datetime.utcnow().isoformat(),
            "total_models": len(results) + len(errors),
            "successful": len(results),
            "failed": len(errors),
            "models": {},
            "ranking": {
                "by_cost": [],
                "by_speed": [],
                "by_quality": []
            },
            "statistics": {},
            "errors": errors
        }

        # Process each successful result
        for model_id, response in results.items():
            comparison["models"][model_id] = {
                "response": {
                    "content": response.content,
                    "content_length": len(response.content)
                },
                "tokens": {
                    "prompt": response.prompt_tokens,
                    "completion": response.completion_tokens,
                    "total": response.total_tokens
                },
                "cost": {
                    "input": response.input_cost,
                    "output": response.output_cost,
                    "total": response.total_cost
                },
                "performance": {
                    "latency_ms": response.latency_ms,
                    "tokens_per_second": response.tokens_per_second
                },
                "finish_reason": response.finish_reason
            }

        # Calculate statistics
        if results:
            total_costs = [r.total_cost for r in results.values()]
            latencies = [r.latency_ms for r in results.values()]
            tokens_per_sec = [r.tokens_per_second for r in results.values()]

            comparison["statistics"] = {
                "cost": {
                    "min": min(total_costs),
                    "max": max(total_costs),
                    "avg": sum(total_costs) / len(total_costs),
                    "range": max(total_costs) - min(total_costs)
                },
                "latency": {
                    "min": min(latencies),
                    "max": max(latencies),
                    "avg": sum(latencies) / len(latencies),
                    "range": max(latencies) - min(latencies)
                },
                "speed": {
                    "min": min(tokens_per_sec),
                    "max": max(tokens_per_sec),
                    "avg": sum(tokens_per_sec) / len(tokens_per_sec)
                }
            }

            # Generate rankings
            comparison["ranking"]["by_cost"] = sorted(
                results.keys(),
                key=lambda mid: results[mid].total_cost
            )
            comparison["ranking"]["by_speed"] = sorted(
                results.keys(),
                key=lambda mid: results[mid].latency_ms
            )
            comparison["ranking"]["by_quality"] = sorted(
                results.keys(),
                key=lambda mid: len(results[mid].content),
                reverse=True
            )

        return comparison

    async def benchmark(
        self,
        model_id: str,
        test_cases: List[ModelRequest],
        iterations: int = 1
    ) -> Dict[str, Any]:
        """
        Benchmark a single model

        Args:
            model_id: Model ID to benchmark
            test_cases: List of test requests
            iterations: Number of iterations per test case

        Returns:
            Benchmark results
        """
        try:
            model = self.registry.get(model_id)
            if not model:
                return {"error": "Model not found"}

            results = []

            # Run each test case
            for idx, test_case in enumerate(test_cases):
                test_results = []

                # Run iterations
                for iteration in range(iterations):
                    try:
                        response = await model.generate(test_case)
                        test_results.append({
                            "iteration": iteration + 1,
                            "success": True,
                            "latency_ms": response.latency_ms,
                            "total_tokens": response.total_tokens,
                            "total_cost": response.total_cost,
                            "tokens_per_second": response.tokens_per_second
                        })
                    except Exception as e:
                        test_results.append({
                            "iteration": iteration + 1,
                            "success": False,
                            "error": str(e)
                        })

                # Calculate test case statistics
                successful = [r for r in test_results if r.get("success")]
                if successful:
                    results.append({
                        "test_case": idx + 1,
                        "iterations": iterations,
                        "successful": len(successful),
                        "failed": len(test_results) - len(successful),
                        "avg_latency_ms": sum(r["latency_ms"] for r in successful) / len(successful),
                        "avg_cost": sum(r["total_cost"] for r in successful) / len(successful),
                        "avg_tokens_per_second": sum(r["tokens_per_second"] for r in successful) / len(successful),
                        "results": test_results
                    })

            # Generate overall benchmark report
            benchmark = {
                "model_id": model_id,
                "timestamp": datetime.utcnow().isoformat(),
                "test_cases": len(test_cases),
                "iterations_per_case": iterations,
                "results": results
            }

            # Calculate overall statistics
            if results:
                all_successful = sum(r["successful"] for r in results)
                all_total = len(test_cases) * iterations

                benchmark["overall"] = {
                    "total_requests": all_total,
                    "successful": all_successful,
                    "success_rate": all_successful / all_total if all_total > 0 else 0,
                    "avg_latency_ms": sum(r["avg_latency_ms"] for r in results) / len(results),
                    "avg_cost": sum(r["avg_cost"] for r in results) / len(results),
                    "avg_tokens_per_second": sum(r["avg_tokens_per_second"] for r in results) / len(results)
                }

            return benchmark

        except Exception as e:
            logger.error(f"Error benchmarking model: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    def generate_report(
        self,
        comparison: Dict[str, Any],
        format: str = "text"
    ) -> str:
        """
        Generate human-readable comparison report

        Args:
            comparison: Comparison results
            format: Output format (text, markdown, html)

        Returns:
            Formatted report
        """
        if format == "markdown":
            return self._generate_markdown_report(comparison)
        elif format == "html":
            return self._generate_html_report(comparison)
        else:
            return self._generate_text_report(comparison)

    def _generate_text_report(self, comparison: Dict[str, Any]) -> str:
        """Generate plain text report"""
        lines = []
        lines.append("=" * 60)
        lines.append("MODEL COMPARISON REPORT")
        lines.append("=" * 60)
        lines.append(f"Timestamp: {comparison['timestamp']}")
        lines.append(f"Models compared: {comparison['total_models']}")
        lines.append(f"Successful: {comparison['successful']}")
        lines.append(f"Failed: {comparison['failed']}")
        lines.append("")

        # Rankings
        if comparison['ranking']['by_cost']:
            lines.append("COST RANKING (cheapest first):")
            for idx, model_id in enumerate(comparison['ranking']['by_cost'], 1):
                cost = comparison['models'][model_id]['cost']['total']
                lines.append(f"  {idx}. {model_id}: ${cost:.6f}")
            lines.append("")

        if comparison['ranking']['by_speed']:
            lines.append("SPEED RANKING (fastest first):")
            for idx, model_id in enumerate(comparison['ranking']['by_speed'], 1):
                latency = comparison['models'][model_id]['performance']['latency_ms']
                lines.append(f"  {idx}. {model_id}: {latency:.2f}ms")
            lines.append("")

        # Statistics
        if comparison['statistics']:
            lines.append("STATISTICS:")
            stats = comparison['statistics']
            lines.append(f"  Cost Range: ${stats['cost']['min']:.6f} - ${stats['cost']['max']:.6f}")
            lines.append(f"  Latency Range: {stats['latency']['min']:.2f}ms - {stats['latency']['max']:.2f}ms")
            lines.append("")

        # Errors
        if comparison['errors']:
            lines.append("ERRORS:")
            for model_id, error in comparison['errors'].items():
                lines.append(f"  {model_id}: {error}")

        lines.append("=" * 60)

        return "\n".join(lines)

    def _generate_markdown_report(self, comparison: Dict[str, Any]) -> str:
        """Generate markdown report"""
        lines = []
        lines.append("# Model Comparison Report")
        lines.append("")
        lines.append(f"**Timestamp**: {comparison['timestamp']}")
        lines.append(f"**Models Compared**: {comparison['total_models']}")
        lines.append("")

        # Detailed results table
        lines.append("## Results")
        lines.append("")
        lines.append("| Model | Cost | Latency | Tokens/sec | Content Length |")
        lines.append("|-------|------|---------|------------|----------------|")

        for model_id, data in comparison['models'].items():
            cost = data['cost']['total']
            latency = data['performance']['latency_ms']
            tps = data['performance']['tokens_per_second']
            length = data['response']['content_length']
            lines.append(f"| {model_id} | ${cost:.6f} | {latency:.2f}ms | {tps:.1f} | {length} |")

        lines.append("")

        # Rankings
        lines.append("## Rankings")
        lines.append("")
        lines.append("### By Cost")
        for idx, model_id in enumerate(comparison['ranking']['by_cost'], 1):
            lines.append(f"{idx}. **{model_id}**")
        lines.append("")

        lines.append("### By Speed")
        for idx, model_id in enumerate(comparison['ranking']['by_speed'], 1):
            lines.append(f"{idx}. **{model_id}**")

        return "\n".join(lines)

    def _generate_html_report(self, comparison: Dict[str, Any]) -> str:
        """Generate HTML report"""
        # Simple HTML generation
        html = f"""
        <html>
        <head><title>Model Comparison Report</title></head>
        <body>
        <h1>Model Comparison Report</h1>
        <p><strong>Timestamp:</strong> {comparison['timestamp']}</p>
        <p><strong>Models Compared:</strong> {comparison['total_models']}</p>

        <h2>Results</h2>
        <table border="1">
        <tr>
            <th>Model</th>
            <th>Cost</th>
            <th>Latency</th>
            <th>Tokens/sec</th>
        </tr>
        """

        for model_id, data in comparison['models'].items():
            cost = data['cost']['total']
            latency = data['performance']['latency_ms']
            tps = data['performance']['tokens_per_second']
            html += f"""
            <tr>
                <td>{model_id}</td>
                <td>${cost:.6f}</td>
                <td>{latency:.2f}ms</td>
                <td>{tps:.1f}</td>
            </tr>
            """

        html += """
        </table>
        </body>
        </html>
        """

        return html
