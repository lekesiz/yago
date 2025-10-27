"""
Enhanced Report Generator for YAGO
Generates detailed HTML/Markdown/JSON reports with visualizations
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger("YAGO")


class ReportGenerator:
    """Generates comprehensive execution reports"""

    def __init__(self, output_dir: str = "reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        self.report_data = {
            "metadata": {},
            "timeline": [],
            "agents": {},
            "tokens": {},
            "errors": [],
            "files_generated": [],
            "metrics": {}
        }

    def _safe_int(self, value: Any) -> int:
        """Safely convert value to int, handling dicts and None"""
        if isinstance(value, dict):
            # If it's a dict, try to get a total or sum
            return sum(v for v in value.values() if isinstance(v, (int, float)))
        try:
            return int(value)
        except (TypeError, ValueError):
            return 0

    def set_metadata(self, idea: str, mode: str, start_time: datetime):
        """Set report metadata"""
        self.report_data["metadata"] = {
            "project_idea": idea,
            "execution_mode": mode,
            "start_time": start_time.isoformat(),
            "yago_version": "1.1.0"
        }

    def add_timeline_event(self, event_type: str, agent: str, description: str,
                          timestamp: Optional[datetime] = None):
        """Add event to timeline"""
        if timestamp is None:
            timestamp = datetime.now()

        self.report_data["timeline"].append({
            "timestamp": timestamp.isoformat(),
            "type": event_type,
            "agent": agent,
            "description": description
        })

    def add_agent_activity(self, agent_name: str, task: str, duration: float,
                          tokens_used: int, cost: float, iterations: int):
        """Record agent activity"""
        if agent_name not in self.report_data["agents"]:
            self.report_data["agents"][agent_name] = []

        self.report_data["agents"][agent_name].append({
            "task": task,
            "duration_seconds": round(duration, 2),
            "tokens": tokens_used,
            "cost_usd": round(cost, 4),
            "iterations": iterations,
            "timestamp": datetime.now().isoformat()
        })

    def add_token_usage(self, provider: str, model: str, input_tokens: int,
                       output_tokens: int, cost: float):
        """Record token usage"""
        key = f"{provider}:{model}"
        if key not in self.report_data["tokens"]:
            self.report_data["tokens"][key] = {
                "provider": provider,
                "model": model,
                "calls": 0,
                "input_tokens": 0,
                "output_tokens": 0,
                "total_cost": 0.0
            }

        self.report_data["tokens"][key]["calls"] += 1
        self.report_data["tokens"][key]["input_tokens"] += input_tokens
        self.report_data["tokens"][key]["output_tokens"] += output_tokens
        self.report_data["tokens"][key]["total_cost"] += cost

    def add_error(self, error_type: str, message: str, context: str,
                 timestamp: Optional[datetime] = None):
        """Record error"""
        if timestamp is None:
            timestamp = datetime.now()

        self.report_data["errors"].append({
            "timestamp": timestamp.isoformat(),
            "type": error_type,
            "message": message,
            "context": context
        })

    def add_generated_file(self, file_path: str, size_bytes: int, language: str):
        """Record generated file"""
        self.report_data["files_generated"].append({
            "path": file_path,
            "size_bytes": size_bytes,
            "language": language,
            "timestamp": datetime.now().isoformat()
        })

    def set_final_metrics(self, total_duration: float, total_cost: float,
                         total_tokens: int, total_api_calls: int,
                         success: bool, workspace_path: str):
        """Set final execution metrics"""
        self.report_data["metadata"]["end_time"] = datetime.now().isoformat()
        self.report_data["metadata"]["success"] = success

        self.report_data["metrics"] = {
            "total_duration_seconds": round(total_duration, 2),
            "total_cost_usd": round(total_cost, 4),
            "total_tokens": total_tokens,
            "total_api_calls": total_api_calls,
            "files_generated_count": len(self.report_data["files_generated"]),
            "errors_count": len(self.report_data["errors"]),
            "workspace_path": workspace_path
        }

    def generate_json(self, filename: Optional[str] = None) -> Path:
        """Generate JSON report"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"yago_report_{timestamp}.json"

        output_path = self.output_dir / filename

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.report_data, f, indent=2, ensure_ascii=False)

        logger.info(f"📄 JSON report saved: {output_path}")
        return output_path

    def generate_markdown(self, filename: Optional[str] = None) -> Path:
        """Generate Markdown report"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"yago_report_{timestamp}.md"

        output_path = self.output_dir / filename

        md_content = self._build_markdown()

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(md_content)

        logger.info(f"📄 Markdown report saved: {output_path}")
        return output_path

    def generate_html(self, filename: Optional[str] = None) -> Path:
        """Generate HTML report with visualizations"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"yago_report_{timestamp}.html"

        output_path = self.output_dir / filename

        html_content = self._build_html()

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        logger.info(f"📄 HTML report saved: {output_path}")
        return output_path

    def generate_all(self, prefix: Optional[str] = None) -> Dict[str, Path]:
        """Generate all report formats"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if prefix:
            base_name = f"{prefix}_{timestamp}"
        else:
            base_name = f"yago_report_{timestamp}"

        return {
            "json": self.generate_json(f"{base_name}.json"),
            "markdown": self.generate_markdown(f"{base_name}.md"),
            "html": self.generate_html(f"{base_name}.html")
        }

    def _build_markdown(self) -> str:
        """Build markdown content"""
        meta = self.report_data["metadata"]
        metrics = self.report_data["metrics"]

        md = f"""# YAGO Execution Report

