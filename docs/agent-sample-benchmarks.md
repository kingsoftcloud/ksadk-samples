# Agent 样例对标笔记

这个文档记录 KSADK Samples 后续补齐场景 Agent 时的参考原则。它不是竞品宣传页，而是给维护者看的样例设计清单：新增 demo 前先看这些维度，避免样例退化成单文件脚本或不可运行的概念代码。

## 参考对象

| 项目 | 值得学习的点 | 在 KSADK Samples 中的落点 |
| --- | --- | --- |
| Google ADK Samples | 场景很多，README 会写清 Agent Details、架构图、运行、部署、测试和自定义方式。 | 每个样例必须有中文优先 README、运行命令、Web UI 调试、部署和常见问题。 |
| ADK Deep Search | 研究类 Agent 强调计划、人类确认、迭代检索、反思和最终报告。 | `deep-research/langgraph` 输出研究计划、执行轨迹、反思补查和交付物；`deep-research/report-writer-*` 对比 LangGraph / ADK / LangChain / DeepAgents 的报告生成写法。 |
| ADK SWE Benchmark / Software Bug Assistant | Coding Agent 强调定位、工具、隔离执行、测试和评审风险。 | `coding-agent/langgraph` 输出变更定位、测试矩阵、发布风险和交付物；`coding-agent/workspace-sandbox-*` 对比多框架 Workspace / Sandbox 边界。 |
| Browser-use / Playwright Agent 经验 | 浏览器 Agent 需要把页面观察、DOM 线索、失败诊断和可复现验证步骤拆开，避免只输出“请刷新”。 | `browser-agent/dom-diagnostics-*` 已补 LangGraph / ADK / LangChain / DeepAgents 的 DOM 诊断基础版本；下一步接真实 Playwright snapshot、截图和 Web UI 日志。 |
| 数据分析 Agent / BI Copilot 经验 | 数据 Agent 要先说明数据样本、指标口径和可视化建议，再谈洞察结论。 | `data-analyst/csv-insight-*` 已补 LangGraph / ADK / LangChain / DeepAgents 的 CSV 洞察基础版本；下一步接 Workspace CSV、DuckDB 查询和图表 artifact。 |
| 客服与工单 Copilot 经验 | 客服 Agent 要把客户现象、知识匹配、排障步骤和升级策略拆清楚，避免只给安慰性回复。 | `customer-support/ticket-triage-*` 已补 LangGraph / ADK / LangChain / DeepAgents 的工单分级基础版本；下一步接真实知识库和工单系统。 |
| Multi-Agent / Super Agent Harness 经验 | 多 Agent 样例要展示角色分工、并行轨迹、冲突合并和验收清单，而不是只列几个角色名。 | `multi-agent-team/team-delivery-*` 已补 LangGraph / ADK / LangChain / DeepAgents 的协作交付基础版本；下一步接真实子 Agent 和任务队列。 |
| AIOps / Incident Copilot 经验 | 运维 Agent 要把指标、日志、Tracing 和变更事件放进同一条 incident timeline，并输出可执行 runbook。 | `aiops/incident-triage-*` 已补 LangGraph / ADK / LangChain / DeepAgents 的告警分诊基础版本；下一步接真实 Prometheus、日志平台和 Tracing。 |
| 财务分析 / 审计预审 Copilot 经验 | 财务 Agent 要先展示报表摘录和口径，再给风险指标、异常解释和审阅动作，不能伪造审计意见。 | `finance/report-review-*` 已补 LangGraph / ADK / LangChain / DeepAgents 的报表审阅基础版本；下一步接 Workspace Excel、财务系统 API 和图表 artifact。 |
| 内容生产 / Campaign Copilot 经验 | 内容生产 Agent 要先对齐目标、受众、渠道和审核约束，再生成草稿，不能只输出泛泛文案。 | `content-production/campaign-planner-*` 已补 LangGraph / ADK / LangChain / DeepAgents 的传播计划基础版本；下一步接 CMS、社媒排期和品牌审核。 |
| 企业知识运营 / Knowledge Ops 经验 | 知识运营 Agent 要把用户反馈、现有文档、缺口和发布校验串起来，避免只做摘要。 | `knowledge-operations/knowledge-curator-*` 已补 LangGraph / ADK / LangChain / DeepAgents 的知识库更新计划版本；下一步接真实知识库、工单和文档 CI。 |
| 销售运营 / Pipeline Copilot 经验 | 销售 Agent 要把线索画像、阶段、跟进动作和风险拆开，避免只输出销售话术。 | `sales-operations/pipeline-copilot-*` 已补 LangGraph / ADK / LangChain / DeepAgents 的 pipeline 跟进计划版本；下一步接真实 CRM、任务系统和销售周报。 |
| 合规审阅 / Policy Review Copilot 经验 | 合规 Agent 要可追溯地列出材料、规则、整改建议和审阅记录，不能替代法务结论。 | `compliance-review/policy-review-*` 已补 LangGraph / ADK / LangChain / DeepAgents 的对外材料审阅版本；下一步接 Workspace 文档、法务规则库和审批流。 |
| 采购协同 / Vendor Selection Copilot 经验 | 采购 Agent 要把需求、供应商、谈判项和审批风险拆开，避免只做价格排序。 | `procurement-collaboration/vendor-selection-*` 已补 LangGraph / ADK / LangChain / DeepAgents 的供应商筛选版本；下一步接真实采购系统、供应商库和审批流。 |
| HR 招聘 / Interview Planner 经验 | 招聘 Agent 要把岗位画像、候选人匹配、面试轮次和录用风险拆开，不能泄露真实个人信息。 | `hr-recruiting/interview-planner-*` 已补 LangGraph / ADK / LangChain / DeepAgents 的面试计划版本；下一步接 ATS、日历和面试评价模板。 |
| 项目管理 / Delivery Planner 经验 | 项目管理 Agent 要把项目状态、风险、推进动作和验收标准拆开，避免只输出周报摘要。 | `project-management/delivery-planner-*` 已补 LangGraph / ADK / LangChain / DeepAgents 的交付计划版本；下一步接真实项目管理系统、风险登记表和发布审批流。 |
| 法务合同 / Contract Negotiation Copilot 经验 | 合同 Agent 要把合同背景、关键条款、谈判建议和法务风险拆开，不能替代正式法律意见。 | `legal-contract/contract-negotiation-*` 已补 LangGraph / ADK / LangChain / DeepAgents 的合同谈判审阅版本；下一步接合同管理系统、法务规则库和审批流。 |
| 研发效能 / Engineering Efficiency 经验 | 研发效能 Agent 要把迭代概览、瓶颈、改进动作和度量指标串起来，避免只给管理口号。 | `dev-productivity/engineering-efficiency-*` 已补 LangGraph / ADK / LangChain / DeepAgents 的效能改进版本；下一步接 Git、CI、Issue、评审和发布流水线。 |
| 产品运营 / Experiment Review 经验 | 产品运营 Agent 要把实验结果、用户分群、运营动作和复盘指标拆开，避免只追单一转化率。 | `product-operations/experiment-review-*` 已补 LangGraph / ADK / LangChain / DeepAgents 的实验复盘版本；下一步接真实埋点、实验平台和运营触达系统。 |
| 数据治理 / Quality Audit 经验 | 数据治理 Agent 要把资产、质量问题、治理动作和责任矩阵串起来，避免只输出抽象治理建议。 | `data-governance/quality-audit-*` 已补 LangGraph / ADK / LangChain / DeepAgents 的质量审计版本；下一步接数据目录、质量规则、血缘和整改工单。 |
| 安全审计 / Threat Review 经验 | 安全审计 Agent 要把变更摘要、威胁、整改和验证证据拆开，避免泄露真实漏洞或生产细节。 | `security-audit/threat-review-*` 已补 LangGraph / ADK / LangChain / DeepAgents 的威胁评审版本；下一步接 SAST、DAST、权限审计和发布审批流。 |
| 客户成功 / Health Review Copilot 经验 | 客户成功 Agent 要把客户健康、风险信号、成功计划和跟进节奏拆开，避免只做续费话术。 | `customer-success/health-review-*` 已补 LangGraph / ADK / LangChain / DeepAgents 的健康复盘版本；下一步接真实 CRM、产品埋点、续费系统和客户旅程平台。 |
| 教育培训 / Learning Coach 经验 | 学习辅导 Agent 要把学习画像、能力缺口、训练计划和评估方式串起来，不能泄露真实学员数据。 | `education-training/learning-coach-*` 已补 LangGraph / ADK / LangChain / DeepAgents 的学习辅导版本；下一步接 LMS、练习平台、测评系统和学习档案。 |
| 供应链计划 / Demand Planner 经验 | 供应链 Agent 要把需求预测、库存风险、调拨计划和监控指标拆开，避免只输出库存口号。 | `supply-chain-planning/demand-planner-*` 已补 LangGraph / ADK / LangChain / DeepAgents 的需求计划版本；下一步接 ERP、WMS、OMS、渠道预测和供应商协同系统。 |
| 长任务 Agent / Super Agent Harness 经验 | 长任务需要可恢复 checkpoint、取消语义、tool receipt 去重和用户可观察状态，不能只依赖进程内存。 | `long-task-resume/{langgraph,adk,langchain,deepagents}` 已补四种框架工程版本，默认用 fixture 演示 checkpoint 列表、ResumeRun、CancelRun 和 receipt 去重；下一步接真实 session backend。 |
| 医疗运营 / Care Coordination 经验 | 医疗运营 Agent 要把患者流转、资源瓶颈、协同计划和风险提醒拆开，不能处理真实诊断或隐私数据。 | `healthcare-operations/care-coordinator-*` 已补 LangGraph / ADK / LangChain / DeepAgents 的护理协同版本；下一步接预约、排队、护理工作站和运营看板的脱敏统计数据。 |
| 能源调度 / Load Balancer 经验 | 能源调度 Agent 要把负荷预测、设备状态、调度策略和安全边界拆开，不能直接下发真实控制指令。 | `energy-dispatch/load-balancer-*` 已补 LangGraph / ADK / LangChain / DeepAgents 的负荷平衡版本；下一步接 EMS、计量平台、天气服务和需求响应系统。 |
| 政务服务 / Case Assistant 经验 | 政务服务 Agent 要把事项画像、材料核验、协同流程和服务承诺拆开，审批结论必须人工复核。 | `public-service/case-assistant-*` 已补 LangGraph / ADK / LangChain / DeepAgents 的事项协同版本；下一步接政务服务平台、材料库和办件流转系统。 |
| 保险理赔 / Claim Review 经验 | 理赔 Agent 要把案件摘要、材料核验、审核建议和风险控制拆开，不能自动给出赔付结论或泄露真实保单信息。 | `insurance-claims/claim-review-*` 已补 LangGraph / ADK / LangChain / DeepAgents 的理赔审核协同版本；下一步接理赔系统、影像件库、定损系统和人工审核工作台。 |
| 制造质量 / Defect Analysis 经验 | 制造质量 Agent 要把质量概览、缺陷归因、改进措施和验证指标串起来，避免泄露真实工艺参数或客户产品信息。 | `manufacturing-quality/defect-analysis-*` 已补 LangGraph / ADK / LangChain / DeepAgents 的缺陷分析版本；下一步接 MES、QMS、设备点检和质量看板。 |
| 零售运营 / Store Optimization 经验 | 零售 Agent 要同时看门店表现、库存结构、运营动作和复盘指标，不能只追销售额或暴露真实会员数据。 | `retail-operations/store-optimizer-*` 已补 LangGraph / ADK / LangChain / DeepAgents 的门店优化版本；下一步接 POS、WMS、商品主数据、促销和会员分析。 |
| 物流履约 / Delivery Exception 经验 | 物流履约 Agent 要把异常订单、配送资源、客户承诺和复盘指标拆开，不能泄露真实地址、订单或司机信息。 | `logistics-fulfillment/delivery-exception-*` 已补 LangGraph / ADK / LangChain / DeepAgents 的履约异常版本；下一步接 OMS、TMS、WMS、客服系统和地图服务。 |
| 房地产运营 / Asset Service 经验 | 房地产运营 Agent 要把资产状态、租户服务、工单协同和收益风险串起来，不能泄露真实租户、合同或财务数据。 | `real-estate-operations/asset-service-*` 已补 LangGraph / ADK / LangChain / DeepAgents 的资产服务版本；下一步接资产台账、工单系统、合同系统和财务看板。 |
| 农业生产 / Crop Planner 经验 | 农业生产 Agent 要把种植计划、环境数据、农事任务和产量预测拆开，农业处方必须保留人工农技师确认。 | `agriculture-production/crop-planner-*` 已补 LangGraph / ADK / LangChain / DeepAgents 的农事计划版本；下一步接农事计划、IoT、天气服务和采收台账。 |
| 通信运维 / Network Change 经验 | 通信运维 Agent 要把网络告警、容量分析、割接计划和客户影响拆开，不能泄露真实拓扑、基站、专线客户或生产告警。 | `telecom-operations/network-change-*` 已补 LangGraph / ADK / LangChain / DeepAgents 的网络割接版本；下一步接 NMS、告警平台、CMDB、容量分析和割接审批系统。 |
| 旅游服务 / Trip Recovery 经验 | 旅游服务 Agent 要把行程变更、资源协调、客户通知和服务补偿拆开，不能泄露真实旅客、订单、证件或供应商结算数据。 | `travel-service/trip-recovery-*` 已补 LangGraph / ADK / LangChain / DeepAgents 的行程恢复版本；下一步接订单系统、航旅动态、酒店库存、车辆调度和通知平台。 |
| 设备维护 / Maintenance Planner 经验 | 设备维护 Agent 要把设备状态、备件计划、维修任务和停机风险拆开，不能泄露真实设备序列号、工艺参数或生产数据。 | `equipment-maintenance/maintenance-planner-*` 已补 LangGraph / ADK / LangChain / DeepAgents 的维修计划版本；下一步接 EAM、CMMS、点检系统、传感器平台和备件库存。 |
| 媒体运营 / Content Distribution 经验 | 媒体运营 Agent 要把内容排期、热点监测、版权风险和多渠道发布拆开，不能泄露真实账号、作者、版权合同或平台后台数据。 | `media-operations/content-distribution-*` 已补 LangGraph / ADK / LangChain / DeepAgents 的内容分发版本；下一步接 CMS、热点监测、版权库、审核流、社媒排期和数据看板。 |
| 金融风控 / Risk Alert 经验 | 金融风控 Agent 要把交易异常、风险规则、人工复核和审计留痕拆开，不能泄露真实账户、交易、客户、卡号、证件号或内部规则阈值。 | `financial-risk/risk-alert-*` 已补 LangGraph / ADK / LangChain / DeepAgents 的风险预警版本；下一步接交易风控、规则引擎、设备指纹、人工复核台和审计系统。 |
| 城市交通 / Traffic Response 经验 | 城市交通 Agent 要把道路拥堵、运力调度、事件响应和公众通知拆开，不能泄露真实车牌、乘客、摄像头画面或生产调度数据。 | `urban-mobility/traffic-response-*` 已补 LangGraph / ADK / LangChain / DeepAgents 的交通响应版本；下一步接交通事件平台、公交调度、路况监测、停车诱导和公众通知平台。 |
| 地产营销 / Lead Conversion 经验 | 地产营销 Agent 要把楼盘线索、渠道投放、内容审核和转化复盘拆开，不能泄露真实客户、手机号、成交价格或渠道后台数据。 | `real-estate-marketing/lead-conversion-*` 已补 LangGraph / ADK / LangChain / DeepAgents 的线索转化版本；下一步接 CRM、广告投放平台、案场系统、内容审核流和成交复盘看板。 |
| 公共安全 / Incident Coordination 经验 | 公共安全 Agent 要把事件线索、资源联动、风险通报和处置复盘拆开，不能泄露真实报警人、地址、执法记录或监控画面。 | `public-safety/incident-coordination-*` 已补 LangGraph / ADK / LangChain / DeepAgents 的事件联动版本；下一步接事件平台、热线系统、现场巡查、交通协同、医疗联动和公众通知平台。 |
| 工业巡检 / Safety Patrol 经验 | 工业巡检 Agent 要把巡检任务、缺陷识别、维修联动和安全复核拆开，不能泄露真实设备序列号、车间位置、工艺参数或事故记录。 | `industrial-inspection/safety-patrol-*` 已补 LangGraph / ADK / LangChain / DeepAgents 的安全巡检版本；下一步接点检系统、EAM、CMMS、传感器平台、备件库存和安全作业票系统。 |
| 环境监测 / Pollution Response 经验 | 环境监测 Agent 要把监测点位、污染线索、处置联动和公众披露拆开，不能泄露真实企业排污数据、坐标、执法记录或敏感事件。 | `environmental-monitoring/pollution-response-*` 已补 LangGraph / ADK / LangChain / DeepAgents 的污染响应版本；下一步接监测点位平台、IoT 传感器、环保工单、巡查记录、气象服务和公众披露平台。 |
| 餐饮运营 / Store Ops 经验 | 餐饮运营 Agent 要把门店排班、食安巡检、库存损耗和顾客反馈拆开，不能泄露真实会员、员工、流水、供应商价格或监管记录。 | `restaurant-operations/store-ops-*` 已补 LangGraph / ADK / LangChain / DeepAgents 的门店协同版本；下一步接 POS、排班系统、食安巡检、库存系统、外卖平台和顾客反馈看板。 |
| 游戏运营 / LiveOps Review 经验 | 游戏运营 Agent 要把玩家反馈、活动配置、经济系统监控和版本复盘拆开，不能泄露真实玩家 ID、充值记录、反作弊规则或未公开版本计划。 | `game-operations/liveops-review-*` 已补 LangGraph / ADK / LangChain / DeepAgents 的版本复盘版本；下一步接玩家反馈平台、活动配置、数据看板、经济系统监控、公告系统和版本管理。 |
| 广告投放 / Campaign Optimization 经验 | 广告投放 Agent 要把投放目标、素材审核、预算节奏和效果复盘拆开，不能泄露真实账户、转化明细、用户画像或广告后台数据。 | `advertising-operations/campaign-optimization-*` 已补 LangGraph / ADK / LangChain / DeepAgents 的投放优化版本；下一步接广告平台、素材库、落地页分析、转化归因、品牌审核和预算看板。 |
| 社群运营 / Community Growth 经验 | 社群运营 Agent 要把社群画像、内容日历、互动风险和转化复盘拆开，不能泄露真实群成员、聊天记录、手机号或私域标签。 | `community-operations/community-growth-*` 已补 LangGraph / ADK / LangChain / DeepAgents 的社群增长版本；下一步接社群平台、内容日历、知识库、活动报名、CRM 线索池和运营看板。 |
| 客服质检 / Service Quality 经验 | 客服质检 Agent 要把质检样本、规则命中、改进建议和培训闭环拆开，不能泄露真实通话录音、客户身份、坐席工号或投诉详情。 | `customer-qa/service-quality-*` 已补 LangGraph / ADK / LangChain / DeepAgents 的服务质检版本；下一步接客服工单、质检规则库、知识库、培训系统、坐席反馈和质量看板。 |
| 门店客服 / Store Service 经验 | 门店客服 Agent 要把门店咨询、服务承诺、问题升级和体验复盘拆开，不能泄露真实顾客、订单、会员、监控或赔付记录。 | `store-service/store-advisor-*` 已补 LangGraph / ADK / LangChain / DeepAgents 的门店服务版本；下一步接门店 POS、会员服务台、客服工单、知识库、排班系统和体验回访看板。 |
| 售后服务 / After-sales Service 经验 | 售后 Agent 要把售后工单、备件协同、服务时效和客户回访拆开，不能泄露真实客户、地址、订单、保修凭证或维修录音。 | `after-sales-service/repair-coordinator-*` 已补 LangGraph / ADK / LangChain / DeepAgents 的售后协同版本；下一步接售后工单系统、备件库存、工程师排班、物流查询和客服回访。 |
| 内容安全 / Content Safety 经验 | 内容安全 Agent 要把内容样本、规则命中、人工复核和风险处置拆开，不能泄露真实用户、原文、截图、敏感词库或风控阈值。 | `content-safety/moderation-review-*` 已补 LangGraph / ADK / LangChain / DeepAgents 的内容审核版本；下一步接审核平台、举报系统、规则引擎、人工复核台和样本回灌管道。 |
| 直播运营 / Live Commerce Operations 经验 | 直播运营 Agent 要把直播场控、商品讲解、异常舆情和转化复盘拆开，不能泄露真实观众、订单、直播间后台或未公开价格策略。 | `live-commerce-operations/session-control-*` 已补 LangGraph / ADK / LangChain / DeepAgents 的直播场控版本；下一步接直播中控台、商品池、库存系统、客服工单、舆情看板和转化分析。 |
| 会员增长 / Membership Growth 经验 | 会员增长 Agent 要把会员分层、权益推荐、触达节奏和留存复盘拆开，不能泄露真实会员、手机号、订单、支付记录或画像明细。 | `membership-growth/member-lifecycle-*` 已补 LangGraph / ADK / LangChain / DeepAgents 的会员生命周期版本；下一步接 CRM、会员中心、权益平台、营销触达系统和客服反馈。 |
| 搜索推荐 / Search Recommendation 经验 | 搜索推荐 Agent 要把查询意图、召回质量、排序诊断和反馈闭环拆开，不能泄露真实 query、点击日志、排序权重或反作弊逻辑。 | `search-recommendation/relevance-diagnostics-*` 已补 LangGraph / ADK / LangChain / DeepAgents 的相关性诊断版本；下一步接搜索日志、召回服务、排序服务、标注平台、AB 实验和指标看板。 |
| 支付风控 / Payment Risk 经验 | 支付风控 Agent 要把支付异常、风控规则、人工复核和审计留痕拆开，不能泄露真实账户、交易号、设备指纹或真实规则阈值。 | `payment-risk/payment-guard-*` 已补 LangGraph / ADK / LangChain / DeepAgents 的支付风控版本；下一步接支付网关、风控规则引擎、设备指纹、退款系统、人工复核台和审计日志平台。 |
| 智能导购 / Shopping Assistant 经验 | 导购 Agent 要把需求澄清、商品对比、库存价格和导购转化拆开，不能泄露真实用户、订单、地址、支付记录或未公开促销策略。 | `shopping-assistant/product-advisor-*` 已补 LangGraph / ADK / LangChain / DeepAgents 的智能导购版本；下一步接商品主数据、库存价格系统、活动权益平台、客服知识库和导购会话。 |
| DevRel 运营 / DevRel Operations 经验 | DevRel Agent 要把开发者反馈、内容运营、活动节奏和社区复盘拆开，不能泄露真实开发者、企业信息、私聊内容或未公开路线图。 | `devrel-operations/community-program-*` 已补 LangGraph / ADK / LangChain / DeepAgents 的开发者运营版本；下一步接 GitHub Issues、Discussions、社群反馈、文档访问分析和贡献者看板。 |
| 品牌舆情 / Brand Reputation 经验 | 品牌舆情 Agent 要把舆情线索、传播路径、回应策略和品牌复盘拆开，不能泄露真实用户、社媒账号、私信内容或未公开声明。 | `brand-reputation/reputation-response-*` 已补 LangGraph / ADK / LangChain / DeepAgents 的品牌舆情版本；下一步接舆情监测平台、客服工单、社媒排期、品牌素材库、法务审核和公关复盘看板。 |
| 渠道运营 / Channel Operations 经验 | 渠道运营 Agent 要把渠道表现、库存协同、价格治理和经营复盘拆开，不能泄露真实经销商、合同价格、结算明细或返点规则。 | `channel-operations/channel-health-*` 已补 LangGraph / ADK / LangChain / DeepAgents 的渠道运营版本；下一步接渠道销售系统、库存系统、价格治理平台、经销商协同、促销系统和经营看板。 |
| 企业培训 / Enterprise Training 经验 | 企业培训 Agent 要把培训对象、课程设计、练习评估和学习复盘拆开，不能泄露真实员工、绩效、考试成绩或个人评价。 | `enterprise-training/training-planner-*` 已补 LangGraph / ADK / LangChain / DeepAgents 的企业培训版本；下一步接 LMS、HR 系统、课程库、考试平台、练习环境和学习数据看板。 |
| 合同履约 / Contract Fulfillment 经验 | 合同履约 Agent 要把履约节点、风险预警、协同动作和验收复盘拆开，不能泄露真实合同、客户名称、金额或商务条款。 | `contract-fulfillment/fulfillment-monitor-*` 已补 LangGraph / ADK / LangChain / DeepAgents 的合同履约版本；下一步接合同管理系统、项目管理系统、交付工单、验收材料库、客户确认记录和财务回款看板。 |
| 招投标协同 / Tender Collaboration 经验 | 招投标 Agent 要把招标需求、供应商响应、评分协同和风险复盘拆开，不能泄露真实供应商、报价、投标文件原文或评分细节。 | `tender-collaboration/bid-evaluator-*` 已补 LangGraph / ADK / LangChain / DeepAgents 的招投标协同版本；下一步接招标需求库、供应商响应文档、评分表、合规规则库、评审会议纪要和采购审批系统。 |
| 园区运营 / Campus Operations 经验 | 园区运营 Agent 要把园区工单、能耗资源、访客安全和运营复盘拆开，不能泄露真实租户、访客、车牌、门禁记录或监控画面。 | `campus-operations/campus-service-*` 已补 LangGraph / ADK / LangChain / DeepAgents 的园区运营版本；下一步接园区工单系统、能耗平台、访客系统、安防巡检、会议室预订和物业排班。 |
| 物业招商 / Property Leasing 经验 | 物业招商 Agent 要把招商线索、租赁方案、合同协同和转化复盘拆开，不能泄露真实租户、联系人、报价、底价或佣金规则。 | `property-leasing/leasing-copilot-*` 已补 LangGraph / ADK / LangChain / DeepAgents 的物业招商版本；下一步接招商 CRM、楼宇资源台账、租赁方案库、合同管理系统、带看日程和转化分析看板。 |
| 客服知识运营 / Support Knowledge Operations 经验 | 客服知识运营 Agent 要把知识缺口、工单反馈、内容更新和发布复盘拆开，不能泄露真实客户、工单原文、账号信息或坐席工号。 | `support-knowledge-operations/knowledge-feedback-*` 已补 LangGraph / ADK / LangChain / DeepAgents 的客服知识运营版本；下一步接客服工单系统、知识库、坐席反馈、搜索日志、内容审核流和发布看板。 |
| 活动会务运营 / Event Operations 经验 | 活动运营 Agent 要把活动报名、现场执行、资源调度和效果复盘拆开，不能泄露真实参会者、签到明细、嘉宾联系方式或活动预算。 | `event-operations/event-runbook-*` 已补 LangGraph / ADK / LangChain / DeepAgents 的活动会务运营版本；下一步接活动报名系统、签到系统、场地资源、物料清单、讲师日程、问卷反馈和转化看板。 |
| VEADK Examples | 从 quickstart 到 memory、knowledge、multi-agent、routing、tracing 逐层展开。 | 基础教程继续保持按能力矩阵覆盖 ADK / LangGraph / LangChain / DeepAgents。 |
| AgentKit Samples | 场景 demo 会拆出 tools、prompts、client、web、skills 等工程边界。 | 新 use case 默认多文件工程，核心逻辑不能塞进 `demo.py`。 |
| DeerFlow | 从 Deep Research 演进到 Super Agent Harness，重视文件系统、memory、skills、sandbox、sub-agents 和长任务可观察性。 | 样例要解释 Workspace、Memory、Skill Runtime、Sandbox 的接入位置和降级行为。 |
| SWE-agent / OpenHands / Aider 等 Coding Agent | 真实编码任务围绕仓库读写、shell 执行、补丁生成、测试和提交闭环。 | Coding Agent 后续应补 Workspace + Sandbox 版本，演示真实文件修改和测试输出。 |

