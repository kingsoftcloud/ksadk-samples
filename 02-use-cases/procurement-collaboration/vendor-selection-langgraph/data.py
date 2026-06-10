PROCUREMENT_REQUESTS = [
    {"item": "Agent Sandbox 计算资源", "quantity": "3 个月", "priority": "高", "requirement": "隔离执行、日志留存、可扩容"},
    {"item": "Web UI 录屏与截图工具", "quantity": "20 席", "priority": "中", "requirement": "支持团队协作、导出 GIF、权限管理"},
    {"item": "文档站监控服务", "quantity": "1 年", "priority": "中", "requirement": "可用性监控、链接检查、告警通知"},
]

VENDORS = [
    {"name": "供应商 A", "score": 87, "strength": "交付快，Sandbox 能力成熟", "risk": "报价偏高"},
    {"name": "供应商 B", "score": 81, "strength": "文档和协作功能完整", "risk": "需要补充安全审计材料"},
    {"name": "供应商 C", "score": 76, "strength": "价格有优势", "risk": "扩容能力和 SLA 需要确认"},
]

NEGOTIATION_ITEMS = [
    "要求高优先级资源给出阶梯报价和容量保障条款。",
    "把日志留存、安全审计和故障响应写入合同附件。",
    "对中优先级工具争取试用期和按席位弹性计费。",
    "要求供应商在验收前提供公开可分享的技术材料。",
]

APPROVAL_RISKS = [
    {"risk": "预算拆分不清", "owner": "采购", "mitigation": "按资源、工具、监控三类拆分预算。"},
    {"risk": "安全材料缺失", "owner": "安全", "mitigation": "要求供应商补安全白皮书和审计日志样例。"},
    {"risk": "SLA 不可验证", "owner": "平台", "mitigation": "把可用性、响应时间和赔付条款写入验收。"},
]
