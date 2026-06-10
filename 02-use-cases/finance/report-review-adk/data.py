from __future__ import annotations

# 本地公开财务报表 fixture。真实项目可以替换为 Workspace 上传的 Excel、财务系统 API 或审计数据集。
REPORT_ROWS = [
    {"quarter": "2026-Q1", "revenue": 1280, "gross_margin": 0.42, "operating_cashflow": 210, "ar_days": 42},
    {"quarter": "2026-Q2", "revenue": 1510, "gross_margin": 0.39, "operating_cashflow": 168, "ar_days": 51},
    {"quarter": "2026-Q3", "revenue": 1760, "gross_margin": 0.34, "operating_cashflow": 96, "ar_days": 67},
]

RISK_THRESHOLDS = [
    {"name": "毛利率连续下滑", "rule": "gross_margin 环比下降超过 3 个百分点", "severity": "中"},
    {"name": "经营现金流弱化", "rule": "operating_cashflow 增速低于 revenue 增速", "severity": "高"},
    {"name": "应收账款周转变慢", "rule": "ar_days 超过 60 天", "severity": "高"},
]

EXPLANATION_NOTES = [
    "收入增长主要来自大客户项目确认，但毛利率受交付成本和折扣影响下滑。",
    "经营现金流没有跟随收入增长，说明回款节奏和成本支付存在错配。",
    "应收账款天数从 42 天升至 67 天，需要关注信用政策和逾期账款。",
]

REVIEW_ACTIONS = [
    "要求销售和财务拆分 Q3 新增收入的客户、合同和回款计划。",
    "复核大客户折扣、交付成本归集和收入确认依据。",
    "对应收账款超过 60 天的客户建立专项跟踪表。",
]
