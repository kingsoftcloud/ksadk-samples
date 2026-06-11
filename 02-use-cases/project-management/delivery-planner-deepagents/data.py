PROJECT_STATUS = [
    {"module": "Runtime API", "progress": "80%", "owner": "平台后端", "status": "接口稳定，缺少压测报告"},
    {"module": "Hosted Web UI", "progress": "65%", "owner": "前端", "status": "主链路可用，上传和取消仍需联调"},
    {"module": "Sandbox 镜像", "progress": "70%", "owner": "运行时", "status": "镜像可构建，升级保留配置待验证"},
    {"module": "公开文档", "progress": "55%", "owner": "文档", "status": "首页已重构，场景文档还需补图和 GIF"},
]

DELIVERY_RISKS = [
    {"risk": "跨团队联调窗口不足", "level": "高", "impact": "Hosted UI 与 Runtime API 可能无法按期验收", "mitigation": "冻结接口契约，安排每日联调检查点。"},
    {"risk": "镜像升级丢失用户配置", "level": "高", "impact": "客户升级后需要重新配置环境", "mitigation": "把配置目录挂载到持久卷，并补升级回归用例。"},
    {"risk": "文档演示材料不足", "level": "中", "impact": "开源用户难以理解最终效果", "mitigation": "补 Web UI 截图、CLI 截图和端到端 GIF。"},
]

DELIVERY_ACTIONS = [
    "把 Runtime API、Web UI、Sandbox 镜像和文档四条线拆成可验收清单。",
    "对高风险事项设置责任人、截止时间和阻塞升级路径。",
    "每天用固定问题跑一次本地 demo，记录接口返回、截图和日志。",
    "发布前执行 public-preflight、CI、真实 Web UI smoke 和公开安全扫描。",
]

ACCEPTANCE_CHECKS = [
    "所有 README 中的命令在公开 clone 后可运行或清楚说明降级行为。",
    "本地 agentengine run 能返回结构化 Markdown，而不是固定占位答案。",
    "镜像升级不会覆盖用户 workspace、memory 或运行时配置。",
    "发布说明区分已完成能力、实验能力和后续计划。",
]
