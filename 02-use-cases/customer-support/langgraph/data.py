from __future__ import annotations

# 本地公开示例数据。真实项目可以把这里替换为知识库、Workspace 文件或业务 API。
SCENARIO_EVIDENCE = [{'id': 'webui', 'title': 'Web UI 无响应', 'content': '先确认 agentengine web 日志、端口、浏览器控制台和模型流式输出是否正常。'},
 {'id': 'skills',
  'title': 'Skill 未调用',
  'content': '检查 prompt 是否要求调用工具、toolset 是否绑定、Space ID 和服务凭证是否正确。'},
 {'id': 'markdown',
  'title': 'Markdown 渲染异常',
  'content': '默认保留模型原文；业务需要时可显式调用 repair_markdown(enabled=True)。'},
 {'id': 'deploy', 'title': '部署失败', 'content': '收集 region、运行时类型、镜像版本、环境变量和 public-preflight 输出。'}]

# 演示行动项模板，tools.py 会根据检索到的证据生成最终计划。
ACTION_TEMPLATES = ['识别问题类型', '匹配知识条目', '给出排障步骤', '判断是否升级工单']
