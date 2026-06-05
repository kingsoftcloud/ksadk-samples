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
