# KSADK 样例（Samples）

[![zread](https://img.shields.io/badge/Ask_Zread-_.svg?style=flat&color=00b0aa&labelColor=000000&logo=data%3Aimage%2Fsvg%2Bxml%3Bbase64%2CPHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAxNiAxNiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTQuOTYxNTYgMS42MDAxSDIuMjQxNTZDMS44ODgxIDEuNjAwMSAxLjYwMTU2IDEuODg2NjQgMS42MDE1NiAyLjI0MDFWNC45NjAxQzEuNjAxNTYgNS4zMTM1NiAxLjg4ODEgNS42MDAxIDIuMjQxNTYgNS42MDAxSDQuOTYxNTZDNS4zMTUwMiA1LjYwMDEgNS42MDE1NiA1LjMxMzU2IDUuNjAxNTYgNC45NjAxVjIuMjQwMUM1LjYwMTU2IDEuODg2NjQgNS4zMTUwMiAxLjYwMDEgNC45NjE1NiAxLjYwMDFaIiBmaWxsPSIjZmZmIi8%2BCjxwYXRoIGQ9Ik00Ljk2MTU2IDEwLjM5OTlIMi4yNDE1NkMxLjg4ODEgMTAuMzk5OSAxLjYwMTU2IDEwLjY4NjQgMS42MDE1NiAxMS4wMzk5VjEzLjc1OTlDMS42MDE1NiAxNC4xMTM0IDEuODg4MSAxNC4zOTk5IDIuMjQxNTYgMTQuMzk5OUg0Ljk2MTU2QzUuMzE1MDIgMTQuMzk5OSA1LjYwMTU2IDE0LjExMzQgNS42MDE1NiAxMy43NTk5VjExLjAzOTlDNS42MDE1NiAxMC42ODY0IDUuMzE1MDIgMTAuMzk5OSA0Ljk2MTU2IDEwLjM5OTlaIiBmaWxsPSIjZmZmIi8%2BCjxwYXRoIGQ9Ik0xMy43NTg0IDEuNjAwMUgxMS4wMzg0QzEwLjY4NSAxLjYwMDEgMTAuMzk4NCAxLjg4NjY0IDEwLjM5ODQgMi4yNDAxVjQuOTYwMUMxMC4zOTg0IDUuMzEzNTYgMTAuNjg1IDUuNjAwMSAxMS4wMzg0IDUuNjAwMUgxMy43NTg0QzE0LjExMTkgNS42MDAxIDE0LjM5ODQgNS4zMTM1NiAxNC4zOTg0IDQuOTYwMVYyLjI0MDFDMTQuMzk4NCAxLjg4NjY0IDE0LjExMTkgMS42MDAxIDEzLjc1ODQgMS42MDAxWiIgZmlsbD0iI2ZmZiIvPgo8cGF0aCBkPSJNNCAxMkwxMiA0TDQgMTJaIiBmaWxsPSIjZmZmIi8%2BCjxwYXRoIGQ9Ik00IDEyTDEyIDQiIHN0cm9rZT0iI2ZmZiIgc3Ryb2tlLXdpZHRoPSIxLjUiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIvPgo8L3N2Zz4K&logoColor=ffffff)](https://zread.ai/kingsoftcloud/ksadk-python)

KSADK Samples 是 AgentEngine / KSADK 的官方场景化代码工坊。仓库默认使用中文 README 和中文注释；`Samples` 和 `Examples` 都表示可运行、可部署、可对比框架写法的公开样例。

样例设计会持续参考 ADK Samples、VEADK Examples、AgentKit Samples、DeerFlow、SWE-agent / OpenHands / Aider 等优秀开源 Agent 项目；维护侧对标原则见 [Agent 样例对标笔记](docs/agent-sample-benchmarks.md)。

## 场景导航

### 按场景选择

| 场景 | 推荐样例 | 覆盖框架 |
| --- | --- | --- |
| 基础 Agent（Basic Agent） | `01-tutorials/hello-world` | Built With ADK / Built With LangGraph / Built With LangChain / Built With DeepAgents |
| 工具调用 Agent（Tool-Using Agent） | `01-tutorials/tool-calling` | Built With ADK / Built With LangGraph / Built With LangChain / Built With DeepAgents |
| 记忆增强 Agent（Memory-aware Agent） | `01-tutorials/memory` | Built With ADK / Built With LangGraph / Built With LangChain / Built With DeepAgents |
| 知识助手（Knowledge Assistant） | `02-use-cases/knowledge-base-rag` | Built With ADK / Built With LangGraph / Built With LangChain / Built With DeepAgents |
| 工作流 Agent（Workflow Agent） | `02-use-cases/agentengine-toolsets/langgraph` | Built With LangGraph |
| 深度研究 Agent（Deep Research Agent） | `02-use-cases/deep-research/langgraph` | Built With LangGraph |
| 编码 Agent（Coding Agent） | `02-use-cases/coding-agent/langgraph` | Built With LangGraph |
| 浏览器 Agent（Browser Agent） | `02-use-cases/browser-agent/langgraph` | Built With LangGraph |
| 数据分析 Agent（Data Analyst） | `02-use-cases/data-analyst/langgraph` | Built With LangGraph |
| 客服 Agent（Customer Support） | `02-use-cases/customer-support/langgraph` | Built With LangGraph |
| 多 Agent 团队（Multi-Agent Team） | `02-use-cases/multi-agent-team/langgraph` | Built With LangGraph |
| 运维告警 Agent（AIOps） | `02-use-cases/aiops/incident-triage-langgraph` | Built With LangGraph / Built With ADK / Built With LangChain / Built With DeepAgents |
| 财务审阅 Agent（Finance） | `02-use-cases/finance/report-review-langgraph` | Built With LangGraph / Built With ADK / Built With LangChain / Built With DeepAgents |
| 内容生产 Agent（Content Production） | `02-use-cases/content-production/campaign-planner-langgraph` | Built With LangGraph / Built With ADK / Built With LangChain / Built With DeepAgents |
| 企业知识运营 Agent（Knowledge Operations） | `02-use-cases/knowledge-operations/knowledge-curator-langgraph` | Built With LangGraph / Built With ADK / Built With LangChain / Built With DeepAgents |
| 销售运营 Agent（Sales Operations） | `02-use-cases/sales-operations/pipeline-copilot-langgraph` | Built With LangGraph / Built With ADK / Built With LangChain / Built With DeepAgents |
| 合规审阅 Agent（Compliance Review） | `02-use-cases/compliance-review/policy-review-langgraph` | Built With LangGraph / Built With ADK / Built With LangChain / Built With DeepAgents |
| 采购协同 Agent（Procurement Collaboration） | `02-use-cases/procurement-collaboration/vendor-selection-langgraph` | Built With LangGraph / Built With ADK / Built With LangChain / Built With DeepAgents |
| HR 招聘 Agent（HR Recruiting） | `02-use-cases/hr-recruiting/interview-planner-langgraph` | Built With LangGraph / Built With ADK / Built With LangChain / Built With DeepAgents |
| 项目管理 Agent（Project Management） | `02-use-cases/project-management/delivery-planner-langgraph` | Built With LangGraph / Built With ADK / Built With LangChain / Built With DeepAgents |
| 法务合同 Agent（Legal Contract） | `02-use-cases/legal-contract/contract-negotiation-langgraph` | Built With LangGraph / Built With ADK / Built With LangChain / Built With DeepAgents |
| 研发效能 Agent（Dev Productivity） | `02-use-cases/dev-productivity/engineering-efficiency-langgraph` | Built With LangGraph / Built With ADK / Built With LangChain / Built With DeepAgents |
| 产品运营 Agent（Product Operations） | `02-use-cases/product-operations/experiment-review-langgraph` | Built With LangGraph / Built With ADK / Built With LangChain / Built With DeepAgents |
| 数据治理 Agent（Data Governance） | `02-use-cases/data-governance/quality-audit-langgraph` | Built With LangGraph / Built With ADK / Built With LangChain / Built With DeepAgents |
| 安全审计 Agent（Security Audit） | `02-use-cases/security-audit/threat-review-langgraph` | Built With LangGraph / Built With ADK / Built With LangChain / Built With DeepAgents |
| 客户成功 Agent（Customer Success） | `02-use-cases/customer-success/health-review-langgraph` | Built With LangGraph / Built With ADK / Built With LangChain / Built With DeepAgents |
| 教育培训 Agent（Education Training） | `02-use-cases/education-training/learning-coach-langgraph` | Built With LangGraph / Built With ADK / Built With LangChain / Built With DeepAgents |
| 供应链计划 Agent（Supply Chain Planning） | `02-use-cases/supply-chain-planning/demand-planner-langgraph` | Built With LangGraph / Built With ADK / Built With LangChain / Built With DeepAgents |
| 长任务恢复 Agent（Long Task Resume） | `02-use-cases/long-task-resume` | Built With LangGraph / Built With ADK / Built With LangChain / Built With DeepAgents |
| 医疗运营 Agent（Healthcare Operations） | `02-use-cases/healthcare-operations/care-coordinator-langgraph` | Built With LangGraph / Built With ADK / Built With LangChain / Built With DeepAgents |
| 能源调度 Agent（Energy Dispatch） | `02-use-cases/energy-dispatch/load-balancer-langgraph` | Built With LangGraph / Built With ADK / Built With LangChain / Built With DeepAgents |
| 政务服务 Agent（Public Service） | `02-use-cases/public-service/case-assistant-langgraph` | Built With LangGraph / Built With ADK / Built With LangChain / Built With DeepAgents |
| 保险理赔 Agent（Insurance Claims） | `02-use-cases/insurance-claims/claim-review-langgraph` | Built With LangGraph / Built With ADK / Built With LangChain / Built With DeepAgents |
| 制造质量 Agent（Manufacturing Quality） | `02-use-cases/manufacturing-quality/defect-analysis-langgraph` | Built With LangGraph / Built With ADK / Built With LangChain / Built With DeepAgents |
| 零售运营 Agent（Retail Operations） | `02-use-cases/retail-operations/store-optimizer-langgraph` | Built With LangGraph / Built With ADK / Built With LangChain / Built With DeepAgents |
| 物流履约 Agent（Logistics Fulfillment） | `02-use-cases/logistics-fulfillment/delivery-exception-langgraph` | Built With LangGraph / Built With ADK / Built With LangChain / Built With DeepAgents |
| 房地产运营 Agent（Real Estate Operations） | `02-use-cases/real-estate-operations/asset-service-langgraph` | Built With LangGraph / Built With ADK / Built With LangChain / Built With DeepAgents |
| 农业生产 Agent（Agriculture Production） | `02-use-cases/agriculture-production/crop-planner-langgraph` | Built With LangGraph / Built With ADK / Built With LangChain / Built With DeepAgents |
| 通信运维 Agent（Telecom Operations） | `02-use-cases/telecom-operations/network-change-langgraph` | Built With LangGraph / Built With ADK / Built With LangChain / Built With DeepAgents |
| 旅游服务 Agent（Travel Service） | `02-use-cases/travel-service/trip-recovery-langgraph` | Built With LangGraph / Built With ADK / Built With LangChain / Built With DeepAgents |
| 设备维护 Agent（Equipment Maintenance） | `02-use-cases/equipment-maintenance/maintenance-planner-langgraph` | Built With LangGraph / Built With ADK / Built With LangChain / Built With DeepAgents |
| 媒体运营 Agent（Media Operations） | `02-use-cases/media-operations/content-distribution-langgraph` | Built With LangGraph / Built With ADK / Built With LangChain / Built With DeepAgents |
| 金融风控 Agent（Financial Risk） | `02-use-cases/financial-risk/risk-alert-langgraph` | Built With LangGraph / Built With ADK / Built With LangChain / Built With DeepAgents |
| 城市交通 Agent（Urban Mobility） | `02-use-cases/urban-mobility/traffic-response-langgraph` | Built With LangGraph / Built With ADK / Built With LangChain / Built With DeepAgents |
| 地产营销 Agent（Real Estate Marketing） | `02-use-cases/real-estate-marketing/lead-conversion-langgraph` | Built With LangGraph / Built With ADK / Built With LangChain / Built With DeepAgents |
| 公共安全 Agent（Public Safety） | `02-use-cases/public-safety/incident-coordination-langgraph` | Built With LangGraph / Built With ADK / Built With LangChain / Built With DeepAgents |
| 工业巡检 Agent（Industrial Inspection） | `02-use-cases/industrial-inspection/safety-patrol-langgraph` | Built With LangGraph / Built With ADK / Built With LangChain / Built With DeepAgents |
| 环境监测 Agent（Environmental Monitoring） | `02-use-cases/environmental-monitoring/pollution-response-langgraph` | Built With LangGraph / Built With ADK / Built With LangChain / Built With DeepAgents |
| 餐饮运营 Agent（Restaurant Operations） | `02-use-cases/restaurant-operations/store-ops-langgraph` | Built With LangGraph / Built With ADK / Built With LangChain / Built With DeepAgents |
| 游戏运营 Agent（Game Operations） | `02-use-cases/game-operations/liveops-review-langgraph` | Built With LangGraph / Built With ADK / Built With LangChain / Built With DeepAgents |
| 广告投放 Agent（Advertising Operations） | `02-use-cases/advertising-operations/campaign-optimization-langgraph` | Built With LangGraph / Built With ADK / Built With LangChain / Built With DeepAgents |
| 社群运营 Agent（Community Operations） | `02-use-cases/community-operations/community-growth-langgraph` | Built With LangGraph / Built With ADK / Built With LangChain / Built With DeepAgents |
| 客服质检 Agent（Customer QA） | `02-use-cases/customer-qa/service-quality-langgraph` | Built With LangGraph / Built With ADK / Built With LangChain / Built With DeepAgents |
| 门店客服 Agent（Store Service） | `02-use-cases/store-service/store-advisor-langgraph` | Built With LangGraph / Built With ADK / Built With LangChain / Built With DeepAgents |
| 售后服务 Agent（After-sales Service） | `02-use-cases/after-sales-service/repair-coordinator-langgraph` | Built With LangGraph / Built With ADK / Built With LangChain / Built With DeepAgents |
| 内容安全 Agent（Content Safety） | `02-use-cases/content-safety/moderation-review-langgraph` | Built With LangGraph / Built With ADK / Built With LangChain / Built With DeepAgents |
| 直播运营 Agent（Live Commerce Operations） | `02-use-cases/live-commerce-operations/session-control-langgraph` | Built With LangGraph / Built With ADK / Built With LangChain / Built With DeepAgents |
| 会员增长 Agent（Membership Growth） | `02-use-cases/membership-growth/member-lifecycle-langgraph` | Built With LangGraph / Built With ADK / Built With LangChain / Built With DeepAgents |
| 搜索推荐 Agent（Search Recommendation） | `02-use-cases/search-recommendation/relevance-diagnostics-langgraph` | Built With LangGraph / Built With ADK / Built With LangChain / Built With DeepAgents |
| 支付风控 Agent（Payment Risk） | `02-use-cases/payment-risk/payment-guard-langgraph` | Built With LangGraph / Built With ADK / Built With LangChain / Built With DeepAgents |
| 智能导购 Agent（Shopping Assistant） | `02-use-cases/shopping-assistant/product-advisor-langgraph` | Built With LangGraph / Built With ADK / Built With LangChain / Built With DeepAgents |
| DevRel 运营 Agent（DevRel Operations） | `02-use-cases/devrel-operations/community-program-langgraph` | Built With LangGraph / Built With ADK / Built With LangChain / Built With DeepAgents |
| 品牌舆情 Agent（Brand Reputation） | `02-use-cases/brand-reputation/reputation-response-langgraph` | Built With LangGraph / Built With ADK / Built With LangChain / Built With DeepAgents |
| 渠道运营 Agent（Channel Operations） | `02-use-cases/channel-operations/channel-health-langgraph` | Built With LangGraph / Built With ADK / Built With LangChain / Built With DeepAgents |
| 企业培训 Agent（Enterprise Training） | `02-use-cases/enterprise-training/training-planner-langgraph` | Built With LangGraph / Built With ADK / Built With LangChain / Built With DeepAgents |
| 合同履约 Agent（Contract Fulfillment） | `02-use-cases/contract-fulfillment/fulfillment-monitor-langgraph` | Built With LangGraph / Built With ADK / Built With LangChain / Built With DeepAgents |
| 招投标协同 Agent（Tender Collaboration） | `02-use-cases/tender-collaboration/bid-evaluator-langgraph` | Built With LangGraph / Built With ADK / Built With LangChain / Built With DeepAgents |
| 园区运营 Agent（Campus Operations） | `02-use-cases/campus-operations/campus-service-langgraph` | Built With LangGraph / Built With ADK / Built With LangChain / Built With DeepAgents |

### 最佳实践案例

| 目标 | LangGraph | ADK | LangChain | DeepAgents |
| --- | --- | --- | --- | --- |
| Deep Research 报告生成 | `02-use-cases/deep-research/report-writer-langgraph` | `02-use-cases/deep-research/report-writer-adk` | `02-use-cases/deep-research/report-writer-langchain` | `02-use-cases/deep-research/report-writer-deepagents` |
| Coding Workspace + Sandbox | `02-use-cases/coding-agent/workspace-sandbox-langgraph` | `02-use-cases/coding-agent/workspace-sandbox-adk` | `02-use-cases/coding-agent/workspace-sandbox-langchain` | `02-use-cases/coding-agent/workspace-sandbox-deepagents` |
| Browser DOM 诊断 | `02-use-cases/browser-agent/dom-diagnostics-langgraph` | `02-use-cases/browser-agent/dom-diagnostics-adk` | `02-use-cases/browser-agent/dom-diagnostics-langchain` | `02-use-cases/browser-agent/dom-diagnostics-deepagents` |
| Data Analyst CSV 洞察 | `02-use-cases/data-analyst/csv-insight-langgraph` | `02-use-cases/data-analyst/csv-insight-adk` | `02-use-cases/data-analyst/csv-insight-langchain` | `02-use-cases/data-analyst/csv-insight-deepagents` |
| Customer Support 工单分级 | `02-use-cases/customer-support/ticket-triage-langgraph` | `02-use-cases/customer-support/ticket-triage-adk` | `02-use-cases/customer-support/ticket-triage-langchain` | `02-use-cases/customer-support/ticket-triage-deepagents` |
| Multi-Agent Team 协作交付 | `02-use-cases/multi-agent-team/team-delivery-langgraph` | `02-use-cases/multi-agent-team/team-delivery-adk` | `02-use-cases/multi-agent-team/team-delivery-langchain` | `02-use-cases/multi-agent-team/team-delivery-deepagents` |
| AIOps 告警分诊 | `02-use-cases/aiops/incident-triage-langgraph` | `02-use-cases/aiops/incident-triage-adk` | `02-use-cases/aiops/incident-triage-langchain` | `02-use-cases/aiops/incident-triage-deepagents` |
| Finance 报表审阅 | `02-use-cases/finance/report-review-langgraph` | `02-use-cases/finance/report-review-adk` | `02-use-cases/finance/report-review-langchain` | `02-use-cases/finance/report-review-deepagents` |
| Content Production 传播计划 | `02-use-cases/content-production/campaign-planner-langgraph` | `02-use-cases/content-production/campaign-planner-adk` | `02-use-cases/content-production/campaign-planner-langchain` | `02-use-cases/content-production/campaign-planner-deepagents` |
| Knowledge Operations 知识运营 | `02-use-cases/knowledge-operations/knowledge-curator-langgraph` | `02-use-cases/knowledge-operations/knowledge-curator-adk` | `02-use-cases/knowledge-operations/knowledge-curator-langchain` | `02-use-cases/knowledge-operations/knowledge-curator-deepagents` |
| Sales Operations Pipeline | `02-use-cases/sales-operations/pipeline-copilot-langgraph` | `02-use-cases/sales-operations/pipeline-copilot-adk` | `02-use-cases/sales-operations/pipeline-copilot-langchain` | `02-use-cases/sales-operations/pipeline-copilot-deepagents` |
| Compliance Review 合规审阅 | `02-use-cases/compliance-review/policy-review-langgraph` | `02-use-cases/compliance-review/policy-review-adk` | `02-use-cases/compliance-review/policy-review-langchain` | `02-use-cases/compliance-review/policy-review-deepagents` |
| Procurement Collaboration 采购协同 | `02-use-cases/procurement-collaboration/vendor-selection-langgraph` | `02-use-cases/procurement-collaboration/vendor-selection-adk` | `02-use-cases/procurement-collaboration/vendor-selection-langchain` | `02-use-cases/procurement-collaboration/vendor-selection-deepagents` |
| HR Recruiting 面试计划 | `02-use-cases/hr-recruiting/interview-planner-langgraph` | `02-use-cases/hr-recruiting/interview-planner-adk` | `02-use-cases/hr-recruiting/interview-planner-langchain` | `02-use-cases/hr-recruiting/interview-planner-deepagents` |
| Project Management 交付计划 | `02-use-cases/project-management/delivery-planner-langgraph` | `02-use-cases/project-management/delivery-planner-adk` | `02-use-cases/project-management/delivery-planner-langchain` | `02-use-cases/project-management/delivery-planner-deepagents` |
| Legal Contract 合同谈判 | `02-use-cases/legal-contract/contract-negotiation-langgraph` | `02-use-cases/legal-contract/contract-negotiation-adk` | `02-use-cases/legal-contract/contract-negotiation-langchain` | `02-use-cases/legal-contract/contract-negotiation-deepagents` |
| Dev Productivity 研发效能 | `02-use-cases/dev-productivity/engineering-efficiency-langgraph` | `02-use-cases/dev-productivity/engineering-efficiency-adk` | `02-use-cases/dev-productivity/engineering-efficiency-langchain` | `02-use-cases/dev-productivity/engineering-efficiency-deepagents` |
| Product Operations 实验复盘 | `02-use-cases/product-operations/experiment-review-langgraph` | `02-use-cases/product-operations/experiment-review-adk` | `02-use-cases/product-operations/experiment-review-langchain` | `02-use-cases/product-operations/experiment-review-deepagents` |
| Data Governance 质量审计 | `02-use-cases/data-governance/quality-audit-langgraph` | `02-use-cases/data-governance/quality-audit-adk` | `02-use-cases/data-governance/quality-audit-langchain` | `02-use-cases/data-governance/quality-audit-deepagents` |
| Security Audit 威胁评审 | `02-use-cases/security-audit/threat-review-langgraph` | `02-use-cases/security-audit/threat-review-adk` | `02-use-cases/security-audit/threat-review-langchain` | `02-use-cases/security-audit/threat-review-deepagents` |
| Customer Success 健康复盘 | `02-use-cases/customer-success/health-review-langgraph` | `02-use-cases/customer-success/health-review-adk` | `02-use-cases/customer-success/health-review-langchain` | `02-use-cases/customer-success/health-review-deepagents` |
| Education Training 学习辅导 | `02-use-cases/education-training/learning-coach-langgraph` | `02-use-cases/education-training/learning-coach-adk` | `02-use-cases/education-training/learning-coach-langchain` | `02-use-cases/education-training/learning-coach-deepagents` |
| Supply Chain Planning 需求计划 | `02-use-cases/supply-chain-planning/demand-planner-langgraph` | `02-use-cases/supply-chain-planning/demand-planner-adk` | `02-use-cases/supply-chain-planning/demand-planner-langchain` | `02-use-cases/supply-chain-planning/demand-planner-deepagents` |
| Long Task Resume 长任务恢复 | `02-use-cases/long-task-resume/langgraph` | `02-use-cases/long-task-resume/adk` | `02-use-cases/long-task-resume/langchain` | `02-use-cases/long-task-resume/deepagents` |
| Healthcare Operations 护理协同 | `02-use-cases/healthcare-operations/care-coordinator-langgraph` | `02-use-cases/healthcare-operations/care-coordinator-adk` | `02-use-cases/healthcare-operations/care-coordinator-langchain` | `02-use-cases/healthcare-operations/care-coordinator-deepagents` |
| Energy Dispatch 负荷平衡 | `02-use-cases/energy-dispatch/load-balancer-langgraph` | `02-use-cases/energy-dispatch/load-balancer-adk` | `02-use-cases/energy-dispatch/load-balancer-langchain` | `02-use-cases/energy-dispatch/load-balancer-deepagents` |
| Public Service 事项协同 | `02-use-cases/public-service/case-assistant-langgraph` | `02-use-cases/public-service/case-assistant-adk` | `02-use-cases/public-service/case-assistant-langchain` | `02-use-cases/public-service/case-assistant-deepagents` |
| Insurance Claims 理赔审核 | `02-use-cases/insurance-claims/claim-review-langgraph` | `02-use-cases/insurance-claims/claim-review-adk` | `02-use-cases/insurance-claims/claim-review-langchain` | `02-use-cases/insurance-claims/claim-review-deepagents` |
| Manufacturing Quality 缺陷分析 | `02-use-cases/manufacturing-quality/defect-analysis-langgraph` | `02-use-cases/manufacturing-quality/defect-analysis-adk` | `02-use-cases/manufacturing-quality/defect-analysis-langchain` | `02-use-cases/manufacturing-quality/defect-analysis-deepagents` |
| Retail Operations 门店优化 | `02-use-cases/retail-operations/store-optimizer-langgraph` | `02-use-cases/retail-operations/store-optimizer-adk` | `02-use-cases/retail-operations/store-optimizer-langchain` | `02-use-cases/retail-operations/store-optimizer-deepagents` |
| Logistics Fulfillment 履约异常 | `02-use-cases/logistics-fulfillment/delivery-exception-langgraph` | `02-use-cases/logistics-fulfillment/delivery-exception-adk` | `02-use-cases/logistics-fulfillment/delivery-exception-langchain` | `02-use-cases/logistics-fulfillment/delivery-exception-deepagents` |
| Real Estate Operations 资产服务 | `02-use-cases/real-estate-operations/asset-service-langgraph` | `02-use-cases/real-estate-operations/asset-service-adk` | `02-use-cases/real-estate-operations/asset-service-langchain` | `02-use-cases/real-estate-operations/asset-service-deepagents` |
| Agriculture Production 农事计划 | `02-use-cases/agriculture-production/crop-planner-langgraph` | `02-use-cases/agriculture-production/crop-planner-adk` | `02-use-cases/agriculture-production/crop-planner-langchain` | `02-use-cases/agriculture-production/crop-planner-deepagents` |
| Telecom Operations 网络割接 | `02-use-cases/telecom-operations/network-change-langgraph` | `02-use-cases/telecom-operations/network-change-adk` | `02-use-cases/telecom-operations/network-change-langchain` | `02-use-cases/telecom-operations/network-change-deepagents` |
| Travel Service 行程恢复 | `02-use-cases/travel-service/trip-recovery-langgraph` | `02-use-cases/travel-service/trip-recovery-adk` | `02-use-cases/travel-service/trip-recovery-langchain` | `02-use-cases/travel-service/trip-recovery-deepagents` |
| Equipment Maintenance 维修计划 | `02-use-cases/equipment-maintenance/maintenance-planner-langgraph` | `02-use-cases/equipment-maintenance/maintenance-planner-adk` | `02-use-cases/equipment-maintenance/maintenance-planner-langchain` | `02-use-cases/equipment-maintenance/maintenance-planner-deepagents` |
| Media Operations 内容分发 | `02-use-cases/media-operations/content-distribution-langgraph` | `02-use-cases/media-operations/content-distribution-adk` | `02-use-cases/media-operations/content-distribution-langchain` | `02-use-cases/media-operations/content-distribution-deepagents` |
| Financial Risk 风险预警 | `02-use-cases/financial-risk/risk-alert-langgraph` | `02-use-cases/financial-risk/risk-alert-adk` | `02-use-cases/financial-risk/risk-alert-langchain` | `02-use-cases/financial-risk/risk-alert-deepagents` |
| Urban Mobility 交通响应 | `02-use-cases/urban-mobility/traffic-response-langgraph` | `02-use-cases/urban-mobility/traffic-response-adk` | `02-use-cases/urban-mobility/traffic-response-langchain` | `02-use-cases/urban-mobility/traffic-response-deepagents` |
| Real Estate Marketing 线索转化 | `02-use-cases/real-estate-marketing/lead-conversion-langgraph` | `02-use-cases/real-estate-marketing/lead-conversion-adk` | `02-use-cases/real-estate-marketing/lead-conversion-langchain` | `02-use-cases/real-estate-marketing/lead-conversion-deepagents` |
| Public Safety 事件联动 | `02-use-cases/public-safety/incident-coordination-langgraph` | `02-use-cases/public-safety/incident-coordination-adk` | `02-use-cases/public-safety/incident-coordination-langchain` | `02-use-cases/public-safety/incident-coordination-deepagents` |
| Industrial Inspection 安全巡检 | `02-use-cases/industrial-inspection/safety-patrol-langgraph` | `02-use-cases/industrial-inspection/safety-patrol-adk` | `02-use-cases/industrial-inspection/safety-patrol-langchain` | `02-use-cases/industrial-inspection/safety-patrol-deepagents` |
| Environmental Monitoring 污染响应 | `02-use-cases/environmental-monitoring/pollution-response-langgraph` | `02-use-cases/environmental-monitoring/pollution-response-adk` | `02-use-cases/environmental-monitoring/pollution-response-langchain` | `02-use-cases/environmental-monitoring/pollution-response-deepagents` |
| Restaurant Operations 门店协同 | `02-use-cases/restaurant-operations/store-ops-langgraph` | `02-use-cases/restaurant-operations/store-ops-adk` | `02-use-cases/restaurant-operations/store-ops-langchain` | `02-use-cases/restaurant-operations/store-ops-deepagents` |
| Game Operations 版本复盘 | `02-use-cases/game-operations/liveops-review-langgraph` | `02-use-cases/game-operations/liveops-review-adk` | `02-use-cases/game-operations/liveops-review-langchain` | `02-use-cases/game-operations/liveops-review-deepagents` |
| Advertising Operations 投放优化 | `02-use-cases/advertising-operations/campaign-optimization-langgraph` | `02-use-cases/advertising-operations/campaign-optimization-adk` | `02-use-cases/advertising-operations/campaign-optimization-langchain` | `02-use-cases/advertising-operations/campaign-optimization-deepagents` |
| Community Operations 社群增长 | `02-use-cases/community-operations/community-growth-langgraph` | `02-use-cases/community-operations/community-growth-adk` | `02-use-cases/community-operations/community-growth-langchain` | `02-use-cases/community-operations/community-growth-deepagents` |
| Customer QA 服务质检 | `02-use-cases/customer-qa/service-quality-langgraph` | `02-use-cases/customer-qa/service-quality-adk` | `02-use-cases/customer-qa/service-quality-langchain` | `02-use-cases/customer-qa/service-quality-deepagents` |
| Store Service 门店客服 | `02-use-cases/store-service/store-advisor-langgraph` | `02-use-cases/store-service/store-advisor-adk` | `02-use-cases/store-service/store-advisor-langchain` | `02-use-cases/store-service/store-advisor-deepagents` |
| After-sales Service 售后协同 | `02-use-cases/after-sales-service/repair-coordinator-langgraph` | `02-use-cases/after-sales-service/repair-coordinator-adk` | `02-use-cases/after-sales-service/repair-coordinator-langchain` | `02-use-cases/after-sales-service/repair-coordinator-deepagents` |
| Content Safety 内容审核 | `02-use-cases/content-safety/moderation-review-langgraph` | `02-use-cases/content-safety/moderation-review-adk` | `02-use-cases/content-safety/moderation-review-langchain` | `02-use-cases/content-safety/moderation-review-deepagents` |
| Live Commerce Operations 直播场控 | `02-use-cases/live-commerce-operations/session-control-langgraph` | `02-use-cases/live-commerce-operations/session-control-adk` | `02-use-cases/live-commerce-operations/session-control-langchain` | `02-use-cases/live-commerce-operations/session-control-deepagents` |
| Membership Growth 会员增长 | `02-use-cases/membership-growth/member-lifecycle-langgraph` | `02-use-cases/membership-growth/member-lifecycle-adk` | `02-use-cases/membership-growth/member-lifecycle-langchain` | `02-use-cases/membership-growth/member-lifecycle-deepagents` |
| Search Recommendation 相关性诊断 | `02-use-cases/search-recommendation/relevance-diagnostics-langgraph` | `02-use-cases/search-recommendation/relevance-diagnostics-adk` | `02-use-cases/search-recommendation/relevance-diagnostics-langchain` | `02-use-cases/search-recommendation/relevance-diagnostics-deepagents` |
| Payment Risk 支付风控 | `02-use-cases/payment-risk/payment-guard-langgraph` | `02-use-cases/payment-risk/payment-guard-adk` | `02-use-cases/payment-risk/payment-guard-langchain` | `02-use-cases/payment-risk/payment-guard-deepagents` |
| Shopping Assistant 智能导购 | `02-use-cases/shopping-assistant/product-advisor-langgraph` | `02-use-cases/shopping-assistant/product-advisor-adk` | `02-use-cases/shopping-assistant/product-advisor-langchain` | `02-use-cases/shopping-assistant/product-advisor-deepagents` |
| DevRel Operations 开发者运营 | `02-use-cases/devrel-operations/community-program-langgraph` | `02-use-cases/devrel-operations/community-program-adk` | `02-use-cases/devrel-operations/community-program-langchain` | `02-use-cases/devrel-operations/community-program-deepagents` |
| Brand Reputation 品牌舆情 | `02-use-cases/brand-reputation/reputation-response-langgraph` | `02-use-cases/brand-reputation/reputation-response-adk` | `02-use-cases/brand-reputation/reputation-response-langchain` | `02-use-cases/brand-reputation/reputation-response-deepagents` |
| Channel Operations 渠道运营 | `02-use-cases/channel-operations/channel-health-langgraph` | `02-use-cases/channel-operations/channel-health-adk` | `02-use-cases/channel-operations/channel-health-langchain` | `02-use-cases/channel-operations/channel-health-deepagents` |
| Enterprise Training 企业培训 | `02-use-cases/enterprise-training/training-planner-langgraph` | `02-use-cases/enterprise-training/training-planner-adk` | `02-use-cases/enterprise-training/training-planner-langchain` | `02-use-cases/enterprise-training/training-planner-deepagents` |
| Contract Fulfillment 合同履约 | `02-use-cases/contract-fulfillment/fulfillment-monitor-langgraph` | `02-use-cases/contract-fulfillment/fulfillment-monitor-adk` | `02-use-cases/contract-fulfillment/fulfillment-monitor-langchain` | `02-use-cases/contract-fulfillment/fulfillment-monitor-deepagents` |
| Tender Collaboration 招投标协同 | `02-use-cases/tender-collaboration/bid-evaluator-langgraph` | `02-use-cases/tender-collaboration/bid-evaluator-adk` | `02-use-cases/tender-collaboration/bid-evaluator-langchain` | `02-use-cases/tender-collaboration/bid-evaluator-deepagents` |
| Campus Operations 园区运营 | `02-use-cases/campus-operations/campus-service-langgraph` | `02-use-cases/campus-operations/campus-service-adk` | `02-use-cases/campus-operations/campus-service-langchain` | `02-use-cases/campus-operations/campus-service-deepagents` |

长任务恢复是横向 Runtime 能力样例，见 `02-use-cases/long-task-resume/{langgraph,adk,langchain,deepagents}`。它重点演示 checkpoint 列表、ResumeRun、tool receipt 去重、CancelRun 和未配置持久化后端时的降级行为。

### 推荐主推 Demo

```bash
cd 02-use-cases/agentengine-toolsets/langgraph
uv pip install -r requirements.txt
uv run agentengine run -i .
```

这个 demo 展示 LangGraph 如何绑定 AgentEngine Toolsets，并覆盖 Skill Space、Skill Runtime、Workspace、Sandbox、知识库和长期记忆的配置边界。未配置平台能力时，demo 会解释缺失项和降级行为，不伪造平台结果。

### 真实 Web UI 演示

下面是 `02-use-cases/deep-research/langgraph` 在本地 `agentengine web` 中的真实问答录制，展示了一个 LangGraph Deep Research Agent 如何输出研究计划、执行轨迹、证据卡片、反思补查和交付物。

![Deep Research Web UI 演示](assets/screenshots/deep-research-webui-demo.gif)

## 环境准备

仓库根目录开发：

```bash
uv venv
uv pip install -e ".[test]"
```

单个样例运行：

```bash
cd 01-tutorials/hello-world/adk
cp ../../../.env.example .env
uv pip install -r requirements.txt
uv run agentengine run -i .
uv run agentengine web .
```

```bash
uv pip install -U "ksadk[all]"
```

每个样例默认读取“当前样例目录”的 `.env`。如果你习惯在仓库根目录维护一份 `.env`，请先 `source .env` 或把它复制到要运行的样例目录。

最小 `.env`：

```bash
OPENAI_API_KEY=your-openai-compatible-api-key
OPENAI_MODEL_NAME=gpt-4o-mini
```

非默认 OpenAI endpoint 时再设置 `OPENAI_BASE_URL`；完整能力集可直接安装 `ksadk[all]`。

## 平台能力配置速查

只配置模型时，大多数基础样例可运行；下面变量只在对应能力需要时填写。

| 能力 | 关键环境变量 | 未配置时 |
| --- | --- | --- |
| 云账号 | `KSYUN_ACCESS_KEY`、`KSYUN_SECRET_KEY`、`KSYUN_REGION=cn-beijing-6` | 不能部署或调用云服务 |
| Skill Space | `KSADK_SKILL_SPACE_IDS` / `SKILL_SPACE_ID`、`KSADK_PUBLIC_SKILL_SPACE_IDS`、`KSADK_SKILL_SERVICE_URL`、`KSADK_SKILL_SERVICE_ACCESS_KEY` | 只能提示缺少 Space、endpoint 或凭证 |
| Skill Runtime | `local_process` 配 `KSADK_SKILL_RUNTIME_AGENT_PATH`；`e2b` 配 `KSADK_SANDBOX_TEMPLATE_ID`、`E2B_API_URL`、`E2B_API_KEY` | 可发现 Skill，但不执行 workflow |
| Workspace | 本地 `agentengine run/web` 自动注入；远端由 AgentEngine runtime 注入 | 不能读写会话 workspace 文件 |
| Sandbox | `KSADK_SANDBOX_BACKEND=e2b`、`KSADK_SANDBOX_TEMPLATE_ID`、`E2B_API_URL`、`E2B_API_KEY` | `run_command` / `run_code` 返回不可用 |
| 知识库 | `KSADK_KB_DATASET_ID`、`KSADK_KB_ENDPOINT`、`KSADK_KB_REGION`、`KSADK_KB_TOP_K` | RAG demo 使用本地 corpus |
| 长期记忆 | `KSADK_LTM_BACKEND`、`KSADK_LTM_INDEX`、`KSADK_LTM_NAMESPACE`、`KSADK_LTM_HTTP_URL` | 记忆 demo 使用本地示例记忆 |

完整解释见主推 demo：[02-use-cases/agentengine-toolsets/langgraph/README.md](02-use-cases/agentengine-toolsets/langgraph/README.md)。

## 相关资源

- 文档：https://kingsoftcloud.github.io/ksadk-python/
- KSADK 仓库：https://github.com/kingsoftcloud/ksadk-python
- Wiki：https://zread.ai/kingsoftcloud/ksadk-python
- Web UI 仓库：https://github.com/kingsoftcloud/ksadk-web
- PyPI：https://pypi.org/project/ksadk/
- 开源协议：Apache-2.0

## 仓库校验

```bash
uv run python scripts/validate_samples.py
uv run pytest -q
make public-preflight
```

`validate_samples.py` 会检查样例结构、README 必备章节、Python 语法 smoke 和敏感内容扫描；`public-preflight` 是公开同步或发布前门禁。

## 后续计划

后续会继续补充更多框架版本和更重的行业样例。新增样例只有在本地可运行、可部署、可脱敏验证、README 足够完整时，才会加入代码目录。

- 为更多场景补充框架版本；当前报告生成、工作区沙箱、浏览器 DOM 诊断、CSV 洞察、工单分级、团队协作、AIOps 告警分诊、财务报表审阅、内容生产、企业知识运营、销售运营、合规审阅、采购协同、HR 招聘、项目管理、法务合同、研发效能、产品运营、数据治理、安全审计、客户成功、教育培训、供应链计划、长任务恢复、医疗运营、能源调度、政务服务、保险理赔、制造质量、零售运营、物流履约、房地产运营、农业生产、通信运维、旅游服务、设备维护、媒体运营、金融风控、城市交通、地产营销、公共安全、工业巡检、环境监测、餐饮运营、游戏运营、广告投放、社群运营、客服质检、门店客服、售后服务、内容安全、直播运营、会员增长、搜索推荐、支付风控、智能导购、DevRel 运营、品牌舆情、渠道运营、企业培训、合同履约、招投标协同和园区运营已覆盖 LangGraph / ADK / LangChain / DeepAgents。
- 增加更多真实 Web UI GIF 和端到端部署录屏；当前已提供 Deep Research Web UI 演示。
- 增加更多行业场景，如物业招商、客服知识运营和活动会务运营。
- 长任务恢复已补多框架工程版本；后续可继续接真实 Postgres session backend 和平台 run/session 事件。
