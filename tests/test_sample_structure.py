from pathlib import Path
import importlib.util
import os
import sys

import yaml

from scripts import check_public_readiness
from scripts import validate_samples


ROOT = Path(__file__).resolve().parents[1]


def _version_tuple(version: str) -> tuple[int, int, int]:
    parts = version.split(".")
    numeric = []
    for part in parts[:3]:
        digits = "".join(character for character in part if character.isdigit())
        numeric.append(int(digits or "0"))
    while len(numeric) < 3:
        numeric.append(0)
    return tuple(numeric)


def test_ksadk_runtime_is_at_least_0_6_2():
    import ksadk

    assert _version_tuple(ksadk.__version__) >= (0, 6, 2)


def test_root_readme_lists_public_project_resources():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    license_text = (ROOT / "LICENSE").read_text(encoding="utf-8")
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert "Ask_Zread" in readme
    for expected in (
        "https://kingsoftcloud.github.io/ksadk-python/",
        "https://github.com/kingsoftcloud/ksadk-python",
        "https://zread.ai/kingsoftcloud/ksadk-python",
        "https://github.com/kingsoftcloud/ksadk-web",
        "https://pypi.org/project/ksadk/",
        "Apache-2.0",
    ):
        assert expected in readme
    assert "Apache License" in license_text
    assert 'license = "Apache-2.0"' in pyproject


def test_root_readme_is_scenario_navigation_and_mentions_examples_alias():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for required in (
        "默认使用中文 README",
        "场景导航",
        "Examples",
        "Samples",
        "按场景选择",
        "推荐主推 Demo",
        "02-use-cases/agentengine-toolsets/langgraph",
    ):
        assert required in readme


def test_root_readme_uses_prd_scenario_categories_without_overclaiming():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for available in (
        "Knowledge Assistant",
        "Workflow Agent",
        "Tool-Using Agent",
        "Memory-aware Agent",
        "Built With LangGraph",
        "Built With ADK",
        "Built With DeepAgents",
        "Deep Research Agent",
        "Coding Agent",
        "Browser Agent",
        "Data Analyst",
        "Customer Support",
        "Multi-Agent Team",
    ):
        assert available in readme

    if "## 后续计划" in readme:
        roadmap = readme[readme.index("## 后续计划"):]
        for implemented in (
            "Deep Research Agent",
            "Coding Agent",
            "Browser Agent",
            "Data Analyst",
            "Customer Support",
            "Multi-Agent Team",
        ):
            assert implemented not in roadmap


def test_readme_roadmap_scenarios_have_runnable_agents():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    required_scenarios = {
        "Deep Research Agent": "02-use-cases/deep-research/langgraph",
        "Coding Agent": "02-use-cases/coding-agent/langgraph",
        "Browser Agent": "02-use-cases/browser-agent/langgraph",
        "Data Analyst": "02-use-cases/data-analyst/langgraph",
        "Customer Support": "02-use-cases/customer-support/langgraph",
        "Multi-Agent Team": "02-use-cases/multi-agent-team/langgraph",
    }

    for scenario_name, relative_dir in required_scenarios.items():
        assert scenario_name in readme
        assert relative_dir in readme
        sample_dir = ROOT / relative_dir
        assert (sample_dir / "README.md").is_file()
        assert (sample_dir / "agent.py").is_file()
        assert (sample_dir / "workflow.py").is_file()
        assert (sample_dir / "prompts.py").is_file()
        assert (sample_dir / "agentengine.yaml").is_file()
        assert (sample_dir / "requirements.txt").is_file()
        assert (sample_dir / "demo.py").is_file()
        assert (sample_dir / "tools.py").is_file() or (sample_dir / "data.py").is_file()
        assert len((sample_dir / "agent.py").read_text(encoding="utf-8").splitlines()) <= 40

    roadmap_start = readme.find("## 后续计划")
    if roadmap_start != -1:
        roadmap = readme[roadmap_start:]
        for scenario_name in required_scenarios:
            assert scenario_name not in roadmap


def test_expected_sample_matrix_exists():
    use_cases = [
        "01-tutorials/hello-world",
        "01-tutorials/tool-calling",
        "01-tutorials/memory",
        "02-use-cases/knowledge-base-rag",
    ]
    frameworks = ["adk", "langgraph", "langchain", "deepagents"]
    for use_case in use_cases:
        for framework in frameworks:
            sample = ROOT / use_case / framework
            assert (sample / "README.md").is_file()
            assert (sample / "agent.py").is_file()
            assert (sample / "agentengine.yaml").is_file()
            assert (sample / "requirements.txt").is_file()


