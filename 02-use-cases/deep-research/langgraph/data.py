from __future__ import annotations

# 本地公开示例数据。真实项目可以把这里替换为知识库、Workspace 文件或业务 API。
# 字段故意比普通 RAG 多一些，用来模拟 DeerFlow / ADK deep-search 这类 Agent 的计划、检索、反思和综合阶段。
SCENARIO_EVIDENCE = [
    {
        'id': 'runtime-platform',
        'title': 'Runtime Platform 价值',
        'content': '统一运行时让同一个 Agent 可以在本地调试、浏览器 UI、OpenAI-Compatible API 和云端部署之间迁移。',
        'angle': '平台定位',
        'gap': '需要补充部署和调试链路的证据。',
    },
    {
        'id': 'sandbox',
        'title': 'Sandbox 和工具边界',
        'content': '生产 Agent 需要把代码执行、文件写入、Skill Runtime 等高风险能力放进明确边界，并提供审批语义。',
        'angle': '安全执行',
        'gap': '需要确认工具调用是否有最小权限和审计记录。',
    },
    {
        'id': 'observability',
        'title': '可观测性',
        'content': 'OpenTelemetry-first 的 tracing 能让 LangGraph、ADK、工具调用和部署链路被统一观察。',
        'angle': '运行观测',
        'gap': '需要补充 trace、日志、指标的统一配置说明。',
    },
    {
        'id': 'samples',
        'title': '样例转化',
        'content': '场景化 demo 比框架分类更容易让新用户理解为什么需要平台能力。',
        'angle': '开发者增长',
        'gap': '需要真实截图、GIF 和一键运行脚本降低试用成本。',
    },
]

# 演示行动项模板，tools.py 会根据检索到的证据生成最终计划。
ACTION_TEMPLATES = ['拆解研究问题树', '检索证据并记录来源', '反思证据缺口并补查', '综合成可交付报告']

# 这些阶段名会出现在最终 Markdown 里，让 Web UI 演示时能看到 Agent 的执行脉络。
RESEARCH_STAGES = [
    'Plan：把开放问题拆成可验证子问题',
    'Search：围绕每个角度收集证据卡片',
    'Reflect：检查证据缺口和反例',
    'Synthesize：形成结论、风险和交付物',
]
