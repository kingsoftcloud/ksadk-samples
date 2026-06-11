DEMAND_FORECAST = {
    "product": "示例智能终端套件",
    "horizon": "未来 4 周",
    "baseline": "预计需求 12,400 套，环比提升 16%",
    "driver": "华东促销和渠道补库带来额外需求，华南预测偏差扩大。",
}

INVENTORY_RISKS = [
    {"risk": "华东安全库存不足", "level": "高", "impact": "第 3 周可能出现 1,200 套缺口。"},
    {"risk": "华南预测偏差扩大", "level": "中", "impact": "若促销不达预期，将形成慢周转库存。"},
    {"risk": "核心部件在途延迟", "level": "中", "impact": "补货计划需要预留替代供应商窗口。"},
]

TRANSFER_PLAN = [
    "从华北仓向华东仓调拨 800 套，并优先覆盖已确认订单。",
    "把华南补货批次拆成两段，第一段按保守预测执行，第二段等待促销数据确认。",
    "要求供应商每日更新核心部件 ETA，延迟超过 24 小时触发替代采购评估。",
    "建立未来四周滚动预测，每周复盘预测偏差和履约损失。",
]

MONITORING_METRICS = [
    {"metric": "华东可售天数", "threshold": ">= 10 天", "owner": "区域计划"},
    {"metric": "华南预测偏差", "threshold": "<= 12%", "owner": "需求计划"},
    {"metric": "核心部件 ETA 偏差", "threshold": "<= 24 小时", "owner": "采购"},
    {"metric": "缺货订单金额", "threshold": "每日下降", "owner": "履约运营"},
]
