from __future__ import annotations

# 本地公开示例数据。真实项目可以把这里替换为知识库、Workspace 文件或业务 API。
SCENARIO_EVIDENCE = [{'id': 'planner', 'title': 'Planner', 'content': '负责拆任务、设定验收标准和维护执行顺序。'},
 {'id': 'researcher', 'title': 'Researcher', 'content': '负责参考竞品样例、提炼场景和发现差距。'},
 {'id': 'builder', 'title': 'Builder', 'content': '负责实现多文件 Agent 工程、README 和 smoke 脚本。'},
 {'id': 'reviewer', 'title': 'Reviewer', 'content': '负责检查事实、门禁、敏感信息和演示效果。'}]

# 演示行动项模板，tools.py 会根据检索到的证据生成最终计划。
ACTION_TEMPLATES = ['分配角色', '并行收集产物', '整合冲突', '输出验收清单']