## 新增样例验收线

- **能运行**：至少有一个离线 `demo.py` 或明确的 `agentengine run` 路径，clone 后不依赖私有账号也能看到主要输出。
- **像工程**：场景 Agent 默认拆成 `agent.py`、`workflow.py`、`tools.py`、`data.py`、`prompts.py`、`demo.py`，必要时再加 `client.py`、`web/`、`fixtures/`。
- **中文优先**：README 和关键注释默认中文，英文名称可以作为括号补充。
- **有执行轨迹**：输出里要能看到 Agent 做了哪些阶段，而不是只有最终答案。
- **可替换真实能力**：README 要说明本地 mock 如何替换为 LLM、Knowledge Base、Workspace、Sandbox、Skill Runtime 或 MCP。
- **可公开**：不得包含真实账号、token、私有 endpoint、客户数据或不能开源的业务流程。
- **有门禁**：新增 README 承诺的场景必须进入 `tests/test_sample_structure.py` 或 `scripts/validate_samples.py` 的校验范围。

## 推荐补齐顺序

1. **Deep Research Agent**：已补报告生成基础版本；下一步接真实 Web Search / Knowledge Base / Workspace 文档。
2. **Coding Agent**：已补 Workspace + Sandbox 规划版本；下一步接真实文件读写和测试运行结果。
3. **Browser Agent**：已补 DOM 观察和失败诊断基础版本；下一步补真实 Web UI 截图、Playwright snapshot 和日志关联。
4. **Data Analyst**：已补 CSV 洞察基础版本；下一步补 DuckDB 查询、Workspace CSV 和图表产物。
5. **Customer Support**：已补工单分级基础版本；下一步接真实知识库、工单状态和升级策略。
6. **Multi-Agent Team**：已补 planner / researcher / builder / reviewer 的协作交付基础版本；下一步接真实子图、子 Agent 或任务队列。
7. **AIOps**：已补告警分诊基础版本；下一步接真实监控、日志、Tracing 和变更系统。
8. **Finance**：已补报表审阅基础版本；下一步接 Workspace Excel、财务系统 API 和图表产物。
9. **Content Production**：已补传播计划基础版本；下一步接 CMS、社媒排期和品牌审核。
10. **Knowledge Operations**：已补知识库更新计划基础版本；下一步接真实知识库、工单反馈和文档 CI。
11. **Sales Operations**：已补 pipeline 跟进计划基础版本；下一步接真实 CRM、任务系统和销售周报。
12. **Compliance Review**：已补对外材料审阅基础版本；下一步接 Workspace 文档、法务规则库和审批流。
13. **Procurement Collaboration**：已补供应商筛选基础版本；下一步接真实采购系统、供应商库和审批流。
14. **HR Recruiting**：已补面试计划基础版本；下一步接 ATS、日历和面试评价模板。
15. **Project Management**：已补交付计划基础版本；下一步接真实项目管理系统、风险登记表和发布审批流。
16. **Legal Contract**：已补合同谈判审阅基础版本；下一步接合同管理系统、法务规则库和审批流。
17. **Dev Productivity**：已补研发效能改进基础版本；下一步接 Git、CI、Issue、评审和发布流水线。
18. **Product Operations**：已补实验复盘基础版本；下一步接真实埋点、实验平台和运营触达系统。
19. **Data Governance**：已补质量审计基础版本；下一步接数据目录、质量规则、血缘和整改工单。
20. **Security Audit**：已补威胁评审基础版本；下一步接 SAST、DAST、权限审计和发布审批流。
21. **Customer Success**：已补健康复盘基础版本；下一步接真实 CRM、产品埋点、续费系统和客户旅程平台。
22. **Education Training**：已补学习辅导基础版本；下一步接 LMS、练习平台、测评系统和学习档案。
23. **Supply Chain Planning**：已补需求计划基础版本；下一步接 ERP、WMS、OMS、渠道预测和供应商协同系统。
24. **Long Task Resume**：已补 LangGraph / ADK / LangChain / DeepAgents 工程版本；下一步接真实 Postgres session backend 和平台 run/session 事件。
25. **Healthcare Operations**：已补护理协同基础版本；下一步接预约、排队、护理工作站和运营看板的脱敏统计数据。
26. **Energy Dispatch**：已补负荷平衡基础版本；下一步接 EMS、计量平台、天气服务和需求响应系统。
27. **Public Service**：已补事项协同基础版本；下一步接政务服务平台、材料库和办件流转系统。
28. **Insurance Claims**：已补理赔审核协同基础版本；下一步接理赔系统、影像件库、定损系统和人工审核工作台。
29. **Manufacturing Quality**：已补缺陷分析基础版本；下一步接 MES、QMS、设备点检和质量看板。
30. **Retail Operations**：已补门店优化基础版本；下一步接 POS、WMS、商品主数据、促销和会员分析。
31. **Logistics Fulfillment**：已补履约异常基础版本；下一步接 OMS、TMS、WMS、客服系统和地图服务。
32. **Real Estate Operations**：已补资产服务基础版本；下一步接资产台账、工单系统、合同系统和财务看板。
33. **Agriculture Production**：已补农事计划基础版本；下一步接农事计划、IoT、天气服务和采收台账。
34. **Telecom Operations**：已补网络割接基础版本；下一步接 NMS、告警平台、CMDB、容量分析、客服工单和割接审批系统。
35. **Travel Service**：已补行程恢复基础版本；下一步接订单系统、航旅动态、酒店库存、车辆调度、客服工单和通知平台。
36. **Equipment Maintenance**：已补维修计划基础版本；下一步接 EAM、CMMS、点检系统、传感器平台、备件库存和生产排程。
37. **Media Operations**：已补内容分发基础版本；下一步接 CMS、热点监测、版权库、审核流、社媒排期和数据看板。
38. **Financial Risk**：已补风险预警基础版本；下一步接交易风控、规则引擎、设备指纹、人工复核台和审计系统。
39. **Urban Mobility**：已补交通响应基础版本；下一步接交通事件平台、公交调度、路况监测、停车诱导和公众通知平台。
40. **Real Estate Marketing**：已补线索转化基础版本；下一步接 CRM、广告投放平台、案场系统、内容审核流和成交复盘看板。
41. **Public Safety**：已补事件联动基础版本；下一步接事件平台、热线系统、现场巡查、交通协同、医疗联动和公众通知平台。
42. **Industrial Inspection**：已补安全巡检基础版本；下一步接点检系统、EAM、CMMS、传感器平台、备件库存和安全作业票系统。
43. **Environmental Monitoring**：已补污染响应基础版本；下一步接监测点位平台、IoT 传感器、环保工单、巡查记录、气象服务和公众披露平台。
44. **Restaurant Operations**：已补门店协同基础版本；下一步接 POS、排班系统、食安巡检、库存系统、外卖平台和顾客反馈看板。
45. **Game Operations**：已补版本复盘基础版本；下一步接玩家反馈平台、活动配置、数据看板、经济系统监控、公告系统和版本管理。
46. **Advertising Operations**：已补投放优化基础版本；下一步接广告平台、素材库、落地页分析、转化归因、品牌审核和预算看板。
47. **Community Operations**：已补社群增长基础版本；下一步接社群平台、内容日历、知识库、活动报名、CRM 线索池和运营看板。
48. **Customer QA**：已补服务质检基础版本；下一步接客服工单、质检规则库、知识库、培训系统、坐席反馈和质量看板。
49. **Store Service**：已补门店服务基础版本；下一步接门店 POS、会员服务台、客服工单、知识库、排班系统和体验回访看板。
50. **After-sales Service**：已补售后协同基础版本；下一步接售后工单系统、备件库存、工程师排班、物流查询、客服回访和知识库。
51. **Content Safety**：已补内容审核基础版本；下一步接内容审核平台、举报系统、规则引擎、人工复核台、运营通知和样本回灌管道。
52. **Live Commerce Operations**：已补直播场控基础版本；下一步接直播中控台、商品池、库存系统、客服工单、舆情看板和转化分析平台。
53. **Membership Growth**：已补会员增长基础版本；下一步接 CRM、会员中心、权益平台、营销触达系统、订单分析和客服反馈平台。
54. **Search Recommendation**：已补搜索推荐诊断基础版本；下一步接搜索日志平台、召回服务、排序服务、标注平台、AB 实验和指标看板。
55. **Payment Risk**：已补支付风控基础版本；下一步接支付网关、风控规则引擎、设备指纹、退款系统、人工复核台和审计日志平台。
56. **Shopping Assistant**：已补智能导购基础版本；下一步接商品主数据、库存价格系统、活动权益平台、客服知识库、导购会话和转化分析平台。
57. **DevRel Operations**：已补 DevRel 运营基础版本；下一步接 GitHub Issues、Discussions、社群反馈、文档访问分析、活动报名和贡献者看板。
58. **Brand Reputation**：已补品牌舆情基础版本；下一步接舆情监测平台、客服工单、社媒排期、品牌素材库、法务审核和公关复盘看板。
59. **Channel Operations**：已补渠道运营基础版本；下一步接渠道销售系统、库存系统、价格治理平台、经销商协同、促销系统和经营看板。
60. **Enterprise Training**：已补企业培训基础版本；下一步接 LMS、HR 系统、课程库、考试平台、练习环境和学习数据看板。
61. **Contract Fulfillment**：已补合同履约基础版本；下一步接合同管理系统、项目管理系统、交付工单、验收材料库、客户确认记录和财务回款看板。
62. **Tender Collaboration**：已补招投标协同基础版本；下一步接招标需求库、供应商响应文档、评分表、合规规则库、评审会议纪要和采购审批系统。
63. **Campus Operations**：已补园区运营基础版本；下一步接园区工单系统、能耗平台、访客系统、安防巡检、会议室预订、物业排班和运营看板。
64. **Property Leasing**：已补物业招商基础版本；下一步接招商 CRM、楼宇资源台账、租赁方案库、合同管理系统、带看日程和转化分析看板。
65. **Support Knowledge Operations**：已补客服知识运营基础版本；下一步接客服工单系统、知识库、坐席反馈、搜索日志、内容审核流和发布看板。
66. **Event Operations**：已补活动会务运营基础版本；下一步接活动报名系统、签到系统、场地资源、物料清单、讲师日程、问卷反馈和转化看板。
67. **Meeting Minutes**：下一步补会议材料、行动项、决策追踪和纪要复盘。
68. **Enterprise OKR**：下一步补目标拆解、进度风险、协同动作和季度复盘。
69. **Organization Knowledge Graph**：下一步补实体抽取、关系校验、知识更新和图谱复盘。

## README 写法建议

每个 use case README 至少回答：

- 这个 Agent 解决什么业务问题？
- 为什么它需要 KSADK 的 Runtime / Web UI / Toolsets，而不只是一个框架脚本？
- 用户 clone 后 30 秒内能运行什么命令？
- 未配置云能力时会如何降级？
- 接入真实能力时需要改哪些文件和环境变量？
- 如何验证 demo 没有坏？
