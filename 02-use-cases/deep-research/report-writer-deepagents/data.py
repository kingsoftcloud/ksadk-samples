from __future__ import annotations

# 本地模拟的研究材料。真实项目可以替换为搜索、知识库或 Workspace 文档。
REPORT_SOURCES = [
    {'id': 'source-runtime', 'title': '统一运行时', 'quote': '统一运行时能让 Agent 在本地调试、浏览器 UI、OpenAI-Compatible API 和云端部署之间复用同一套工程结构。', 'section': '平台价值', 'quality': '证据覆盖开发、调试和部署，但还需要补充线上运维数据。'},
    {'id': 'source-sandbox', 'title': '安全执行边界', 'quote': 'Workspace、Sandbox、Skill Runtime 应当分别承担文件上下文、隔离执行和可复用业务能力。', 'section': '运行边界', 'quality': '证据能说明边界划分，但真实项目还要验证权限和审计策略。'},
    {'id': 'source-observe', 'title': '可观测性', 'quote': 'OpenTelemetry-first 的 tracing 可以把模型调用、工具调用和部署链路放进同一条观察路径。', 'section': '可观测性', 'quality': '证据适合写入方案，但需要接入真实 trace 截图增强说服力。'},
    {'id': 'source-samples', 'title': '样例运营', 'quote': '场景化 demo、真实 Web UI GIF 和可运行脚本比框架分类更容易提升新用户转化。', 'section': '开发者体验', 'quality': '证据适合公开 README，但后续要继续补行业案例。'},
]

# 报告大纲固定为可解释的四段。
REPORT_OUTLINE = ['摘要', '关键发现', '风险和限制', '落地建议']
