from __future__ import annotations

# 本地公开示例数据。真实项目可以把这里替换为知识库、Workspace 文件或业务 API。
SCENARIO_EVIDENCE = [{'id': 'observe', 'title': '观察页面', 'content': '先记录 URL、标题、关键区域和控制台错误，再决定是否点击或输入。'},
 {'id': 'act', 'title': '安全操作', 'content': '浏览器 Agent 只执行可解释步骤，高风险提交必须让用户确认。'},
 {'id': 'screenshot', 'title': '视觉证据', 'content': '重要节点保存截图或 DOM 摘要，方便复盘 UI 问题。'},
 {'id': 'fallback', 'title': '失败降级', 'content': '页面不可达时输出诊断：端口、路由、服务日志和网络状态。'}]

# 演示行动项模板，tools.py 会根据检索到的证据生成最终计划。
ACTION_TEMPLATES = ['规划导航路径', '定义观察点', '生成操作步骤', '输出验证报告']
