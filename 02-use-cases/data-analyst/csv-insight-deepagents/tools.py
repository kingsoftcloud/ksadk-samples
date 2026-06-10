from __future__ import annotations

from langchain_core.tools import tool

from data import CHART_SUGGESTIONS, CSV_ROWS, METRIC_DEFINITIONS
from prompts import SYSTEM_PROMPT, TITLE


@tool
def load_csv_rows(query: str) -> list[dict]:
    """加载 CSV 行数据。

    这里默认读取本地 fixture；真实项目可替换为 Workspace 文件、DuckDB SQL 或数据平台 API。
    """

    return CSV_ROWS


@tool
def calculate_metrics(query: str) -> list[dict]:
    """计算每周核心指标。"""

    return _calculate_metrics_from_rows(CSV_ROWS)


def _calculate_metrics_from_rows(rows: list[dict]) -> list[dict]:
    metrics = []
    previous = None
    for row in rows:
        activation_rate = row["activated"] / row["visitors"]
        retention_rate = row["retained"] / row["activated"]
        webui_intensity = row["webui_runs"] / row["activated"]
        metrics.append(
            {
                "week": row["week"],
                "activation_rate": activation_rate,
                "retention_rate": retention_rate,
                "webui_intensity": webui_intensity,
                "activated_delta": None if previous is None else row["activated"] - previous["activated"],
                "retained_delta": None if previous is None else row["retained"] - previous["retained"],
            }
        )
        previous = row
    return metrics


def _percent(value: float) -> str:
    return f"{value * 100:.1f}%"


def _render_sample_table(rows: list[dict]) -> str:
    lines = ["| week | visitors | activated | retained | webui_runs |", "| --- | ---: | ---: | ---: | ---: |"]
    for row in rows:
        lines.append(
            f"| {row['week']} | {row['visitors']} | {row['activated']} | {row['retained']} | {row['webui_runs']} |"
        )
    return "\n".join(lines)


def _render_metric_table(metrics: list[dict]) -> str:
    lines = ["| week | 激活率 | 留存率 | Web UI 使用强度 |", "| --- | ---: | ---: | ---: |"]
    for item in metrics:
        lines.append(
            f"| {item['week']} | {_percent(item['activation_rate'])} | {_percent(item['retention_rate'])} | {item['webui_intensity']:.2f} |"
        )
    return "\n".join(lines)


def _rank_insights(metrics: list[dict]) -> list[str]:
    latest = metrics[-1]
    first = metrics[0]
    activation_gain = latest["activation_rate"] - first["activation_rate"]
    retention_gain = latest["retention_rate"] - first["retention_rate"]
    intensity_gain = latest["webui_intensity"] - first["webui_intensity"]
    return [
        f"激活率从 {_percent(first['activation_rate'])} 提升到 {_percent(latest['activation_rate'])}，说明样例入口和首次运行链路在改善。",
        f"留存率从 {_percent(first['retention_rate'])} 提升到 {_percent(latest['retention_rate'])}，但增幅 {_percent(retention_gain)} 仍低于 Web UI 使用强度增幅。",
        f"Web UI 使用强度增加 {intensity_gain:.2f} 次/激活用户，建议重点观察调试体验是否带动二次使用。",
        f"最近一周激活用户净增 {latest['activated_delta']}、留存用户净增 {latest['retained_delta']}，适合继续拆解渠道或框架维度。",
    ]


def render_demo_answer(query: str) -> str:
    """生成离线 CSV 洞察报告。"""

    rows = CSV_ROWS
    metrics = _calculate_metrics_from_rows(CSV_ROWS)
    sample_table = _render_sample_table(rows)
    metric_table = _render_metric_table(metrics)
    definitions = "\n".join(
        f"- **{item['name']}**：`{item['formula']}`，{item['meaning']}" for item in METRIC_DEFINITIONS
    )
    insights = "\n".join(f"{index}. {text}" for index, text in enumerate(_rank_insights(metrics), 1))
    charts = "\n".join(f"- {text}" for text in CHART_SUGGESTIONS)
    goal_line = next((line.strip() for line in SYSTEM_PROMPT.splitlines() if line.strip().startswith("这个场景")), "")
    return f"""# {TITLE}

**用户问题**：{query}

## 结论

{goal_line} 当前 demo 使用本地 CSV fixture，不伪造真实线上指标；接入 Workspace CSV 或 DuckDB 后可复用同一套指标口径。

## 数据样本

{sample_table}

## 指标口径

{definitions}

{metric_table}

## 洞察排序

{insights}

## 图表建议

{charts}

## 工程说明

- `agent.py` 暴露框架入口。
- `tools.py` 负责加载 CSV、计算指标和渲染 Markdown。
- `data.py` 可替换为真实 CSV、DuckDB 查询或 BI API 输出。
""".strip()


def collect_evidence(query: str) -> list[dict]:
    """LangGraph 节点使用的证据收集函数。"""

    return _calculate_metrics_from_rows(CSV_ROWS)


def plan_actions(query: str, evidence: list[dict]) -> list[dict]:
    """LangGraph 节点使用的行动规划函数。"""

    return [
        {"step": 1, "owner": "数据分析师", "action": "确认 CSV 字段和指标口径", "why": "避免图表好看但口径错误。"},
        {"step": 2, "owner": "数据分析师", "action": "计算周趋势并排序洞察", "why": "先定位变化最大的指标。"},
        {"step": 3, "owner": "产品和研发", "action": "补充渠道、框架和 Web UI 埋点维度", "why": "把趋势拆到可行动的改进项。"},
    ]


def render_answer(query: str, evidence: list[dict], actions: list[dict]) -> str:
    """LangGraph 输出节点复用离线渲染。"""

    return render_demo_answer(query)
