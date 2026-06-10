from __future__ import annotations

# 模拟浏览器观察结果。真实项目可以把这些条目替换为 Playwright、Browser Use 或 hosted UI 的 DOM 快照。
PAGE_OBSERVATIONS = [
    {'selector': 'textarea[placeholder*="发送消息"]', 'role': '输入框', 'state': '可输入', 'finding': '消息输入框存在，placeholder 指向发送消息。'},
    {'selector': 'button[title="发送消息"]', 'role': '发送按钮', 'state': 'disabled', 'finding': '发送按钮在输入为空时禁用，填入文本后应变为可点击。'},
    {'selector': 'button:has-text("Workspace")', 'role': '工作区入口', 'state': '可点击', 'finding': 'Workspace 入口可见，说明 Web UI bootstrap 已加载。'},
    {'selector': 'aside [data-session-list]', 'role': '会话列表', 'state': '可见', 'finding': '历史会话区域可见，可用于判断 session backend 是否正常。'},
]

DIAGNOSTIC_RULES = [
    '先确认页面是否完成 bootstrap，再看输入框和发送按钮状态。',
    '按钮 disabled 时先检查输入框内容、模型选择、前端校验和会话创建接口。',
    '如果 DOM 存在但点击无响应，再看浏览器控制台和后端 /agentengine/api/v1 日志。',
]

VERIFY_STEPS = [
    '打开 agentengine web 页面并等待 networkidle。',
    '定位 textarea，填入一条问题。',
    '确认发送按钮从 disabled 变为 enabled。',
    '点击发送并等待回答中出现预期章节。',
]
