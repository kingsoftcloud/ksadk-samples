JOB_PROFILE = {
    "title": "Agent Runtime 平台工程师",
    "must_have": ["Python", "分布式系统", "Agent Runtime", "可观测性"],
    "nice_to_have": ["LangGraph", "Kubernetes", "OpenTelemetry", "Sandbox"],
    "level": "P6-P7",
}

CANDIDATES = [
    {"name": "候选人 A", "years": 7, "strength": "Python 和平台工程经验扎实", "gap": "Agent 框架经验需要追问", "match": 86},
    {"name": "候选人 B", "years": 5, "strength": "熟悉 LangGraph 和工具调用", "gap": "大规模生产运维经验不足", "match": 82},
    {"name": "候选人 C", "years": 8, "strength": "Kubernetes 和可观测性经验强", "gap": "需要验证 Agent 产品理解", "match": 79},
]

INTERVIEW_ROUNDS = [
    {"round": "技术一面", "focus": "Python、Agent Runtime、工具调用和错误处理", "interviewer": "平台研发"},
    {"round": "系统设计", "focus": "多租户 Runtime、Sandbox 隔离、Tracing 和部署边界", "interviewer": "架构师"},
    {"round": "业务协作", "focus": "开源样例、文档质量、跨团队推进", "interviewer": "产品/研发负责人"},
]

HIRING_RISKS = [
    {"risk": "Agent 框架理解停留在 demo 层", "mitigation": "要求现场设计一个可恢复长任务 Agent。"},
    {"risk": "生产稳定性经验不足", "mitigation": "追问 K8s、多副本、日志和指标排查案例。"},
    {"risk": "开源协作经验不足", "mitigation": "让候选人 review 一个 README 和样例结构。"},
]
