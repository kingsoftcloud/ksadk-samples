from __future__ import annotations

# 本地公开知识条目。真实项目可以替换为 KSADK Knowledge Base、工单系统 API 或客服知识库。
KNOWLEDGE_ARTICLES = [
    {
        "id": "kb-webui-no-response",
        "title": "Web UI 启动后无响应",
        "symptom": "页面能打开，但发送消息后没有后续输出。",
        "resolution": "确认 agentengine web 日志、/health、/v1/models、浏览器控制台和模型流式输出。",
        "severity": "P1",
    },
    {
        "id": "kb-skill-not-called",
        "title": "Skill Space 已配置但工具未调用",
        "symptom": "模型只回答文本，没有返回 space 下的 skill 调用痕迹。",
        "resolution": "检查工具绑定、Space ID、服务凭证、prompt 是否要求调用工具，以及 tool dispatcher 日志。",
        "severity": "P1",
    },
    {
        "id": "kb-markdown-rendering",
        "title": "Markdown 表格渲染异常",
        "symptom": "列表或表格在 Web UI 中显示不稳定。",
        "resolution": "默认保留模型原文；业务按需开启 repair_markdown，并补充 CommonMark 回归样例。",
        "severity": "P2",
    },
]

ESCALATION_POLICY = [
    {"level": "P0", "condition": "线上多租户不可用或数据安全风险", "target": "值班研发 + 负责人"},
    {"level": "P1", "condition": "核心调试链路不可用但有替代路径", "target": "AgentEngine Runtime 研发"},
    {"level": "P2", "condition": "展示或格式问题，不阻断主流程", "target": "Web UI / SDK 维护者"},
]

REPLY_STEPS = [
    "复述客户现象并确认影响范围。",
    "匹配知识条目，列出需要客户补充的日志和环境信息。",
    "给出 3 到 5 步可执行排障动作。",
    "根据严重程度决定是否升级工单并标注 owner。",
]
