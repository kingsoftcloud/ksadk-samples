from __future__ import annotations

# 本地公开示例数据。真实项目可以把这里替换为知识库、Workspace 文件或业务 API。
SCENARIO_EVIDENCE = [{'id': 'runtime-platform',
  'title': 'Runtime Platform 价值',
  'content': '统一运行时让同一个 Agent 可以在本地调试、浏览器 UI、OpenAI-Compatible API 和云端部署之间迁移。'},
 {'id': 'sandbox',
  'title': 'Sandbox 和工具边界',
  'content': '生产 Agent 需要把代码执行、文件写入、Skill Runtime 等高风险能力放进明确边界，并提供审批语义。'},
 {'id': 'observability',
  'title': '可观测性',
  'content': 'OpenTelemetry-first 的 tracing 能让 LangGraph、ADK、工具调用和部署链路被统一观察。'},
 {'id': 'samples', 'title': '样例转化', 'content': '场景化 demo 比框架分类更容易让新用户理解为什么需要平台能力。'}]

# 演示行动项模板，tools.py 会根据检索到的证据生成最终计划。
ACTION_TEMPLATES = ['形成研究问题树', '收集证据卡片', '列出反例和风险', '输出可执行结论']
