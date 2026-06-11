TEAM_OVERVIEW = {
    "team": "Agent Runtime 平台团队",
    "sprint": "2026-Q2 开源发布冲刺",
    "throughput": "完成 18 个需求、修复 9 个缺陷",
    "quality": "CI 成功率 92%，回归缺陷 3 个",
    "delivery": "平均 PR 等待评审 14 小时，平均发布准备 2.5 天",
}

BOTTLENECKS = [
    {"area": "评审等待", "signal": "PR 等待超过 24 小时的比例 28%", "impact": "功能合并延迟，测试窗口被压缩", "fix": "设置评审轮值和高优先级 PR SLA。"},
    {"area": "CI 反馈", "signal": "E2E 失败后平均定位 6 小时", "impact": "修复周期长，开发者不敢频繁提交", "fix": "拆分冒烟用例和慢速用例，保留失败日志 artifact。"},
    {"area": "样例回归", "signal": "README 承诺和 demo 运行结果偶尔脱节", "impact": "开源用户照做时容易失败", "fix": "把 README 承诺目录纳入结构测试和 public-preflight。"},
]

IMPROVEMENT_PLAN = [
    "为 PR 建立 review owner 和 12 小时响应 SLA。",
    "把 public-preflight、LangGraph API smoke 和离线 demo 输出纳入发布 checklist。",
    "为慢速 E2E 保存请求、响应、日志和截图，减少复盘成本。",
    "每周复盘一次 README 承诺、样例可运行性和 CI flakiness。",
]

METRICS = [
    {"metric": "PR 首次响应时间", "target": "P75 < 12 小时", "why": "减少排队等待。"},
    {"metric": "CI 首次通过率", "target": ">= 95%", "why": "降低集成摩擦。"},
    {"metric": "样例本地运行成功率", "target": "100%", "why": "保证开源用户照 README 可上手。"},
    {"metric": "发布准备周期", "target": "<= 1 天", "why": "缩短从修复到可发布的等待时间。"},
]
