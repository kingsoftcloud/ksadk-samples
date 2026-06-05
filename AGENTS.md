# AGENTS.md

> `ksadk-samples` 的协作规则。适用于 Codex、Claude Code 和其他会在本仓库内读写、验证样例的智能体。

## 核心原则

- 这个仓库是 KSADK 的公开样例工坊，样例必须面向外部开发者可读、可运行、可部署。
- 不提交真实 AK/SK、dataset id、内部 endpoint、客户信息或内部业务文档。
- 每个样例必须包含 `README.md`、`agent.py`、`agentengine.yaml`、`requirements.txt`。
- `agentengine.yaml` 必须显式声明 `framework`、`entry_point`、`agent_variable`。
- 新增或修改样例时，优先保持现有目录结构：按用例组织，再按框架拆分。

## 本地环境与 E2E

- 本地运行、smoke test 和 e2e 验证必须使用 `uv` 创建并驱动仓库级虚拟环境。
- 不要依赖全局 Python、全局 `agentengine`，也不要把 `pip install -U "ksadk[all]"` 当成本仓库 e2e 的充分准备。
- 最近多次出现样例依赖没有被加入 `ksadk[all]` 的情况；验证时必须让样例自己的 `requirements.txt` 参与安装，避免全局环境掩盖缺依赖问题。
- 推荐仓库级准备命令：

```bash
uv venv
uv pip install -e ".[test]"
uv pip install -r <sample-dir>/requirements.txt
```

- 推荐样例运行命令：

```bash
uv run agentengine run -i .
uv run agentengine web .
uv run agentengine build . --push
uv run agentengine deploy .
```

## 验证纪律

- 修改样例结构后运行 `uv run python scripts/validate_samples.py`。
- 修改 `common/`、脚本或测试后运行 `uv run pytest -q`。
- 宣称某个样例本地可运行前，必须在对应样例目录用 `uv run agentengine run -i .` 做过真实 smoke；不能跑时说明缺少的模型配置、云权限或凭证。
- 不提交 `.env`、`.venv/`、`.pytest_cache/`、`__pycache__/`、`*.pyc`。
