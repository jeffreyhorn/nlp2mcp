#!/usr/bin/env python3
"""Generate interactive HTML dashboard with Chart.js visualizations.

This script generates a static HTML dashboard with:
- Stage timing bar chart
- Sprint progress line chart (parse rate, term reduction over Sprints 8-12)
- Model duration bar chart

Usage:
    # Generate from local diagnostics directory
    python scripts/generate_html_dashboard.py --input diagnostics/

    # Output to specific file
    python scripts/generate_html_dashboard.py --output docs/dashboard.html
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


def load_diagnostics(input_dir: Path) -> list[dict[str, Any]]:
    """Load all JSON diagnostics files from a directory."""
    diagnostics = []
    if not input_dir.exists():
        return diagnostics

    for json_file in sorted(input_dir.glob("*.json")):
        try:
            with open(json_file) as f:
                data = json.load(f)
                diagnostics.append(data)
        except (json.JSONDecodeError, OSError) as e:
            print(f"Warning: Failed to load {json_file}: {e}", file=sys.stderr)

    return diagnostics


def load_sprint_history() -> list[dict[str, Any]]:
    """Load historical sprint data for trend charts."""
    # Historical data from CHANGELOG and baselines
    return [
        {
            "sprint": "Sprint 8",
            "parse_rate": 40.0,
            "convert_rate": 87.5,
            "test_time_s": 24.0,
            "term_reduction": 0.0,  # Not measured
        },
        {
            "sprint": "Sprint 9",
            "parse_rate": 60.0,
            "convert_rate": 90.0,
            "test_time_s": 29.0,
            "term_reduction": 0.0,  # Not measured
        },
        {
            "sprint": "Sprint 10",
            "parse_rate": 90.0,
            "convert_rate": 90.0,
            "test_time_s": 16.0,
            "term_reduction": 15.0,  # Estimated
        },
        {
            "sprint": "Sprint 11",
            "parse_rate": 100.0,
            "convert_rate": 90.0,
            "test_time_s": 17.0,
            "term_reduction": 26.19,
        },
        {
            "sprint": "Sprint 12",
            "parse_rate": 100.0,
            "convert_rate": 90.0,
            "test_time_s": 24.0,
            "term_reduction": 26.19,
        },
    ]


def calculate_stats(diagnostics: list[dict[str, Any]]) -> dict[str, Any]:
    """Calculate aggregate statistics from diagnostics."""
    if not diagnostics:
        return {
            "total_models": 0,
            "successful_models": 0,
            "success_rate": 0.0,
            "stage_stats": {},
            "avg_total_duration": 0.0,
        }

    total = len(diagnostics)
    successful = sum(1 for d in diagnostics if d.get("overall_success", False))

    stage_names = [
        "Parse",
        "Semantic Analysis",
        "Simplification",
        "IR Generation",
        "MCP Generation",
    ]
    stage_stats = {}

    for stage in stage_names:
        stage_data = [
            d["stages"].get(stage)
            for d in diagnostics
            if "stages" in d and stage in d.get("stages", {})
        ]

        if stage_data:
            durations = [s["duration_ms"] for s in stage_data if s]
            successes = sum(1 for s in stage_data if s and s.get("success", False))

            stage_stats[stage] = {
                "count": len(stage_data),
                "success_count": successes,
                "success_rate": (successes / len(stage_data) * 100) if stage_data else 0,
                "avg_duration_ms": sum(durations) / len(durations) if durations else 0,
                "min_duration_ms": min(durations) if durations else 0,
                "max_duration_ms": max(durations) if durations else 0,
            }
        else:
            stage_stats[stage] = {
                "count": 0,
                "success_count": 0,
                "success_rate": 0,
                "avg_duration_ms": 0,
                "min_duration_ms": 0,
                "max_duration_ms": 0,
            }

    total_durations = [d.get("total_duration_ms", 0) for d in diagnostics]
    avg_total = sum(total_durations) / len(total_durations) if total_durations else 0

    return {
        "total_models": total,
        "successful_models": successful,
        "success_rate": (successful / total * 100) if total > 0 else 0,
        "stage_stats": stage_stats,
        "avg_total_duration": avg_total,
    }


def generate_html_dashboard(diagnostics: list[dict[str, Any]], stats: dict[str, Any]) -> str:
    """Generate HTML dashboard with Chart.js visualizations."""
    sprint_history = load_sprint_history()

    # Prepare data for charts
    stage_names = [
        "Parse",
        "Semantic Analysis",
        "Simplification",
        "IR Generation",
        "MCP Generation",
    ]
    stage_durations = [
        stats["stage_stats"].get(s, {}).get("avg_duration_ms", 0) for s in stage_names
    ]

    # Model timing data
    model_data = []
    for d in diagnostics:
        model_name = d.get("model_name", "Unknown")
        total_ms = d.get("total_duration_ms", 0)
        success = d.get("overall_success", False)
        model_data.append({"name": model_name, "duration": total_ms, "success": success})

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NLP2MCP Pipeline Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {{
            --bg-primary: #1a1a2e;
            --bg-secondary: #16213e;
            --bg-card: #0f3460;
            --text-primary: #eee;
            --text-secondary: #aaa;
            --accent-green: #4ade80;
            --accent-blue: #60a5fa;
            --accent-yellow: #fbbf24;
            --accent-red: #f87171;
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            line-height: 1.6;
            padding: 20px;
        }}

        .dashboard {{
            max-width: 1400px;
            margin: 0 auto;
        }}

        header {{
            text-align: center;
            margin-bottom: 30px;
            padding: 20px;
            background: var(--bg-secondary);
            border-radius: 12px;
        }}

        header h1 {{
            font-size: 2rem;
            margin-bottom: 10px;
        }}

        .meta {{
            color: var(--text-secondary);
            font-size: 0.9rem;
        }}

        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }}

        .card {{
            background: var(--bg-card);
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        }}

        .card h2 {{
            font-size: 1.2rem;
            margin-bottom: 15px;
            color: var(--accent-blue);
        }}

        .stat-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 15px;
        }}

        .stat {{
            text-align: center;
            padding: 15px;
            background: var(--bg-secondary);
            border-radius: 8px;
        }}

        .stat-value {{
            font-size: 2rem;
            font-weight: bold;
            color: var(--accent-green);
        }}

        .stat-value.warning {{
            color: var(--accent-yellow);
        }}

        .stat-value.error {{
            color: var(--accent-red);
        }}

        .stat-label {{
            font-size: 0.85rem;
            color: var(--text-secondary);
            margin-top: 5px;
        }}

        .chart-container {{
            position: relative;
            height: 300px;
        }}

        .wide-card {{
            grid-column: 1 / -1;
        }}

        .model-list {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }}

        .model-badge {{
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.85rem;
            background: var(--bg-secondary);
        }}

        .model-badge.success {{
            border: 1px solid var(--accent-green);
            color: var(--accent-green);
        }}

        .model-badge.failure {{
            border: 1px solid var(--accent-red);
            color: var(--accent-red);
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
        }}

        th, td {{
            padding: 10px;
            text-align: left;
            border-bottom: 1px solid var(--bg-secondary);
        }}

        th {{
            color: var(--accent-blue);
            font-weight: 600;
        }}

        footer {{
            text-align: center;
            padding: 20px;
            color: var(--text-secondary);
            font-size: 0.85rem;
        }}

        @media (max-width: 768px) {{
            .grid {{
                grid-template-columns: 1fr;
            }}

            .stat-grid {{
                grid-template-columns: 1fr;
            }}

            header h1 {{
                font-size: 1.5rem;
            }}
        }}
    </style>
</head>
<body>
    <div class="dashboard">
        <header>
            <h1>NLP2MCP Pipeline Dashboard</h1>
            <p class="meta">Generated: {
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    } | Schema: v1.0.0</p>
        </header>

        <!-- Summary Stats -->
        <div class="grid">
            <div class="card">
                <h2>Pipeline Summary</h2>
                <div class="stat-grid">
                    <div class="stat">
                        <div class="stat-value{" warning" if stats["success_rate"] < 90 else ""}">{
        stats["success_rate"]:.0f}%</div>
                        <div class="stat-label">Success Rate</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value">{stats["successful_models"]}/{
        stats["total_models"]
    }</div>
                        <div class="stat-label">Models Passing</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value">{stats["avg_total_duration"]:.0f}ms</div>
                        <div class="stat-label">Avg Duration</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value">5</div>
                        <div class="stat-label">Pipeline Stages</div>
                    </div>
                </div>
            </div>

            <div class="card">
                <h2>Model Status</h2>
                <div class="model-list">
                    {
        "".join(
            f'<span class="model-badge {"success" if m["success"] else "failure"}">{m["name"]}</span>'
            for m in model_data
        )
    }
                </div>
            </div>
        </div>

        <!-- Charts Row -->
        <div class="grid">
            <div class="card">
                <h2>Stage Timing (Avg ms)</h2>
                <div class="chart-container">
                    <canvas id="stageTimingChart"></canvas>
                </div>
            </div>

            <div class="card">
                <h2>Sprint Progress</h2>
                <div class="chart-container">
                    <canvas id="sprintProgressChart"></canvas>
                </div>
            </div>
        </div>

        <!-- Wide Charts -->
        <div class="grid">
            <div class="card wide-card">
                <h2>Model Pipeline Duration</h2>
                <div class="chart-container">
                    <canvas id="modelDurationChart"></canvas>
                </div>
            </div>
        </div>

        <!-- Stage Details Table -->
        <div class="grid">
            <div class="card wide-card">
                <h2>Stage Performance Details</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Stage</th>
                            <th>Success Rate</th>
                            <th>Avg (ms)</th>
                            <th>Min (ms)</th>
                            <th>Max (ms)</th>
                        </tr>
                    </thead>
                    <tbody>
                        {
        "".join(
            f'''
                        <tr>
                            <td>{stage}</td>
                            <td>{stats['stage_stats'].get(stage, {}).get('success_rate', 0):.0f}%</td>
                            <td>{stats['stage_stats'].get(stage, {}).get('avg_duration_ms', 0):.1f}</td>
                            <td>{stats['stage_stats'].get(stage, {}).get('min_duration_ms', 0):.1f}</td>
                            <td>{stats['stage_stats'].get(stage, {}).get('max_duration_ms', 0):.1f}</td>
                        </tr>
                        '''
            for stage in stage_names
        )
    }
                    </tbody>
                </table>
            </div>
        </div>

        <footer>
            <p>Dashboard generated by <code>scripts/generate_html_dashboard.py</code></p>
            <p>Diagnostics schema: v1.0.0 | See <code>docs/schemas/diagnostics_v1.0.0.json</code></p>
        </footer>
    </div>

    <script>
        // Chart.js configuration
        Chart.defaults.color = '#aaa';
        Chart.defaults.borderColor = 'rgba(255,255,255,0.1)';

        // Stage Timing Bar Chart
        new Chart(document.getElementById('stageTimingChart'), {{
            type: 'bar',
            data: {{
                labels: {json.dumps(stage_names)},
                datasets: [{{
                    label: 'Duration (ms)',
                    data: {json.dumps(stage_durations)},
                    backgroundColor: [
                        'rgba(96, 165, 250, 0.8)',
                        'rgba(74, 222, 128, 0.8)',
                        'rgba(251, 191, 36, 0.8)',
                        'rgba(248, 113, 113, 0.8)',
                        'rgba(167, 139, 250, 0.8)'
                    ],
                    borderRadius: 4
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{ display: false }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true,
                        title: {{ display: true, text: 'Duration (ms)' }}
                    }}
                }}
            }}
        }});

        // Sprint Progress Line Chart
        new Chart(document.getElementById('sprintProgressChart'), {{
            type: 'line',
            data: {{
                labels: {json.dumps([s["sprint"] for s in sprint_history])},
                datasets: [
                    {{
                        label: 'Parse Rate (%)',
                        data: {json.dumps([s["parse_rate"] for s in sprint_history])},
                        borderColor: 'rgba(74, 222, 128, 1)',
                        backgroundColor: 'rgba(74, 222, 128, 0.1)',
                        fill: true,
                        tension: 0.3
                    }},
                    {{
                        label: 'Term Reduction (%)',
                        data: {json.dumps([s["term_reduction"] for s in sprint_history])},
                        borderColor: 'rgba(96, 165, 250, 1)',
                        backgroundColor: 'rgba(96, 165, 250, 0.1)',
                        fill: true,
                        tension: 0.3
                    }}
                ]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{ position: 'bottom' }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true,
                        max: 100,
                        title: {{ display: true, text: 'Percentage' }}
                    }}
                }}
            }}
        }});

        // Model Duration Bar Chart
        new Chart(document.getElementById('modelDurationChart'), {{
            type: 'bar',
            data: {{
                labels: {json.dumps([m["name"] for m in model_data])},
                datasets: [{{
                    label: 'Duration (ms)',
                    data: {json.dumps([m["duration"] for m in model_data])},
                    backgroundColor: {
        json.dumps(
            [
                "rgba(74, 222, 128, 0.8)" if m["success"] else "rgba(248, 113, 113, 0.8)"
                for m in model_data
            ]
        )
    },
                    borderRadius: 4
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{ display: false }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true,
                        title: {{ display: true, text: 'Duration (ms)' }}
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>
"""
    return html


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate interactive HTML dashboard with Chart.js"
    )
    parser.add_argument(
        "--input",
        "-i",
        type=Path,
        default=Path("diagnostics"),
        help="Directory containing JSON diagnostics files",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=Path("docs/dashboard.html"),
        help="Output HTML file (default: docs/dashboard.html)",
    )

    args = parser.parse_args()

    # Load diagnostics
    print(f"Loading diagnostics from {args.input}...", file=sys.stderr)
    diagnostics = load_diagnostics(args.input)

    if not diagnostics:
        print("No diagnostics data found.", file=sys.stderr)
        sys.exit(1)

    print(f"Loaded {len(diagnostics)} diagnostics files.", file=sys.stderr)

    # Calculate stats and generate dashboard
    stats = calculate_stats(diagnostics)
    html = generate_html_dashboard(diagnostics, stats)

    # Write output
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w") as f:
        f.write(html)
    print(f"Dashboard written to {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
