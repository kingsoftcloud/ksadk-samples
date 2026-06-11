DATA_ASSETS = [
    {"asset": "agent_runs_daily", "owner": "平台数据", "usage": "统计 Agent 运行次数、成功率和耗时", "consumer": "运营看板"},
    {"asset": "tool_calls_detail", "owner": "运行时", "usage": "分析工具调用、失败原因和耗时", "consumer": "稳定性分析"},
    {"asset": "webui_events", "owner": "前端", "usage": "分析 Web UI 点击、上传和取消行为", "consumer": "产品运营"},
]

QUALITY_ISSUES = [
    {"issue": "运行状态枚举不一致", "severity": "高", "asset": "agent_runs_daily", "action": "统一 success、failed、cancelled、timeout 枚举。"},
    {"issue": "工具调用缺少 trace_id", "severity": "高", "asset": "tool_calls_detail", "action": "把 trace_id 纳入采集必填字段并补回填任务。"},
    {"issue": "Web UI 事件延迟入仓", "severity": "中", "asset": "webui_events", "action": "增加调度延迟监控和补数告警。"},
    {"issue": "指标口径缺少 owner", "severity": "中", "asset": "全部资产", "action": "为核心指标补充口径文档和责任人。"},
]

GOVERNANCE_ACTIONS = [
    "把核心资产加入数据目录，补充 owner、用途、SLA 和血缘。",
    "为高严重度质量问题创建整改工单，并要求每周同步状态。",
    "为 trace_id、run_id、session_id 建立字段标准和自动校验。",
    "发布前用本地 fixture 回归治理报告，避免真实数据泄露到样例。",
]

RESPONSIBILITY_MATRIX = [
    {"owner": "平台数据", "scope": "指标口径、数据目录和质量规则", "deliverable": "质量规则和口径文档"},
    {"owner": "运行时", "scope": "trace_id、tool call、run 状态采集", "deliverable": "采集字段和回填任务"},
    {"owner": "产品运营", "scope": "使用方校验和看板验收", "deliverable": "验收反馈和业务解释"},
]
