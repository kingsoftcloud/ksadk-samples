CHANGE_SUMMARY = {
    "change": "Hosted Web UI 文件上传与工具调用链路（示例）",
    "scope": "浏览器上传、workspace 写入、工具读取和响应展示",
    "assets": "用户文件、运行日志、会话元数据和临时产物",
    "exposure": "本地 demo 使用公开 fixture，真实环境需经过权限和数据安全审计",
}

THREATS = [
    {"threat": "越权读取 workspace 文件", "severity": "高", "impact": "不同会话或租户之间的数据隔离被破坏", "control": "校验 session_id、principal_id 和 workspace 根目录边界。"},
    {"threat": "上传文件类型绕过", "severity": "中", "impact": "恶意文件进入工具执行链路", "control": "限制 MIME、扩展名、大小，并在工具执行前二次校验。"},
    {"threat": "工具输出泄露敏感日志", "severity": "中", "impact": "内部路径、环境变量或 token 被展示给用户", "control": "对日志、环境变量和错误栈做脱敏过滤。"},
]

REMEDIATION_PLAN = [
    "为 workspace 读写增加租户、会话和路径边界测试。",
    "上传入口启用文件大小、类型和内容扫描策略。",
    "工具执行前后统一经过敏感信息脱敏过滤器。",
    "发布前保存 health、chat、上传和取消链路的审计证据。",
]

EVIDENCE_ITEMS = [
    {"evidence": "权限边界测试", "status": "待补", "owner": "平台后端"},
    {"evidence": "上传策略配置", "status": "待确认", "owner": "Web UI"},
    {"evidence": "脱敏扫描报告", "status": "待补", "owner": "安全"},
    {"evidence": "发布前 smoke 日志", "status": "已规划", "owner": "质量"},
]
