from pathlib import Path
import importlib.util
import os
import sys

import yaml


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
        "agentengine_tool_dispatcher",
        "release_risk_matrix",
        "graph_status",
        "component_status",
    ):
        assert required in source

    combined = f"{readme}\n{source}"
    forbidden_fragments = (
        ".".join(("aicp", "inner", "api", "ksyun", "com")),
        ".".join(("mgr", "cn-beijing-6", "sandbox", "ksyun", "com")),
        ".".join(("100", "91", "6", "15")),
        "-".join(("7673e478", "277d", "4ebf", "")),
        "-".join(("15fd0bc7", "908a", "")),
        "AKLT" + "W9dW7YHYQ",
        "OHLW" + "iYdvCl1C",
        "-".join(("ab10091f", "ec89", "")),
    )
    for fragment in forbidden_fragments:
        assert fragment not in combined


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
        assert len(text.splitlines()) >= 35, f"{readme_path.relative_to(ROOT)} README is too short"
        for section in required_sections:
            assert section in text, f"{readme_path.relative_to(ROOT)} missing README section: {section}"


def test_agentengine_yaml_contracts_are_valid():
    for config_path in ROOT.glob("0*/**/agentengine.yaml"):
        config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
        assert config["framework"] in {"adk", "langgraph", "langchain", "deepagents"}
        assert config["entry_point"] == "agent.py"
        assert config["agent_variable"] == "root_agent"
        assert (config_path.parent / config["entry_point"]).is_file()


def test_all_samples_import_with_ksadk_0_6_2_runtime():
    os.environ.setdefault("OPENAI_API_KEY", "test-key")
    os.environ.setdefault("OPENAI_API_BASE", "https://api.openai.com/v1")
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
