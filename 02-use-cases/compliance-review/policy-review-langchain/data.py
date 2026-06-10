MATERIALS = [
    {"id": "release-post", "title": "开源发布博客", "owner": "marketing", "claim": "统一 Runtime 能显著降低多框架接入成本"},
    {"id": "comparison-table", "title": "能力对比表", "owner": "docs", "claim": "突出 Runtime、Web UI、部署和可观测性"},
    {"id": "customer-slide", "title": "客户演示页", "owner": "sales", "claim": "引用客户反馈时必须脱敏"},
]

POLICY_RULES = [
    {"rule": "事实可验证", "risk": "不能把未验证结论写成确定性承诺。", "severity": "high"},
    {"rule": "竞品表述准确", "risk": "能力对比必须基于公开事实，不得贬损或误导。", "severity": "high"},
    {"rule": "客户信息脱敏", "risk": "不得出现真实客户名称、账号、内部链接或未授权案例。", "severity": "critical"},
    {"rule": "版本边界清晰", "risk": "未发布功能必须标注计划或预览，不得进入稳定能力清单。", "severity": "medium"},
]

REMEDIATIONS = [
    "把夸张表述改成基于当前样例和公开文档可验证的描述。",
    "能力对比只保留事实差异，并在 README 中引导读者看详细文档。",
    "移除客户名称和内部链接，使用公开 fixture 或通用行业描述。",
    "为未发布能力增加版本边界和 changelog 链接。",
]

REVIEW_LOG = [
    {"step": "材料读取", "result": "3 份材料进入审阅队列。"},
    {"step": "规则匹配", "result": "命中事实可验证、竞品表述和脱敏规则。"},
    {"step": "整改输出", "result": "生成可交给文档和市场团队的修改清单。"},
]