def test_langgraph_agentengine_toolsets_sample_exists_and_is_public_ready():
    sample = ROOT / "02-use-cases/agentengine-toolsets/langgraph"
    readme = (sample / "README.md").read_text(encoding="utf-8")
    source = (sample / "agent.py").read_text(encoding="utf-8")

    for required in (
        "环境准备",
        "本地运行",
        "Web UI 调试",
        "部署",
        "示例问题",
        "可选配置",
        "配置速查表",
        "Skill Space",
        "Skill Runtime",
        "Workspace",
        "Sandbox",
        "知识库",
        "长期记忆",
        "脱敏说明",
        "常见问题",
    ):
        assert required in readme

    for required in (
        "KSADK_SKILL_SPACE_IDS",
        "SKILL_SPACE_ID",
        "KSADK_PUBLIC_SKILL_SPACE_IDS",
        "KSADK_SKILL_SERVICE_URL",
        "KSADK_SKILL_SERVICE_ACCESS_KEY",
        "KSADK_SKILL_RUNTIME_BACKEND",
        "KSADK_SKILL_RUNTIME_AGENT_PATH",
        "KSADK_SKILL_RUNTIME_TEMPLATE_ID",
        "KSADK_SANDBOX_BACKEND",
        "KSADK_SANDBOX_TEMPLATE_ID",
        "KSADK_SANDBOX_TIMEOUT",
        "E2B_API_KEY",
        "KSADK_KB_DATASET_ID",
        "KSADK_KB_ENDPOINT",
        "KSADK_KB_TOP_K",
        "KSADK_LTM_BACKEND",
        "KSADK_LTM_NAMESPACE",
        "KSADK_LTM_HTTP_URL",
        "workspace_status",
        "agentengine_tool_dispatcher",
    ):
        assert required in readme

    for required in (
        "get_agentengine_tools",
        "describe_agentengine_tools",
        "resolve_skill_service_url",
        "_skill_space_ids",
        "agentengine_tool_dispatcher",
        "release_risk_matrix",
        "graph_status",
        "component_status",
        "missing_for_skill_space",
        "space_ids_configured",
        "list_skills",
        "search_skills",
        "load_skill",
    ):
        assert required in source

    assert not check_public_readiness.scan_file(sample / "README.md")
    assert not check_public_readiness.scan_file(sample / "agent.py")


def test_new_scenario_agents_invoke_with_demo_questions():
    scenario_questions = {
        "02-use-cases/deep-research/langgraph": "研究一下企业 Agent Runtime Platform 的选型维度。",
        "02-use-cases/coding-agent/langgraph": "这个函数偶尔返回空结果，帮我设计修复和测试。",
        "02-use-cases/browser-agent/langgraph": "帮我验证本地 Web UI 首页是否能展示调试入口。",
        "02-use-cases/data-analyst/langgraph": "分析这个月 Agent 调试功能的使用趋势。",
        "02-use-cases/customer-support/langgraph": "客户说 Web UI 启动后没有响应，帮我排查。",
        "02-use-cases/multi-agent-team/langgraph": "组织一个团队把 samples 仓库补齐。",
    }

    for relative_dir, question in scenario_questions.items():
        sample_dir = ROOT / relative_dir
        module_name = "sample_invoke_" + "_".join(sample_dir.relative_to(ROOT).parts)
        sys.path.insert(0, str(ROOT))
        sys.path.insert(0, str(sample_dir))
        try:
            spec = importlib.util.spec_from_file_location(module_name, sample_dir / "agent.py")
            assert spec is not None
            assert spec.loader is not None
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            state = module.ksadk_prepare_state({"input": question}, {})
            result = module.root_agent.invoke(state)
            answer = result.get("answer", "")
            assert "## 证据卡片" in answer
            assert "## 行动计划" in answer
            assert "工程说明" in answer
            assert (sample_dir / "demo.py").read_text(encoding="utf-8").count("root_agent.invoke") == 1
        finally:
            for value in (str(sample_dir), str(ROOT)):
                try:
                    sys.path.remove(value)
                except ValueError:
                    pass
            sys.modules.pop(module_name, None)
            for transient in ("workflow", "tools", "data", "prompts"):
                sys.modules.pop(transient, None)


def test_all_sample_readmes_are_actionable_for_new_users():
    required_sections = (
        "适用场景",
        "环境准备",
        "本地运行",
        "Web UI 调试",
        "部署",
        "示例问题",
        "常见问题",
    )
    for readme_path in ROOT.glob("0*/**/README.md"):
        text = readme_path.read_text(encoding="utf-8")
        first_line = text.splitlines()[0]
        assert any("\u4e00" <= character <= "\u9fff" for character in first_line), (
            f"{readme_path.relative_to(ROOT)} README title must be Chinese-first"
        )
        assert len(text.splitlines()) >= 35, f"{readme_path.relative_to(ROOT)} README is too short"
        for section in required_sections:
            assert section in text, f"{readme_path.relative_to(ROOT)} missing README section: {section}"


