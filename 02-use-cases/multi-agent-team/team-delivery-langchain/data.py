from __future__ import annotations

# 本地公开团队角色。真实项目可以替换为多 Agent 子图、子 Agent 服务或任务队列。
TEAM_ROLES = [
    {"name": "Planner", "responsibility": "拆解目标、定义完成标准和里程碑。", "artifact": "执行计划"},
    {"name": "Researcher", "responsibility": "参考 ADK、VEADK、DeerFlow、OpenHands 等优秀样例。", "artifact": "对标笔记"},
    {"name": "Builder", "responsibility": "实现多文件 Agent 工程、README 和可运行 demo。", "artifact": "代码变更"},
    {"name": "Reviewer", "responsibility": "检查事实、开源安全、门禁和演示效果。", "artifact": "验收意见"},
]

PARALLEL_TASKS = [
    {"role": "Planner", "task": "把需求拆成场景、框架和验证三条线。", "status": "done"},
    {"role": "Researcher", "task": "提炼深度研究、编码、浏览器、数据分析、客服和团队协作的样例模式。", "status": "done"},
    {"role": "Builder", "task": "补齐 LangGraph / ADK / LangChain / DeepAgents 的多文件工程。", "status": "running"},
    {"role": "Reviewer", "task": "运行 demo.py、agentengine run smoke 和 public-preflight。", "status": "pending"},
]

MERGE_RULES = [
    "如果速度和质量冲突，以门禁和可运行性优先。",
    "如果 README 和代码行为冲突，以本地可验证行为为准并回写 README。",
    "如果样例涉及平台能力，必须写清未配置时的降级行为。",
]

ACCEPTANCE_CHECKS = [
    "每个 README-advertised demo 都能本地运行。",
    "ADK / LangChain / DeepAgents 不只是占位目录，而是有对应框架入口。",
    "README 和注释中文优先，且不包含私有 endpoint、token 或客户数据。",
    "make public-preflight 通过后再提交和推送。",
]
