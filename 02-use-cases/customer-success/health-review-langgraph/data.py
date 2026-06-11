CUSTOMER_HEALTH = {
    "customer": "示例云协作团队",
    "health_score": 68,
    "stage": "续费前 45 天",
    "usage": "近 14 天活跃席位下降 12%，核心自动化流程仍保持稳定运行",
    "value": "已节省例行巡检时间，但新团队尚未完成高级能力培训",
}

RISK_SIGNALS = [
    {"signal": "管理员近两周未登录", "level": "高", "reason": "续费窗口临近，关键人参与度下降。"},
    {"signal": "高级工具配置失败率 18%", "level": "中", "reason": "新团队复制配置时缺少环境变量说明。"},
    {"signal": "支持工单集中在权限和 Web UI 调试", "level": "中", "reason": "使用扩展阶段需要更清晰的最佳实践。"},
]

SUCCESS_ACTIONS = [
    "安排一次 45 分钟健康复盘，先展示已节省工时和当前风险。",
    "为管理员提供 Skill Runtime、Workspace、Sandbox 和 Memory 的配置检查清单。",
    "给新团队补一场基于真实工作流的训练，并用公开样例复现关键路径。",
    "把续费前关键指标改成每周追踪，异常时自动生成行动建议。",
]

FOLLOW_UPS = [
    {"cadence": "本周", "owner": "客户成功经理", "checkpoint": "完成健康复盘并确认关键人。"},
    {"cadence": "下周", "owner": "解决方案工程师", "checkpoint": "完成配置诊断和新团队培训。"},
    {"cadence": "续费前 14 天", "owner": "客户负责人", "checkpoint": "复查活跃席位、工单关闭率和价值证明材料。"},
]