def test_sample_readmes_copy_env_template_into_sample_directory():
    for readme_path in ROOT.glob("0*/**/README.md"):
        text = readme_path.read_text(encoding="utf-8")
        assert "cp .env.example .env" not in text, (
            f"{readme_path.relative_to(ROOT)} should copy the root .env.example into the sample directory"
        )


def test_validate_samples_enforces_root_readme_gate(tmp_path):
    original_root = validate_samples.ROOT
    try:
        validate_samples.ROOT = tmp_path
        (tmp_path / "README.md").write_text("# Broken\n", encoding="utf-8")
        errors = validate_samples.validate_root_readme()
    finally:
        validate_samples.ROOT = original_root

    assert any("README.md missing required content" in error for error in errors)


def test_validate_samples_enforces_sample_readme_sections(tmp_path):
    sample_dir = tmp_path / "01-tutorials" / "broken" / "adk"
    sample_dir.mkdir(parents=True)
    (sample_dir / "README.md").write_text("# Broken\n", encoding="utf-8")

    errors = validate_samples.validate_sample_readme(sample_dir)

    assert "README title must be Chinese-first" in "\n".join(errors)
    assert "missing README section: 适用场景" in "\n".join(errors)


def test_validate_samples_scans_synthetic_private_endpoint(tmp_path):
    original_root = validate_samples.ROOT
    try:
        validate_samples.ROOT = tmp_path
        (tmp_path / "README.md").write_text(
            "endpoint=" + "service" + ".in" + "ternal" + ".example.com",
            encoding="utf-8",
        )
        errors = validate_samples.validate_public_safety()
    finally:
        validate_samples.ROOT = original_root

    assert any("matches forbidden pattern" in error for error in errors)


def test_public_readiness_scan_blocks_internal_domain_variants_and_low_level_headers(tmp_path):
    sample = tmp_path / "README.md"
    sample.write_text(
        "\n".join(
                [
                "endpoint=example." + "in" + "ternal",
                "header=" + chr(88) + "-Ksc-Account-Id",
            ]
        ),
        encoding="utf-8",
    )

    errors = check_public_readiness.scan_file(sample)

    assert len(errors) >= 2
    assert any("internal" in error.lower() for error in errors)
    assert any("X" in error or "K" in error for error in errors)


def test_agentengine_yaml_contracts_are_valid():
    for config_path in ROOT.glob("0*/**/agentengine.yaml"):
        config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
        assert config["framework"] in {"adk", "langgraph", "langchain", "deepagents"}
        assert config["entry_point"] == "agent.py"
        assert config["agent_variable"] == "root_agent"
        assert (config_path.parent / config["entry_point"]).is_file()


def test_all_samples_import_with_ksadk_0_6_2_runtime():
    os.environ.setdefault("OPENAI_API_KEY", "test-key")
    os.environ.setdefault("OPENAI_BASE_URL", "https://api.openai.com/v1")
    os.environ.setdefault("OPENAI_MODEL_NAME", "gpt-4o-mini")

    for config_path in ROOT.glob("0*/**/agentengine.yaml"):
        sample_dir = config_path.parent
        config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
        agent_path = sample_dir / config["entry_point"]
        module_name = "sample_import_" + "_".join(sample_dir.relative_to(ROOT).parts)
        sys.path.insert(0, str(ROOT))
        sys.path.insert(0, str(sample_dir))
        try:
            spec = importlib.util.spec_from_file_location(module_name, agent_path)
            assert spec is not None
            assert spec.loader is not None
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            assert hasattr(module, config["agent_variable"])
        finally:
            for path in (str(sample_dir), str(ROOT)):
                try:
                    sys.path.remove(path)
                except ValueError:
                    pass
            sys.modules.pop(module_name, None)
            for transient in ("workflow", "tools", "data", "prompts"):
                sys.modules.pop(transient, None)


def test_langgraph_toolsets_route_workspace_to_dispatcher_instead_of_skill_space():
    os.environ.setdefault("OPENAI_API_KEY", "test-key")
    os.environ.setdefault("OPENAI_MODEL_NAME", "gpt-4o-mini")

    sample_dir = ROOT / "02-use-cases" / "agentengine-toolsets" / "langgraph"
    agent_path = sample_dir / "agent.py"
    module_name = "sample_langgraph_toolsets_route_test"
    sys.path.insert(0, str(sample_dir))
    try:
        spec = importlib.util.spec_from_file_location(module_name, agent_path)
        assert spec is not None
        assert spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)

        route = module._route_for_text("请用 dispatcher 看看 Workspace 还有哪些可调用工具。")

        assert route["scenario"] == "ksadk_toolsets"
        assert route["suggested_tools"] == ["agentengine_tool_dispatcher"]
    finally:
        try:
            sys.path.remove(str(sample_dir))
        except ValueError:
            pass
        sys.modules.pop(module_name, None)
