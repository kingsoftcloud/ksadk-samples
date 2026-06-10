CAMPAIGN_BRIEF = {
    "product": "Agent Runtime Platform",
    "audience": ["Agent 应用开发者", "平台工程师", "开源贡献者"],
    "objective": "让开发者理解统一 Runtime、Web UI 调试、Sandbox 和部署工作流的价值。",
    "tone": "技术可信、中文优先、避免夸大竞品差异",
}

CHANNELS = [
    {"name": "GitHub README", "purpose": "第一屏说明项目定位和 30 秒体验路径", "asset": "简洁 hero、安装命令、场景导航"},
    {"name": "技术博客", "purpose": "解释为什么 Agent 需要 Runtime Platform", "asset": "架构图、长任务恢复、Sandbox 示例"},
    {"name": "社区短帖", "purpose": "用真实 Web UI GIF 吸引试用", "asset": "截图、GIF、三条关键能力"},
    {"name": "开发者群", "purpose": "收集试用反馈和缺失场景", "asset": "示例问题、常见问题、贡献入口"},
]

DRAFTS = [
    {"format": "README 摘要", "text": "Build agents once. Run them anywhere. 用统一 Runtime 调试、运行和部署多框架 Agent。"},
    {"format": "博客标题", "text": "从框架脚本到 Agent Runtime Platform：KsADK 的开源样例实践"},
    {"format": "社区短帖", "text": "一个命令启动 Web UI，观察 LangGraph Agent 的计划、证据和交付物。"},
]

REVIEW_ITEMS = [
    "不得使用真实客户名称、账号、私有 endpoint 或未发布版本承诺。",
    "能力对比必须符合事实，只突出 Runtime、调试、部署和可观测性差异。",
    "README 保持中文优先，英文 slogan 只作为辅助。",
    "所有示例命令必须能在公开仓库 clone 后运行或清楚说明降级行为。",
]
