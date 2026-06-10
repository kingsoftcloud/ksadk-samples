from __future__ import annotations

# 本地公开运维告警 fixture。真实项目可替换为 Prometheus、日志平台、Tracing 或变更系统 API。
ALERTS = [
    {"metric": "payment_api_5xx_rate", "value": "12.8%", "baseline": "0.6%", "window": "10m", "severity": "P1"},
    {"metric": "payment_api_p95_latency", "value": "1840ms", "baseline": "320ms", "window": "10m", "severity": "P1"},
    {"metric": "checkout_success_rate", "value": "91.2%", "baseline": "98.7%", "window": "10m", "severity": "P1"},
]

LOG_CLUES = [
    {"source": "payment-api", "signal": "TimeoutError: risk-service call exceeded 1500ms", "count": 384},
    {"source": "risk-service", "signal": "connection pool exhausted", "count": 129},
    {"source": "gateway", "signal": "retry budget exceeded for /pay/confirm", "count": 221},
]

CHANGE_EVENTS = [
    {"time": "10:12", "service": "risk-service", "event": "发布 v2026.06.11-rc2，连接池默认值从 80 调整为 20"},
    {"time": "10:19", "service": "payment-api", "event": "自动扩容从 6 副本增加到 10 副本"},
]

RUNBOOK_STEPS = [
    "冻结 risk-service 最近一次发布，确认是否需要回滚连接池配置。",
    "临时提升 risk-service 连接池和副本数，保护支付确认链路。",
    "在网关侧降低高风险重试，避免重试放大下游压力。",
    "把 5xx、p95 延迟和 checkout_success_rate 纳入同一条 incident timeline。",
]

POSTMORTEM_ITEMS = [
    "为连接池配置增加发布前容量检查。",
    "把 risk-service 饱和度加入支付链路 SLO 看板。",
    "补充回滚演练和告警抑制策略，避免重复通知淹没值班。",
]
