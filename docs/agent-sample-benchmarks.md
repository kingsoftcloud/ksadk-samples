# Agent 样例对标笔记

这个文档记录 KSADK Samples 后续补齐场景 Agent 时的参考原则。它不是竞品宣传页，而是给维护者看的样例设计清单：新增 demo 前先看这些维度，避免样例退化成单文件脚本或不可运行的概念代码。

## 参考对象

| 项目 | 值得学习的点 | 在 KSADK Samples 中的落点 |
| --- | --- | --- |
| Google ADK Samples | 场景很多，README 会写清 Agent Details、架构图、运行、部署、测试和自定义方式。 | 每个样例必须有中文优先 README、运行命令、Web UI 调试、部署和常见问题。 |
| ADK Deep Search | 研究类 Agent 强调计划、人类确认、迭代检索、反思和最终报告。 | `deep-research/langgraph` 输出研究计划、执行轨迹、反思补查和交付物。 |
| ADK SWE Benchmark / Software Bug Assistant | Coding Agent 强调定位、工具、隔离执行、测试和评审风险。 | `coding-agent/langgraph` 输出变更定位、测试矩阵、发布风险和交付物。 |
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

1. **Deep Research Agent**：补 Web Search / Knowledge Base / 报告生成版本。
2. **Coding Agent**：补 Workspace + Sandbox 的真实文件读写和测试运行版本。
3. **Browser Agent**：补真实 Web UI 截图、DOM 观察和失败诊断。
4. **Data Analyst**：补 CSV / DuckDB / 图表产物。
5. **Customer Support**：补知识库、工单状态和升级策略。
6. **Multi-Agent Team**：补 planner / researcher / builder / reviewer 的子图或子 Agent 协作。

## README 写法建议

每个 use case README 至少回答：

- 这个 Agent 解决什么业务问题？
- 为什么它需要 KSADK 的 Runtime / Web UI / Toolsets，而不只是一个框架脚本？
- 用户 clone 后 30 秒内能运行什么命令？
- 未配置云能力时会如何降级？
- 接入真实能力时需要改哪些文件和环境变量？
- 如何验证 demo 没有坏？
