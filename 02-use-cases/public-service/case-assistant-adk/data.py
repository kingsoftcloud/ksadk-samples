CASE_PROFILE = {
    "service": "示例企业开办联办事项",
    "applicant": "公开虚构企业申请人",
    "status": "材料初审中",
    "pain_point": "申请人多次补正经营范围说明和授权材料。",
}

MATERIAL_CHECKS = [
    {"material": "主体信息表", "status": "已齐", "note": "字段完整，需后台复核。"},
    {"material": "授权委托书", "status": "待补正", "note": "缺少经办人签名页。"},
    {"material": "经营范围说明", "status": "需澄清", "note": "表述与示例分类不一致。"},
]

WORKFLOW_ACTIONS = [
    "窗口一次性告知授权委托书缺失页，并提供线上补正入口。",
    "后台审批人员提前标注经营范围说明的可选分类，减少反复退回。",
    "短信提醒申请人补正截止时间和材料示例链接。",
    "办结后回访一次，记录材料说明是否清晰并更新知识库。",
]

SERVICE_COMMITMENTS = [
    {"commitment": "办理时限", "rule": "材料补齐后 1 个工作日内完成初审。"},
    {"commitment": "隐私保护", "rule": "样例不得保存真实身份证、手机号、营业执照或账号。"},
    {"commitment": "人工复核", "rule": "Agent 只给协同建议，最终审批结论由授权人员确认。"},
]
