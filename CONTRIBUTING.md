# Contributing

新增样例时请遵循以下约定：

1. 每个样例必须包含 `README.md`、`agent.py`、`agentengine.yaml`、`requirements.txt`。
2. `agentengine.yaml` 必须显式声明 `framework`、`entry_point`、`agent_variable`。
3. 样例不能包含真实 AK/SK、dataset id、内部 endpoint 或内部业务文档。
4. 样例应支持 `uv run agentengine run -i .`、`uv run agentengine web .`、`uv run agentengine deploy .`。
5. 本地 smoke / e2e 必须使用 `uv` 虚拟环境；可以安装 `ksadk[all]` 覆盖全量示例，也可以安装对应样例的 `requirements.txt` 验证最小依赖。
6. 提交前运行：

```bash
uv run python scripts/validate_samples.py
uv run pytest -q
```

公开同步或发布前运行：

```bash
make public-preflight
```

`public-preflight` 覆盖公开敏感信息扫描、样例结构校验和测试。当前 sample 仓库以轻量门禁为主；只有当仓库开始长期混放内部样例和公开样例时，才需要引入类似 `ksadk-python` 的独立公开工作树流程。

## 模块化与测试契约

`long-task-resume/langgraph` 采用渐进式模块化：`agent.py` 作入口 + `stages.py`（阶段数据）+ `llm_client.py`（LLM 调用）+ `search.py`（web 检索/抓取）。

**跨模块 monkeypatch（双 patch）**：函数抽到子模块后，`test_agent_behavior.py` patch `agent_module.xxx` 不拦截子模块内部调用，需同时 patch 定义模块。`load_agent` 已预加载 `_search_module`/`_llm_client_module` 到 agent_module 上，测试直接用 `agent_module._search_module` 做双 patch，无需局部 import。

继续抽 `workflow.py`（节点层）前需把节点的 `_call_required_llm`/`_web_search` 等依赖改为依赖注入（通过 Runner 实例属性），否则节点跨模块调用会引入 14+ 处双 patch。当前 ksadk `LangGraphRunner` 已支持 checkpointer/`aget_state`/`astream(None)`/interrupt，但节点编排仍需用户手写 `_build_execution_graph`；待 ksadk runner 演进到声明式托管节点后，samples 可直接用框架能力瘦身。
