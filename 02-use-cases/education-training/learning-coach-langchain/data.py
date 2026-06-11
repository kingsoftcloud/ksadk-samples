LEARNER_PROFILE = {
    "learner": "示例企业培训学员组",
    "goal": "四周内掌握 Agent 工程化开发基础",
    "level": "能读懂 Python，缺少 LangGraph 和 Runtime 调试经验",
    "preference": "喜欢先看完整案例，再拆解工具、状态和测试。",
}

SKILL_GAPS = [
    {"topic": "状态建模", "evidence": "练习中经常把用户输入、工具结果和最终答案混在一个字段。", "priority": "高"},
    {"topic": "工具边界", "evidence": "工具函数里直接拼接大段 prompt，难以测试和复用。", "priority": "中"},
    {"topic": "本地验证", "evidence": "只跑 Web UI，没有保留离线 demo 和 smoke test。", "priority": "高"},
]

TRAINING_PLAN = [
    "第 1 周：阅读多文件样例，画出 agent.py、workflow.py、tools.py 和 data.py 的职责边界。",
    "第 2 周：改造一个单文件脚本，拆出工具、prompt、fixture 和离线 demo。",
    "第 3 周：接入 agentengine run/web，观察 API、Web UI 和日志输出是否一致。",
    "第 4 周：补测试、公开扫描和 README，把样例交给同伴复现。",
]

ASSESSMENTS = [
    {"method": "代码练习", "metric": "能在 30 分钟内补齐一个多文件 Agent 工程。"},
    {"method": "口头讲解", "metric": "能解释 Runtime、Workspace、Sandbox、Memory 的接入位置。"},
    {"method": "回归验证", "metric": "能运行 demo.py、agentengine run 和结构测试。"},
]