## Project Information
- **Idea:** {meta.get('project_idea', 'N/A')}
- **Mode:** {meta.get('execution_mode', 'N/A')}
- **Start Time:** {meta.get('start_time', 'N/A')}
- **End Time:** {meta.get('end_time', 'N/A')}
- **Status:** {'✅ Success' if meta.get('success') else '❌ Failed'}
- **YAGO Version:** {meta.get('yago_version', 'N/A')}

## Execution Metrics
- **Total Duration:** {metrics.get('total_duration_seconds', 0):.2f}s
- **Total Cost:** ${metrics.get('total_cost_usd', 0):.4f}
- **Total Tokens:** {self._safe_int(metrics.get('total_tokens', 0)):,}
- **API Calls:** {self._safe_int(metrics.get('total_api_calls', 0))}
- **Files Generated:** {self._safe_int(metrics.get('files_generated_count', 0))}
- **Errors:** {self._safe_int(metrics.get('errors_count', 0))}

## Token Usage by Provider
"""

        for token_key, token_data in self.report_data["tokens"].items():
            md += f"""
### {token_data['provider']} - {token_data['model']}
- Calls: {token_data['calls']}
- Input Tokens: {token_data['input_tokens']:,}
- Output Tokens: {token_data['output_tokens']:,}
- Cost: ${token_data['total_cost']:.4f}
"""

        md += "\n## Agent Activity\n"
        for agent_name, activities in self.report_data["agents"].items():
            md += f"\n### {agent_name}\n"
            total_duration = sum(a['duration_seconds'] for a in activities)
            total_cost = sum(a['cost_usd'] for a in activities)
            md += f"- Total Duration: {total_duration:.2f}s\n"
            md += f"- Total Cost: ${total_cost:.4f}\n"
            md += f"- Tasks Completed: {len(activities)}\n"

        if self.report_data["errors"]:
            md += "\n## Errors\n"
            for error in self.report_data["errors"]:
                md += f"\n### {error['type']}\n"
                md += f"- **Time:** {error['timestamp']}\n"
                md += f"- **Message:** {error['message']}\n"
                md += f"- **Context:** {error['context']}\n"

        if self.report_data["files_generated"]:
            md += "\n## Generated Files\n"
            for file_info in self.report_data["files_generated"]:
                md += f"- `{file_info['path']}` ({file_info['language']}, {file_info['size_bytes']} bytes)\n"

        md += f"\n---\n*Report generated by YAGO v{meta.get('yago_version', '1.0')}*\n"

        return md

    def _build_html(self) -> str:
        """Build HTML content with visualizations"""
        meta = self.report_data["metadata"]
        metrics = self.report_data["metrics"]

        # Calculate provider breakdown for pie chart
        provider_costs = {}
        for token_data in self.report_data["tokens"].values():
            provider = token_data['provider']
            if provider not in provider_costs:
                provider_costs[provider] = 0.0
            provider_costs[provider] += token_data['total_cost']

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>YAGO Report - {meta.get('project_idea', 'Unknown')}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            color: #333;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        .header p {{
            opacity: 0.9;
            font-size: 1.1em;
        }}
        .status {{
            display: inline-block;
            padding: 8px 20px;
            border-radius: 20px;
            background: {'rgba(40, 167, 69, 0.2)' if meta.get('success') else 'rgba(220, 53, 69, 0.2)'};
            color: {'#28a745' if meta.get('success') else '#dc3545'};
            font-weight: bold;
            margin-top: 15px;
        }}
        .content {{
            padding: 40px;
        }}
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        .metric-card {{
            background: #f8f9fa;
            padding: 25px;
            border-radius: 12px;
            text-align: center;
            border-left: 4px solid #667eea;
        }}
        .metric-card .value {{
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 5px;
        }}
        .metric-card .label {{
            color: #6c757d;
            font-size: 0.9em;
        }}
        .section {{
            margin-bottom: 40px;
        }}
        .section h2 {{
            color: #667eea;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #e9ecef;
        }}
        .provider-card {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 15px;
        }}
        .provider-card h3 {{
            color: #495057;
            margin-bottom: 10px;
        }}
        .provider-stats {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
        }}
        .stat {{
            display: flex;
            justify-content: space-between;
            padding: 5px 0;
        }}
        .stat-label {{
            color: #6c757d;
        }}
        .stat-value {{
            font-weight: bold;
        }}
        .timeline {{
            position: relative;
            padding-left: 30px;
        }}
        .timeline::before {{
            content: '';
            position: absolute;
            left: 10px;
            top: 0;
            bottom: 0;
            width: 2px;
            background: #dee2e6;
        }}
        .timeline-item {{
            position: relative;
            margin-bottom: 20px;
            padding-left: 30px;
        }}
        .timeline-item::before {{
            content: '';
            position: absolute;
            left: -24px;
            top: 5px;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: #667eea;
            border: 3px solid white;
            box-shadow: 0 0 0 2px #667eea;
        }}
        .timeline-item .time {{
            color: #6c757d;
            font-size: 0.85em;
            margin-bottom: 5px;
        }}
        .timeline-item .desc {{
            color: #495057;
        }}
        .error-card {{
            background: #f8d7da;
            border: 1px solid #f5c6cb;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 15px;
        }}
        .error-card .error-type {{
            color: #721c24;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        .error-card .error-msg {{
            color: #721c24;
            font-size: 0.9em;
        }}
        .file-list {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
        }}
        .file-item {{
            padding: 10px;
            border-bottom: 1px solid #dee2e6;
        }}
        .file-item:last-child {{
            border-bottom: none;
        }}
        .file-item code {{
            background: #e9ecef;
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 0.9em;
        }}
        .footer {{
            text-align: center;
            padding: 20px;
            background: #f8f9fa;
            color: #6c757d;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 YAGO Execution Report</h1>
            <p>{meta.get('project_idea', 'N/A')}</p>
            <div class="status">{'✅ Success' if meta.get('success') else '❌ Failed'}</div>
        </div>

        <div class="content">
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="value">{metrics.get('total_duration_seconds', 0):.1f}s</div>
                    <div class="label">Duration</div>
                </div>
                <div class="metric-card">
                    <div class="value">${metrics.get('total_cost_usd', 0):.4f}</div>
                    <div class="label">Total Cost</div>
                </div>
                <div class="metric-card">
                    <div class="value">{int(metrics.get('total_tokens', 0)):,}</div>
                    <div class="label">Tokens</div>
                </div>
                <div class="metric-card">
                    <div class="value">{int(metrics.get('total_api_calls', 0))}</div>
                    <div class="label">API Calls</div>
                </div>
                <div class="metric-card">
                    <div class="value">{metrics.get('files_generated_count', 0)}</div>
                    <div class="label">Files Generated</div>
                </div>
                <div class="metric-card">
                    <div class="value">{metrics.get('errors_count', 0)}</div>
                    <div class="label">Errors</div>
                </div>
            </div>

            <div class="section">
                <h2>📊 Token Usage by Provider</h2>
"""

        for token_data in self.report_data["tokens"].values():
            html += f"""
                <div class="provider-card">
                    <h3>{token_data['provider']} - {token_data['model']}</h3>
                    <div class="provider-stats">
                        <div class="stat">
                            <span class="stat-label">API Calls:</span>
                            <span class="stat-value">{token_data['calls']}</span>
                        </div>
                        <div class="stat">
                            <span class="stat-label">Cost:</span>
                            <span class="stat-value">${token_data['total_cost']:.4f}</span>
                        </div>
                        <div class="stat">
                            <span class="stat-label">Input Tokens:</span>
                            <span class="stat-value">{token_data['input_tokens']:,}</span>
                        </div>
                        <div class="stat">
                            <span class="stat-label">Output Tokens:</span>
                            <span class="stat-value">{token_data['output_tokens']:,}</span>
                        </div>
                    </div>
                </div>
"""

        html += """
            </div>
"""

        if self.report_data["timeline"]:
            html += """
            <div class="section">
                <h2>⏱️ Execution Timeline</h2>
                <div class="timeline">
"""
            for event in self.report_data["timeline"][:10]:  # Show first 10 events
                html += f"""
                    <div class="timeline-item">
                        <div class="time">{event['timestamp']}</div>
                        <div class="desc"><strong>{event['agent']}</strong> - {event['description']}</div>
                    </div>
"""
            html += """
                </div>
            </div>
"""

        if self.report_data["errors"]:
            html += """
            <div class="section">
                <h2>❌ Errors</h2>
"""
            for error in self.report_data["errors"]:
                html += f"""
                <div class="error-card">
                    <div class="error-type">{error['type']}</div>
                    <div class="error-msg">{error['message']}</div>
                </div>
"""
            html += """
            </div>
"""

        if self.report_data["files_generated"]:
            html += """
            <div class="section">
                <h2>📁 Generated Files</h2>
                <div class="file-list">
"""
            for file_info in self.report_data["files_generated"]:
                html += f"""
                    <div class="file-item">
                        <code>{file_info['path']}</code>
                        <span style="color: #6c757d; margin-left: 10px;">
                            {file_info['language']} • {file_info['size_bytes']} bytes
                        </span>
                    </div>
"""
            html += """
                </div>
            </div>
"""

        html += f"""
        </div>

        <div class="footer">
            Report generated by YAGO v{meta.get('yago_version', '1.0')} on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </div>
    </div>
</body>
</html>
"""

        return html


# Singleton instance
_report_generator = None

def get_report_generator() -> ReportGenerator:
    """Get or create report generator singleton"""
    global _report_generator
    if _report_generator is None:
        _report_generator = ReportGenerator()
    return _report_generator

def reset_report_generator():
    """Reset report generator (for new run)"""
    global _report_generator
    _report_generator = ReportGenerator()
