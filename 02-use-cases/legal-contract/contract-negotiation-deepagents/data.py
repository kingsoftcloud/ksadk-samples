CONTRACT_SUMMARY = {
    "name": "Agent Runtime 平台合作协议（示例）",
    "counterparty": "示例合作方",
    "amount": "人民币 120 万元以内框架额度",
    "term": "12 个月",
    "purpose": "共同验证 Agent Runtime、Web UI 调试和 Sandbox 运行能力。",
}

KEY_CLAUSES = [
    {"clause": "服务范围", "status": "需明确", "note": "应写清 Runtime、Web UI、Sandbox、支持响应和验收边界。"},
    {"clause": "数据安全", "status": "高风险", "note": "需要补充数据留存、访问审计、脱敏和删除机制。"},
    {"clause": "知识产权", "status": "需谈判", "note": "样例、插件和客户私有配置的归属需要区分。"},
    {"clause": "服务等级", "status": "需明确", "note": "SLA、故障响应、赔付上限和免责场景需要量化。"},
]

NEGOTIATION_POINTS = [
    "要求服务范围附件列出 Runtime、Skill、Workspace、Sandbox 和 Web UI 的责任边界。",
    "把客户数据、模型调用日志和调试产物的保留周期写入数据安全条款。",
    "区分开源样例、平台通用能力和客户私有 Agent 代码的知识产权归属。",
    "将 SLA、响应时间、验收标准和整改周期写成可度量指标。",
]

LEGAL_RISKS = [
    {"risk": "数据处理边界不清", "level": "高", "mitigation": "补充数据处理协议和访问审计要求。"},
    {"risk": "验收标准不可量化", "level": "中", "mitigation": "用 API 可用性、Web UI 功能和部署成功率定义验收。"},
    {"risk": "开源与客户私有资产混淆", "level": "中", "mitigation": "合同附件明确 Apache-2.0 样例与客户私有代码边界。"},
]
