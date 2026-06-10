KNOWLEDGE_ASSETS = [
    {"id": "doc-runtime-overview", "title": "Runtime 总览", "status": "published", "signal": "新用户能理解定位，但不知道该从哪个 demo 开始。"},
    {"id": "doc-sandbox", "title": "Sandbox 配置", "status": "published", "signal": "用户经常询问未配置时的降级行为。"},
    {"id": "faq-webui", "title": "Web UI 常见问题", "status": "draft", "signal": "需要补充真实截图和问答失败排查步骤。"},
    {"id": "guide-memory", "title": "Memory 与 Knowledge 区别", "status": "needs_update", "signal": "反馈显示两个概念容易混淆。"},
]

FEEDBACK_SIGNALS = [
    "README 能跑起来，但不清楚 Skill Runtime、Workspace、Sandbox 分别怎么配置。",
    "Web UI 截图很有帮助，希望每个主推 demo 都有真实效果图。",
    "知识库和长期记忆的边界需要更多例子。",
    "升级版本后希望 changelog 能直接链接到对应示例。",
]

UPDATE_PLAN = [
    {"target": "doc-runtime-overview", "action": "补一段按场景选择 demo 的导览。", "owner": "docs"},
    {"target": "doc-sandbox", "action": "增加未配置、E2B 配置、远端 Runtime 三种路径。", "owner": "runtime"},
    {"target": "faq-webui", "action": "加入真实 Web UI 截图和失败排查 checklist。", "owner": "samples"},
    {"target": "guide-memory", "action": "用对话记忆、知识库检索和长期画像三个例子区分概念。", "owner": "docs"},
]

RELEASE_CHECKS = [
    "所有链接必须指向公开文档或公开仓库。",
    "示例环境变量只能使用占位符，不能包含真实凭证。",
    "新增知识库页面必须能从 README 或导航入口发现。",
    "发布前运行 public-preflight 并保留 CI 绿灯记录。",
]
