LEADS = [
    {"account": "北辰制造", "stage": "方案评估", "value": 38, "signal": "关注私有化部署和审批周期", "last_touch_days": 5},
    {"account": "星河零售", "stage": "POC", "value": 24, "signal": "Web UI 演示反馈积极，但需要安全评审", "last_touch_days": 2},
    {"account": "云杉教育", "stage": "初步沟通", "value": 12, "signal": "希望先看知识库和长期记忆样例", "last_touch_days": 9},
    {"account": "远航金融", "stage": "商务谈判", "value": 55, "signal": "关心审计记录、部署边界和合规材料", "last_touch_days": 4},
]

PLAYBOOK = [
    {"stage": "初步沟通", "action": "发送场景导航和 30 秒 Quick Start，约技术发现会。"},
    {"stage": "方案评估", "action": "补充架构图、部署边界和成功案例材料。"},
    {"stage": "POC", "action": "安排 Web UI 演示、Sandbox 风险说明和验收指标。"},
    {"stage": "商务谈判", "action": "同步报价、法务材料、审计记录和上线排期。"},
]

CRM_ACTIONS = [
    "为高价值线索创建下周跟进任务，并记录 next step owner。",
    "把安全评审、合规材料和 POC 验收指标写入 CRM 备注。",
    "超过 7 天未触达的线索自动进入复访队列。",
    "对商务谈判阶段线索增加决策人、预算和签约日期字段。",
]

DEAL_RISKS = [
    {"risk": "审批周期不清", "impact": "中", "mitigation": "补齐客户采购路径和关键人。"},
    {"risk": "安全评审材料不足", "impact": "高", "mitigation": "提供部署边界、审计日志和数据流说明。"},
    {"risk": "POC 目标不明确", "impact": "中", "mitigation": "把成功标准写成可验证 checklist。"},
]
