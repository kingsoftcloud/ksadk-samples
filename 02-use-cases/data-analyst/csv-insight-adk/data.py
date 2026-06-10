from __future__ import annotations

# 模拟 CSV 数据。真实项目可以替换为 Workspace 上传的 CSV、DuckDB 查询结果或 BI API。
CSV_ROWS = [
    {"week": "2026-W21", "visitors": 1200, "activated": 420, "retained": 180, "webui_runs": 260},
    {"week": "2026-W22", "visitors": 1480, "activated": 570, "retained": 260, "webui_runs": 390},
    {"week": "2026-W23", "visitors": 1720, "activated": 690, "retained": 330, "webui_runs": 520},
    {"week": "2026-W24", "visitors": 1900, "activated": 820, "retained": 430, "webui_runs": 710},
]

METRIC_DEFINITIONS = [
    {"name": "激活率", "formula": "activated / visitors", "meaning": "访问样例后完成首次运行的比例。"},
    {"name": "留存率", "formula": "retained / activated", "meaning": "激活用户中下一周继续使用的比例。"},
    {"name": "Web UI 使用强度", "formula": "webui_runs / activated", "meaning": "每个激活用户平均打开 Web UI 调试的次数。"},
]

CHART_SUGGESTIONS = [
    "折线图：展示 visitors、activated、retained 的周趋势。",
    "组合柱线图：柱状展示 activated，折线展示激活率。",
    "散点图：观察 Web UI 使用强度和留存率是否同向变化。",
]
