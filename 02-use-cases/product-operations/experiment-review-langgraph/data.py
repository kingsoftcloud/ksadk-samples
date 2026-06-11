EXPERIMENT_SUMMARY = {
    "name": "Web UI 新手引导实验（示例）",
    "goal": "提升首次对话完成率和次日回访率",
    "sample": "公开脱敏样本 8,000 次访问",
    "result": "首次对话完成率从 41% 提升到 49%，但高级工具配置页跳出率升高",
}

USER_SEGMENTS = [
    {"segment": "首次体验用户", "size": "52%", "signal": "完成引导后更愿意发送第一条消息", "opportunity": "保留最短路径，减少配置干扰。"},
    {"segment": "工具配置用户", "size": "31%", "signal": "在 Skill、Memory、Sandbox 配置页停留时间长", "opportunity": "提供配置检测和示例 .env。"},
    {"segment": "返回用户", "size": "17%", "signal": "更关注历史会话和文件产物", "opportunity": "突出 workspace、artifact 和会话恢复入口。"},
]

OPTIMIZATION_ACTIONS = [
    "把首次体验路径压缩到模型配置、提问、查看结果三个步骤。",
    "在高级配置页加入检测面板，解释 Skill Runtime、Workspace、Sandbox 和 Memory 的缺失项。",
    "为返回用户增加最近会话、最近 artifact 和上次运行状态入口。",
    "下一轮实验同时观察完成率、配置成功率和次日回访率，避免只优化一个指标。",
]

REVIEW_METRICS = [
    {"metric": "首次对话完成率", "baseline": "41%", "target": ">= 52%"},
    {"metric": "高级配置成功率", "baseline": "34%", "target": ">= 45%"},
    {"metric": "次日回访率", "baseline": "18%", "target": ">= 24%"},
    {"metric": "配置页跳出率", "baseline": "37%", "target": "<= 28%"},
]
