from pathlib import Path
import importlib.util
import os
import subprocess
import sys

import yaml

from scripts import check_public_readiness
from scripts import validate_samples


ROOT = Path(__file__).resolve().parents[1]


def _clear_sample_module_cache() -> None:
    for transient in ("workflow", "tools", "data", "prompts"):
        sys.modules.pop(transient, None)


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
        "| 场景 | 样例 |",
        "| 目标 | 样例 |",
        "[LangGraph]",
        "[ADK]",
        "[DeepAgents]",
        "Deep Research Agent",
        "Coding Agent",
        "Browser Agent",
        "Data Analyst",
        "Customer Support",
        "Multi-Agent Team",
        "最佳实践案例",
        "Deep Research 报告生成",
        "Coding Workspace + Sandbox",
        "report-writer-adk",
        "report-writer-deepagents",
        "workspace-sandbox-adk",
        "workspace-sandbox-deepagents",
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


def test_root_readme_links_agent_sample_benchmark_notes():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    benchmark = (ROOT / "docs/agent-sample-benchmarks.md").read_text(encoding="utf-8")

    assert "docs/agent-sample-benchmarks.md" in readme
    for project_name in ("ADK Samples", "VEADK", "AgentKit", "DeerFlow", "SWE-agent", "OpenHands", "Aider"):
        assert project_name in benchmark
    for principle in ("能运行", "像工程", "中文优先", "有执行轨迹", "可替换真实能力", "有门禁"):
        assert principle in benchmark


def test_readme_links_real_webui_demo_assets():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    deep_research_readme = (ROOT / "02-use-cases/deep-research/langgraph/README.md").read_text(encoding="utf-8")
    gif_path = ROOT / "assets/screenshots/deep-research-webui-demo.gif"
    png_path = ROOT / "assets/screenshots/deep-research-webui-answer.png"

    assert "真实 Web UI 演示" in readme
    assert "assets/screenshots/deep-research-webui-demo.gif" in readme
    assert "../../../assets/screenshots/deep-research-webui-answer.png" in deep_research_readme
    assert gif_path.is_file()
    assert png_path.is_file()
    assert gif_path.stat().st_size < 1_000_000
    assert png_path.stat().st_size < 1_000_000


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


def test_scenario_agents_are_multi_file_projects_with_chinese_guidance():
    """场景 demo 要像可复制的 Agent 工程，而不是单文件脚本。"""

    scenario_dirs = (
        ROOT / "02-use-cases/deep-research/langgraph",
        ROOT / "02-use-cases/coding-agent/langgraph",
        ROOT / "02-use-cases/browser-agent/langgraph",
        ROOT / "02-use-cases/data-analyst/langgraph",
        ROOT / "02-use-cases/customer-support/langgraph",
        ROOT / "02-use-cases/multi-agent-team/langgraph",
    )
    required_files = ("agent.py", "workflow.py", "prompts.py", "data.py", "tools.py", "demo.py")

    def has_chinese_comment(text: str) -> bool:
        comment_lines = [
            line
            for line in text.splitlines()
            if line.strip().startswith("#") or line.strip().startswith('"""')
        ]
        return any(any("\u4e00" <= character <= "\u9fff" for character in line) for line in comment_lines)

    for sample_dir in scenario_dirs:
        readme = (sample_dir / "README.md").read_text(encoding="utf-8")
        assert "不是单文件脚本" in readme
        assert "工程结构" in readme

        for filename in required_files:
            source = (sample_dir / filename).read_text(encoding="utf-8")
            assert has_chinese_comment(source), (
                f"{sample_dir.relative_to(ROOT)}/{filename} should include Chinese guidance comments"
            )

        demo_source = (sample_dir / "demo.py").read_text(encoding="utf-8")
        assert "def " not in demo_source, f"{sample_dir.relative_to(ROOT)}/demo.py should stay as a thin runner"
        assert demo_source.count("root_agent.invoke") == 1


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
    env_example = (sample / ".env.example").read_text(encoding="utf-8")

    for required in (
        "环境准备",
        "开发者学习路径",
        "改造成你的业务 Agent",
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
        "E2B_API_URL",
        "E2B_API_KEY",
        "E2B_TEMPLATE_ID",
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
        "OPENAI_API_KEY=your-openai-compatible-api-key",
        "OPENAI_MODEL_NAME=gpt-4o-mini",
        "KSYUN_REGION=cn-beijing-6",
        "KSADK_SKILL_RUNTIME_BACKEND=disabled",
        "KSADK_SKILL_RUNTIME_AGENT_PATH=/absolute/path/to/skill-runtime-agent.py",
        "KSADK_SANDBOX_BACKEND=disabled",
        "KSADK_SANDBOX_TEMPLATE_ID=your-sandbox-template-id",
        "E2B_API_URL=https://mgr.cn-beijing-6.sandbox.ksyun.com",
        "E2B_API_KEY=your-e2b-api-key",
        "KSADK_KB_ENDPOINT=aicp.api.ksyun.com",
        "KSADK_LTM_BACKEND=",
    ):
        assert required in env_example

    assert "E2B_TEMPLATE_ID" not in env_example
    assert "KSADK_SKILL_RUNTIME_TEMPLATE_ID" not in env_example

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
        "_resolve_skill_runtime_status",
        "_resolve_sandbox_status",
        "template_required",
        "template_source",
        "ignored_env",
        "space_ids_configured",
        "list_skills",
        "search_skills",
        "load_skill",
    ):
        assert required in source

    assert not check_public_readiness.scan_file(sample / "README.md")
    assert not check_public_readiness.scan_file(sample / "agent.py")
    assert not check_public_readiness.scan_file(sample / ".env.example")


def test_long_task_resume_sample_exists_and_is_public_ready():
    sample = ROOT / "02-use-cases/long-task-resume/langgraph"
    required_files = (
        "README.md",
        ".env.example",
        "agent.py",
        "workflow.py",
        "tools.py",
        "demo.py",
        "smoke.py",
        "e2e_http.py",
        "tests/test_agent_behavior.py",
        "pg_smoke.py",
        "agentengine.yaml",
        "requirements.txt",
    )

    for filename in required_files:
        assert (sample / filename).is_file(), f"missing {filename}"

    readme = (sample / "README.md").read_text(encoding="utf-8")
    for required in (
        "适用场景",
        "环境准备",
        "本地运行",
        "Web UI 调试",
        "部署",
        "示例问题",
        "checkpoint 列表",
        "ResumeRun",
        "tool receipt",
        "CancelRun",
        "降级说明",
        "常见问题",
        "可选真实 PG smoke",
        "HTTP E2E 验收",
    ):
        assert required in readme

    env_example = (sample / ".env.example").read_text(encoding="utf-8")
    for required in (
        "KSADK_SESSION_BACKEND=postgres",
        "KSADK_SESSION_DSN=postgresql://<user>:<password>@<postgres-host>:5432/<database>",
        "KSADK_LANGGRAPH_CHECKPOINT_DSN=postgresql://<user>:<password>@<postgres-host>:5432/<database>",
        "KSADK_SESSION_NAMESPACE=long_task_resume_demo",
        "LONG_TASK_RESUME_DEMO_MODE=fixture",
        "LONG_TASK_STAGE_DELAY_SECONDS=6",
        "DEEPRESEARCH_WEB_SEARCH_URL=",
    ):
        assert required in env_example

    source = (sample / "agent.py").read_text(encoding="utf-8")
    for required in (
        "class LongTaskE2ERunner",
        "REPORT_STAGES",
        "_build_web_search_subgraph",
        "_build_analysis_subgraph",
        "graph.astream(",
        "graph.astream(\n                None,",
        "stream_mode=\"updates\"",
        "StateSnapshot",
        "checkpoint_resume",
        "run_checkpoint",
        "不要在普通聊天里声称已经创建 checkpoint",
    ):
        assert required in source

    pg_smoke = (sample / "pg_smoke.py").read_text(encoding="utf-8")
    for required in (
        "LONG_TASK_RESUME_DEMO_MODE",
        "postgres",
        "KSADK_SESSION_DSN",
        "long_task_resume_smoke",
        "CREATE TABLE IF NOT EXISTS",
    ):
        assert required in pg_smoke
    forbidden_values = (
        ".".join(("35", "37", "7", "168")),
        "Ksadk" + "@2026",
        "agent_" + "session_test",
    )
    for forbidden in forbidden_values:
        assert forbidden not in pg_smoke
        assert forbidden not in readme
        assert forbidden not in env_example

    leaked_runtime_artifacts = [
        path
        for path in sample.rglob("*")
        if ".agentengine" in path.parts or path.suffix == ".sqlite"
    ]
    assert leaked_runtime_artifacts == []

    smoke_result = subprocess.run(
        [sys.executable, "smoke.py"],
        cwd=sample,
        capture_output=True,
        text=True,
        check=True,
    )
    smoke_output = smoke_result.stdout
    for required in (
        "run_id",
        "checkpoint_id",
        "resume_attempt_id",
        "cancel_status",
        "duplicate_tool_count",
        "Deep Research",
        "检索公开网页",
        "交叉分析发现",
        "deepresearch-report.md",
    ):
        assert required in smoke_output

    for filename in required_files:
        assert not check_public_readiness.scan_file(sample / filename)


def test_long_task_resume_multi_framework_variants_exist_and_render_resume_sections():
    """Long Task Resume 作为横向 Runtime 能力，也要补齐多框架写法。"""

    for obsolete_dir in (
        "02-use-cases/long-task-resume-adk",
        "02-use-cases/long-task-resume-langchain",
        "02-use-cases/long-task-resume-deepagents",
    ):
        assert not (ROOT / obsolete_dir).exists(), f"{obsolete_dir} should be nested under long-task-resume/"

    os.environ.setdefault("OPENAI_API_KEY", "test-key")
    os.environ.setdefault("OPENAI_BASE_URL", "https://api.openai.com/v1")
    os.environ.setdefault("OPENAI_MODEL_NAME", "gpt-4o-mini")

    samples = {
        "02-use-cases/long-task-resume/langgraph": ("langgraph", True),
        "02-use-cases/long-task-resume/adk": ("adk", False),
        "02-use-cases/long-task-resume/langchain": ("langchain", False),
        "02-use-cases/long-task-resume/deepagents": ("deepagents", False),
    }
    required_sections = (
        "## checkpoint 列表",
        "## ResumeRun",
        "## tool receipt",
        "## CancelRun",
        "## 降级说明",
    )

    for relative_dir, (framework, has_workflow) in samples.items():
        sample_dir = ROOT / relative_dir
        required_files = ["README.md", ".env.example", "agent.py", "tools.py", "demo.py", "smoke.py", "agentengine.yaml", "requirements.txt"]
        if has_workflow:
            required_files.append("workflow.py")
        for filename in required_files:
            assert (sample_dir / filename).is_file(), f"{relative_dir} missing {filename}"

        config = yaml.safe_load((sample_dir / "agentengine.yaml").read_text(encoding="utf-8"))
        assert config["framework"] == framework
        readme = (sample_dir / "README.md").read_text(encoding="utf-8")
        assert "不是单文件脚本" in readme
        assert "checkpoint 列表" in readme

        module_name = "sample_long_task_resume_" + "_".join(sample_dir.relative_to(ROOT).parts)
        sys.path.insert(0, str(ROOT))
        sys.path.insert(0, str(sample_dir))
        try:
            _clear_sample_module_cache()
            spec = importlib.util.spec_from_file_location(module_name, sample_dir / "agent.py")
            assert spec is not None
            assert spec.loader is not None
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            assert hasattr(module, "root_agent")
            tools = importlib.import_module("tools")
            if framework == "langgraph":
                workflow = importlib.import_module("workflow")
                state = workflow.prepare_state(
                    {"input": "调研国产 AI Agent Runtime 的市场格局、竞品、落地风险和下一步建议。"},
                    {},
                )
                answer = workflow.build_agent_graph().invoke(state)["answer"]
            else:
                answer = tools.render_demo_answer("调研国产 AI Agent Runtime 的市场格局、竞品、落地风险和下一步建议。")
            for section in required_sections:
                assert section in answer
            for business_signal in (
                "Deep Research",
                "检索公开网页",
                "交叉分析发现",
                "deepresearch-report.md",
            ):
                assert business_signal in answer
        finally:
            for value in (str(sample_dir), str(ROOT)):
                try:
                    sys.path.remove(value)
                except ValueError:
                    pass
            sys.modules.pop(module_name, None)
            _clear_sample_module_cache()


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
            _clear_sample_module_cache()
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
            _clear_sample_module_cache()


def test_deep_research_and_coding_agents_show_mature_agent_workflows():
    """核心场景要体现成熟开源 Agent 的工程闭环，而不是只返回通用建议。"""

    expected_sections = {
        "02-use-cases/deep-research/langgraph": (
            "## 研究计划",
            "## 执行轨迹",
            "## 反思与补查",
            "## 交付物",
        ),
        "02-use-cases/coding-agent/langgraph": (
            "## 变更定位",
            "## 测试矩阵",
            "## 发布风险",
            "## 交付物",
        ),
    }

    for relative_dir, sections in expected_sections.items():
        sample_dir = ROOT / relative_dir
        module_name = "sample_workflow_quality_" + "_".join(sample_dir.relative_to(ROOT).parts)
        sys.path.insert(0, str(ROOT))
        sys.path.insert(0, str(sample_dir))
        try:
            spec = importlib.util.spec_from_file_location(module_name, sample_dir / "agent.py")
            assert spec is not None
            assert spec.loader is not None
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            state = module.ksadk_prepare_state({"input": "演示一个完整流程。"}, {})
            result = module.root_agent.invoke(state)
            answer = result.get("answer", "")
            for section in sections:
                assert section in answer
        finally:
            for value in (str(sample_dir), str(ROOT)):
                try:
                    sys.path.remove(value)
                except ValueError:
                    pass
            sys.modules.pop(module_name, None)
            for transient in ("workflow", "tools", "data", "prompts"):
                sys.modules.pop(transient, None)


def test_best_practice_agents_cover_next_completion_order():
    """补齐顺序里的最佳实践 demo 必须有可运行工程和清晰输出。"""

    os.environ.setdefault("OPENAI_API_KEY", "test-key")
    os.environ.setdefault("OPENAI_BASE_URL", "https://api.openai.com/v1")
    os.environ.setdefault("OPENAI_MODEL_NAME", "gpt-4o-mini")

    samples = {
        "02-use-cases/deep-research/report-writer-langgraph": (
            "langgraph",
            "生成一份 Agent Runtime Platform 选型报告。",
            ("## 报告大纲", "## 引用材料", "## 质量检查", "## 最终报告"),
        ),
        "02-use-cases/deep-research/report-writer-adk": (
            "adk",
            "生成一份 Agent Runtime Platform 选型报告。",
            ("## 报告大纲", "## 引用材料", "## 质量检查", "## 最终报告"),
        ),
        "02-use-cases/deep-research/report-writer-deepagents": (
            "deepagents",
            "生成一份 Agent Runtime Platform 选型报告。",
            ("## 报告大纲", "## 引用材料", "## 质量检查", "## 最终报告"),
        ),
        "02-use-cases/deep-research/report-writer-langchain": (
            "langchain",
            "生成一份 Agent Runtime Platform 选型报告。",
            ("## 报告大纲", "## 引用材料", "## 质量检查", "## 最终报告"),
        ),
        "02-use-cases/coding-agent/workspace-sandbox-langgraph": (
            "langgraph",
            "修复 Markdown 表格渲染不稳定的问题，并给出测试计划。",
            ("## 工作区文件", "## 沙箱命令", "## 补丁计划", "## 验证结果"),
        ),
        "02-use-cases/coding-agent/workspace-sandbox-adk": (
            "adk",
            "修复 Markdown 表格渲染不稳定的问题，并给出测试计划。",
            ("## 工作区文件", "## 沙箱命令", "## 补丁计划", "## 验证结果"),
        ),
        "02-use-cases/coding-agent/workspace-sandbox-deepagents": (
            "deepagents",
            "修复 Markdown 表格渲染不稳定的问题，并给出测试计划。",
            ("## 工作区文件", "## 沙箱命令", "## 补丁计划", "## 验证结果"),
        ),
        "02-use-cases/coding-agent/workspace-sandbox-langchain": (
            "langchain",
            "修复 Markdown 表格渲染不稳定的问题，并给出测试计划。",
            ("## 工作区文件", "## 沙箱命令", "## 补丁计划", "## 验证结果"),
        ),
        "02-use-cases/browser-agent/dom-diagnostics-langgraph": (
            "langgraph",
            "验证本地 Web UI 首页无法点击发送按钮的问题。",
            ("## 页面观察", "## DOM 线索", "## 失败诊断", "## 验证步骤"),
        ),
        "02-use-cases/browser-agent/dom-diagnostics-adk": (
            "adk",
            "验证本地 Web UI 首页无法点击发送按钮的问题。",
            ("## 页面观察", "## DOM 线索", "## 失败诊断", "## 验证步骤"),
        ),
        "02-use-cases/browser-agent/dom-diagnostics-deepagents": (
            "deepagents",
            "验证本地 Web UI 首页无法点击发送按钮的问题。",
            ("## 页面观察", "## DOM 线索", "## 失败诊断", "## 验证步骤"),
        ),
        "02-use-cases/browser-agent/dom-diagnostics-langchain": (
            "langchain",
            "验证本地 Web UI 首页无法点击发送按钮的问题。",
            ("## 页面观察", "## DOM 线索", "## 失败诊断", "## 验证步骤"),
        ),
        "02-use-cases/data-analyst/csv-insight-langgraph": (
            "langgraph",
            "分析 Agent 调试功能的激活率和留存变化。",
            ("## 数据样本", "## 指标口径", "## 洞察排序", "## 图表建议"),
        ),
        "02-use-cases/data-analyst/csv-insight-adk": (
            "adk",
            "分析 Agent 调试功能的激活率和留存变化。",
            ("## 数据样本", "## 指标口径", "## 洞察排序", "## 图表建议"),
        ),
        "02-use-cases/data-analyst/csv-insight-deepagents": (
            "deepagents",
            "分析 Agent 调试功能的激活率和留存变化。",
            ("## 数据样本", "## 指标口径", "## 洞察排序", "## 图表建议"),
        ),
        "02-use-cases/data-analyst/csv-insight-langchain": (
            "langchain",
            "分析 Agent 调试功能的激活率和留存变化。",
            ("## 数据样本", "## 指标口径", "## 洞察排序", "## 图表建议"),
        ),
        "02-use-cases/customer-support/ticket-triage-langgraph": (
            "langgraph",
            "客户说 Web UI 启动后没有响应，帮我排查。",
            ("## 工单摘要", "## 知识匹配", "## 处理步骤", "## 升级策略"),
        ),
        "02-use-cases/customer-support/ticket-triage-adk": (
            "adk",
            "客户说 Web UI 启动后没有响应，帮我排查。",
            ("## 工单摘要", "## 知识匹配", "## 处理步骤", "## 升级策略"),
        ),
        "02-use-cases/customer-support/ticket-triage-deepagents": (
            "deepagents",
            "客户说 Web UI 启动后没有响应，帮我排查。",
            ("## 工单摘要", "## 知识匹配", "## 处理步骤", "## 升级策略"),
        ),
        "02-use-cases/customer-support/ticket-triage-langchain": (
            "langchain",
            "客户说 Web UI 启动后没有响应，帮我排查。",
            ("## 工单摘要", "## 知识匹配", "## 处理步骤", "## 升级策略"),
        ),
        "02-use-cases/multi-agent-team/team-delivery-langgraph": (
            "langgraph",
            "组织一个团队把 samples 仓库补齐。",
            ("## 角色分工", "## 并行轨迹", "## 冲突合并", "## 验收清单"),
        ),
        "02-use-cases/multi-agent-team/team-delivery-adk": (
            "adk",
            "组织一个团队把 samples 仓库补齐。",
            ("## 角色分工", "## 并行轨迹", "## 冲突合并", "## 验收清单"),
        ),
        "02-use-cases/multi-agent-team/team-delivery-deepagents": (
            "deepagents",
            "组织一个团队把 samples 仓库补齐。",
            ("## 角色分工", "## 并行轨迹", "## 冲突合并", "## 验收清单"),
        ),
        "02-use-cases/multi-agent-team/team-delivery-langchain": (
            "langchain",
            "组织一个团队把 samples 仓库补齐。",
            ("## 角色分工", "## 并行轨迹", "## 冲突合并", "## 验收清单"),
        ),
        "02-use-cases/aiops/incident-triage-langgraph": (
            "langgraph",
            "分析支付服务 5xx 激增和延迟升高的告警。",
            ("## 告警摘要", "## 根因线索", "## 处置动作", "## 复盘事项"),
        ),
        "02-use-cases/aiops/incident-triage-adk": (
            "adk",
            "分析支付服务 5xx 激增和延迟升高的告警。",
            ("## 告警摘要", "## 根因线索", "## 处置动作", "## 复盘事项"),
        ),
        "02-use-cases/aiops/incident-triage-langchain": (
            "langchain",
            "分析支付服务 5xx 激增和延迟升高的告警。",
            ("## 告警摘要", "## 根因线索", "## 处置动作", "## 复盘事项"),
        ),
        "02-use-cases/aiops/incident-triage-deepagents": (
            "deepagents",
            "分析支付服务 5xx 激增和延迟升高的告警。",
            ("## 告警摘要", "## 根因线索", "## 处置动作", "## 复盘事项"),
        ),
        "02-use-cases/finance/report-review-langgraph": (
            "langgraph",
            "审阅本季度收入、毛利率和现金流风险。",
            ("## 报表摘录", "## 风险指标", "## 异常解释", "## 审阅结论"),
        ),
        "02-use-cases/finance/report-review-adk": (
            "adk",
            "审阅本季度收入、毛利率和现金流风险。",
            ("## 报表摘录", "## 风险指标", "## 异常解释", "## 审阅结论"),
        ),
        "02-use-cases/finance/report-review-langchain": (
            "langchain",
            "审阅本季度收入、毛利率和现金流风险。",
            ("## 报表摘录", "## 风险指标", "## 异常解释", "## 审阅结论"),
        ),
        "02-use-cases/finance/report-review-deepagents": (
            "deepagents",
            "审阅本季度收入、毛利率和现金流风险。",
            ("## 报表摘录", "## 风险指标", "## 异常解释", "## 审阅结论"),
        ),
        "02-use-cases/content-production/campaign-planner-langgraph": (
            "langgraph",
            "为 Agent Runtime Platform 设计一轮开源发布传播计划。",
            ("## 创意简报", "## 渠道计划", "## 内容草稿", "## 审核清单"),
        ),
        "02-use-cases/content-production/campaign-planner-adk": (
            "adk",
            "为 Agent Runtime Platform 设计一轮开源发布传播计划。",
            ("## 创意简报", "## 渠道计划", "## 内容草稿", "## 审核清单"),
        ),
        "02-use-cases/content-production/campaign-planner-langchain": (
            "langchain",
            "为 Agent Runtime Platform 设计一轮开源发布传播计划。",
            ("## 创意简报", "## 渠道计划", "## 内容草稿", "## 审核清单"),
        ),
        "02-use-cases/content-production/campaign-planner-deepagents": (
            "deepagents",
            "为 Agent Runtime Platform 设计一轮开源发布传播计划。",
            ("## 创意简报", "## 渠道计划", "## 内容草稿", "## 审核清单"),
        ),
        "02-use-cases/knowledge-operations/knowledge-curator-langgraph": (
            "langgraph",
            "整理一批用户反馈，把它转成可发布的知识库更新计划。",
            ("## 知识盘点", "## 缺口分析", "## 更新计划", "## 发布校验"),
        ),
        "02-use-cases/knowledge-operations/knowledge-curator-adk": (
            "adk",
            "整理一批用户反馈，把它转成可发布的知识库更新计划。",
            ("## 知识盘点", "## 缺口分析", "## 更新计划", "## 发布校验"),
        ),
        "02-use-cases/knowledge-operations/knowledge-curator-langchain": (
            "langchain",
            "整理一批用户反馈，把它转成可发布的知识库更新计划。",
            ("## 知识盘点", "## 缺口分析", "## 更新计划", "## 发布校验"),
        ),
        "02-use-cases/knowledge-operations/knowledge-curator-deepagents": (
            "deepagents",
            "整理一批用户反馈，把它转成可发布的知识库更新计划。",
            ("## 知识盘点", "## 缺口分析", "## 更新计划", "## 发布校验"),
        ),
        "02-use-cases/sales-operations/pipeline-copilot-langgraph": (
            "langgraph",
            "分析一组销售线索，给出下周跟进计划。",
            ("## 线索画像", "## 跟进策略", "## CRM 动作", "## 成交风险"),
        ),
        "02-use-cases/sales-operations/pipeline-copilot-adk": (
            "adk",
            "分析一组销售线索，给出下周跟进计划。",
            ("## 线索画像", "## 跟进策略", "## CRM 动作", "## 成交风险"),
        ),
        "02-use-cases/sales-operations/pipeline-copilot-langchain": (
            "langchain",
            "分析一组销售线索，给出下周跟进计划。",
            ("## 线索画像", "## 跟进策略", "## CRM 动作", "## 成交风险"),
        ),
        "02-use-cases/sales-operations/pipeline-copilot-deepagents": (
            "deepagents",
            "分析一组销售线索，给出下周跟进计划。",
            ("## 线索画像", "## 跟进策略", "## CRM 动作", "## 成交风险"),
        ),
        "02-use-cases/compliance-review/policy-review-langgraph": (
            "langgraph",
            "审阅一份对外发布材料，找出合规风险并给整改建议。",
            ("## 材料清单", "## 风险条款", "## 整改建议", "## 审阅记录"),
        ),
        "02-use-cases/compliance-review/policy-review-adk": (
            "adk",
            "审阅一份对外发布材料，找出合规风险并给整改建议。",
            ("## 材料清单", "## 风险条款", "## 整改建议", "## 审阅记录"),
        ),
        "02-use-cases/compliance-review/policy-review-langchain": (
            "langchain",
            "审阅一份对外发布材料，找出合规风险并给整改建议。",
            ("## 材料清单", "## 风险条款", "## 整改建议", "## 审阅记录"),
        ),
        "02-use-cases/compliance-review/policy-review-deepagents": (
            "deepagents",
            "审阅一份对外发布材料，找出合规风险并给整改建议。",
            ("## 材料清单", "## 风险条款", "## 整改建议", "## 审阅记录"),
        ),
        "02-use-cases/procurement-collaboration/vendor-selection-langgraph": (
            "langgraph",
            "为一批采购需求做供应商筛选和谈判计划。",
            ("## 采购需求", "## 供应商对比", "## 谈判计划", "## 审批风险"),
        ),
        "02-use-cases/procurement-collaboration/vendor-selection-adk": (
            "adk",
            "为一批采购需求做供应商筛选和谈判计划。",
            ("## 采购需求", "## 供应商对比", "## 谈判计划", "## 审批风险"),
        ),
        "02-use-cases/procurement-collaboration/vendor-selection-langchain": (
            "langchain",
            "为一批采购需求做供应商筛选和谈判计划。",
            ("## 采购需求", "## 供应商对比", "## 谈判计划", "## 审批风险"),
        ),
        "02-use-cases/procurement-collaboration/vendor-selection-deepagents": (
            "deepagents",
            "为一批采购需求做供应商筛选和谈判计划。",
            ("## 采购需求", "## 供应商对比", "## 谈判计划", "## 审批风险"),
        ),
        "02-use-cases/hr-recruiting/interview-planner-langgraph": (
            "langgraph",
            "根据岗位要求和候选人简历，生成面试计划。",
            ("## 岗位画像", "## 候选人匹配", "## 面试计划", "## 录用风险"),
        ),
        "02-use-cases/hr-recruiting/interview-planner-adk": (
            "adk",
            "根据岗位要求和候选人简历，生成面试计划。",
            ("## 岗位画像", "## 候选人匹配", "## 面试计划", "## 录用风险"),
        ),
        "02-use-cases/hr-recruiting/interview-planner-langchain": (
            "langchain",
            "根据岗位要求和候选人简历，生成面试计划。",
            ("## 岗位画像", "## 候选人匹配", "## 面试计划", "## 录用风险"),
        ),
        "02-use-cases/hr-recruiting/interview-planner-deepagents": (
            "deepagents",
            "根据岗位要求和候选人简历，生成面试计划。",
            ("## 岗位画像", "## 候选人匹配", "## 面试计划", "## 录用风险"),
        ),
        "02-use-cases/project-management/delivery-planner-langgraph": (
            "langgraph",
            "根据项目状态生成交付风险评估和推进计划。",
            ("## 项目状态", "## 风险雷达", "## 推进计划", "## 验收清单"),
        ),
        "02-use-cases/project-management/delivery-planner-adk": (
            "adk",
            "根据项目状态生成交付风险评估和推进计划。",
            ("## 项目状态", "## 风险雷达", "## 推进计划", "## 验收清单"),
        ),
        "02-use-cases/project-management/delivery-planner-langchain": (
            "langchain",
            "根据项目状态生成交付风险评估和推进计划。",
            ("## 项目状态", "## 风险雷达", "## 推进计划", "## 验收清单"),
        ),
        "02-use-cases/project-management/delivery-planner-deepagents": (
            "deepagents",
            "根据项目状态生成交付风险评估和推进计划。",
            ("## 项目状态", "## 风险雷达", "## 推进计划", "## 验收清单"),
        ),
        "02-use-cases/legal-contract/contract-negotiation-langgraph": (
            "langgraph",
            "审阅一份合作合同，提取关键条款和谈判建议。",
            ("## 合同摘要", "## 关键条款", "## 谈判建议", "## 法务风险"),
        ),
        "02-use-cases/legal-contract/contract-negotiation-adk": (
            "adk",
            "审阅一份合作合同，提取关键条款和谈判建议。",
            ("## 合同摘要", "## 关键条款", "## 谈判建议", "## 法务风险"),
        ),
        "02-use-cases/legal-contract/contract-negotiation-langchain": (
            "langchain",
            "审阅一份合作合同，提取关键条款和谈判建议。",
            ("## 合同摘要", "## 关键条款", "## 谈判建议", "## 法务风险"),
        ),
        "02-use-cases/legal-contract/contract-negotiation-deepagents": (
            "deepagents",
            "审阅一份合作合同，提取关键条款和谈判建议。",
            ("## 合同摘要", "## 关键条款", "## 谈判建议", "## 法务风险"),
        ),
        "02-use-cases/dev-productivity/engineering-efficiency-langgraph": (
            "langgraph",
            "分析研发团队迭代数据，给出效能改进计划。",
            ("## 研发概览", "## 瓶颈分析", "## 改进计划", "## 度量指标"),
        ),
        "02-use-cases/dev-productivity/engineering-efficiency-adk": (
            "adk",
            "分析研发团队迭代数据，给出效能改进计划。",
            ("## 研发概览", "## 瓶颈分析", "## 改进计划", "## 度量指标"),
        ),
        "02-use-cases/dev-productivity/engineering-efficiency-langchain": (
            "langchain",
            "分析研发团队迭代数据，给出效能改进计划。",
            ("## 研发概览", "## 瓶颈分析", "## 改进计划", "## 度量指标"),
        ),
        "02-use-cases/dev-productivity/engineering-efficiency-deepagents": (
            "deepagents",
            "分析研发团队迭代数据，给出效能改进计划。",
            ("## 研发概览", "## 瓶颈分析", "## 改进计划", "## 度量指标"),
        ),
        "02-use-cases/product-operations/experiment-review-langgraph": (
            "langgraph",
            "分析一组产品实验数据，给出运营优化计划。",
            ("## 实验概览", "## 用户分群", "## 优化动作", "## 复盘指标"),
        ),
        "02-use-cases/product-operations/experiment-review-adk": (
            "adk",
            "分析一组产品实验数据，给出运营优化计划。",
            ("## 实验概览", "## 用户分群", "## 优化动作", "## 复盘指标"),
        ),
        "02-use-cases/product-operations/experiment-review-langchain": (
            "langchain",
            "分析一组产品实验数据，给出运营优化计划。",
            ("## 实验概览", "## 用户分群", "## 优化动作", "## 复盘指标"),
        ),
        "02-use-cases/product-operations/experiment-review-deepagents": (
            "deepagents",
            "分析一组产品实验数据，给出运营优化计划。",
            ("## 实验概览", "## 用户分群", "## 优化动作", "## 复盘指标"),
        ),
        "02-use-cases/data-governance/quality-audit-langgraph": (
            "langgraph",
            "审计一批数据资产，生成质量问题和治理计划。",
            ("## 资产清单", "## 质量问题", "## 治理计划", "## 责任矩阵"),
        ),
        "02-use-cases/data-governance/quality-audit-adk": (
            "adk",
            "审计一批数据资产，生成质量问题和治理计划。",
            ("## 资产清单", "## 质量问题", "## 治理计划", "## 责任矩阵"),
        ),
        "02-use-cases/data-governance/quality-audit-langchain": (
            "langchain",
            "审计一批数据资产，生成质量问题和治理计划。",
            ("## 资产清单", "## 质量问题", "## 治理计划", "## 责任矩阵"),
        ),
        "02-use-cases/data-governance/quality-audit-deepagents": (
            "deepagents",
            "审计一批数据资产，生成质量问题和治理计划。",
            ("## 资产清单", "## 质量问题", "## 治理计划", "## 责任矩阵"),
        ),
        "02-use-cases/security-audit/threat-review-langgraph": (
            "langgraph",
            "审查一次安全变更，输出威胁分析和整改计划。",
            ("## 变更摘要", "## 威胁分析", "## 整改计划", "## 验证证据"),
        ),
        "02-use-cases/security-audit/threat-review-adk": (
            "adk",
            "审查一次安全变更，输出威胁分析和整改计划。",
            ("## 变更摘要", "## 威胁分析", "## 整改计划", "## 验证证据"),
        ),
        "02-use-cases/security-audit/threat-review-langchain": (
            "langchain",
            "审查一次安全变更，输出威胁分析和整改计划。",
            ("## 变更摘要", "## 威胁分析", "## 整改计划", "## 验证证据"),
        ),
        "02-use-cases/security-audit/threat-review-deepagents": (
            "deepagents",
            "审查一次安全变更，输出威胁分析和整改计划。",
            ("## 变更摘要", "## 威胁分析", "## 整改计划", "## 验证证据"),
        ),
        "02-use-cases/customer-success/health-review-langgraph": (
            "langgraph",
            "分析一组客户使用数据，给出客户成功行动计划。",
            ("## 客户健康", "## 风险信号", "## 成功计划", "## 跟进节奏"),
        ),
        "02-use-cases/customer-success/health-review-adk": (
            "adk",
            "分析一组客户使用数据，给出客户成功行动计划。",
            ("## 客户健康", "## 风险信号", "## 成功计划", "## 跟进节奏"),
        ),
        "02-use-cases/customer-success/health-review-langchain": (
            "langchain",
            "分析一组客户使用数据，给出客户成功行动计划。",
            ("## 客户健康", "## 风险信号", "## 成功计划", "## 跟进节奏"),
        ),
        "02-use-cases/customer-success/health-review-deepagents": (
            "deepagents",
            "分析一组客户使用数据，给出客户成功行动计划。",
            ("## 客户健康", "## 风险信号", "## 成功计划", "## 跟进节奏"),
        ),
        "02-use-cases/education-training/learning-coach-langgraph": (
            "langgraph",
            "根据学习目标和练习记录，生成培训辅导计划。",
            ("## 学习画像", "## 能力缺口", "## 训练计划", "## 评估方式"),
        ),
        "02-use-cases/education-training/learning-coach-adk": (
            "adk",
            "根据学习目标和练习记录，生成培训辅导计划。",
            ("## 学习画像", "## 能力缺口", "## 训练计划", "## 评估方式"),
        ),
        "02-use-cases/education-training/learning-coach-langchain": (
            "langchain",
            "根据学习目标和练习记录，生成培训辅导计划。",
            ("## 学习画像", "## 能力缺口", "## 训练计划", "## 评估方式"),
        ),
        "02-use-cases/education-training/learning-coach-deepagents": (
            "deepagents",
            "根据学习目标和练习记录，生成培训辅导计划。",
            ("## 学习画像", "## 能力缺口", "## 训练计划", "## 评估方式"),
        ),
        "02-use-cases/supply-chain-planning/demand-planner-langgraph": (
            "langgraph",
            "分析一批需求和库存数据，生成供应链计划。",
            ("## 需求预测", "## 库存风险", "## 调拨计划", "## 监控指标"),
        ),
        "02-use-cases/supply-chain-planning/demand-planner-adk": (
            "adk",
            "分析一批需求和库存数据，生成供应链计划。",
            ("## 需求预测", "## 库存风险", "## 调拨计划", "## 监控指标"),
        ),
        "02-use-cases/supply-chain-planning/demand-planner-langchain": (
            "langchain",
            "分析一批需求和库存数据，生成供应链计划。",
            ("## 需求预测", "## 库存风险", "## 调拨计划", "## 监控指标"),
        ),
        "02-use-cases/supply-chain-planning/demand-planner-deepagents": (
            "deepagents",
            "分析一批需求和库存数据，生成供应链计划。",
            ("## 需求预测", "## 库存风险", "## 调拨计划", "## 监控指标"),
        ),
        "02-use-cases/healthcare-operations/care-coordinator-langgraph": (
            "langgraph",
            "分析一组门诊运营数据，生成护理协同计划。",
            ("## 患者流转", "## 资源瓶颈", "## 协同计划", "## 风险提醒"),
        ),
        "02-use-cases/healthcare-operations/care-coordinator-adk": (
            "adk",
            "分析一组门诊运营数据，生成护理协同计划。",
            ("## 患者流转", "## 资源瓶颈", "## 协同计划", "## 风险提醒"),
        ),
        "02-use-cases/healthcare-operations/care-coordinator-langchain": (
            "langchain",
            "分析一组门诊运营数据，生成护理协同计划。",
            ("## 患者流转", "## 资源瓶颈", "## 协同计划", "## 风险提醒"),
        ),
        "02-use-cases/healthcare-operations/care-coordinator-deepagents": (
            "deepagents",
            "分析一组门诊运营数据，生成护理协同计划。",
            ("## 患者流转", "## 资源瓶颈", "## 协同计划", "## 风险提醒"),
        ),
        "02-use-cases/energy-dispatch/load-balancer-langgraph": (
            "langgraph",
            "根据负荷预测和设备状态，生成能源调度建议。",
            ("## 负荷预测", "## 设备状态", "## 调度策略", "## 安全边界"),
        ),
        "02-use-cases/energy-dispatch/load-balancer-adk": (
            "adk",
            "根据负荷预测和设备状态，生成能源调度建议。",
            ("## 负荷预测", "## 设备状态", "## 调度策略", "## 安全边界"),
        ),
        "02-use-cases/energy-dispatch/load-balancer-langchain": (
            "langchain",
            "根据负荷预测和设备状态，生成能源调度建议。",
            ("## 负荷预测", "## 设备状态", "## 调度策略", "## 安全边界"),
        ),
        "02-use-cases/energy-dispatch/load-balancer-deepagents": (
            "deepagents",
            "根据负荷预测和设备状态，生成能源调度建议。",
            ("## 负荷预测", "## 设备状态", "## 调度策略", "## 安全边界"),
        ),
        "02-use-cases/public-service/case-assistant-langgraph": (
            "langgraph",
            "整理一批政务服务事项，生成办事协同方案。",
            ("## 事项画像", "## 材料核验", "## 协同流程", "## 服务承诺"),
        ),
        "02-use-cases/public-service/case-assistant-adk": (
            "adk",
            "整理一批政务服务事项，生成办事协同方案。",
            ("## 事项画像", "## 材料核验", "## 协同流程", "## 服务承诺"),
        ),
        "02-use-cases/public-service/case-assistant-langchain": (
            "langchain",
            "整理一批政务服务事项，生成办事协同方案。",
            ("## 事项画像", "## 材料核验", "## 协同流程", "## 服务承诺"),
        ),
        "02-use-cases/public-service/case-assistant-deepagents": (
            "deepagents",
            "整理一批政务服务事项，生成办事协同方案。",
            ("## 事项画像", "## 材料核验", "## 协同流程", "## 服务承诺"),
        ),
        "02-use-cases/insurance-claims/claim-review-langgraph": (
            "langgraph",
            "分析一批理赔材料，生成理赔审核协同建议。",
            ("## 案件摘要", "## 材料核验", "## 审核建议", "## 风险控制"),
        ),
        "02-use-cases/insurance-claims/claim-review-adk": (
            "adk",
            "分析一批理赔材料，生成理赔审核协同建议。",
            ("## 案件摘要", "## 材料核验", "## 审核建议", "## 风险控制"),
        ),
        "02-use-cases/insurance-claims/claim-review-langchain": (
            "langchain",
            "分析一批理赔材料，生成理赔审核协同建议。",
            ("## 案件摘要", "## 材料核验", "## 审核建议", "## 风险控制"),
        ),
        "02-use-cases/insurance-claims/claim-review-deepagents": (
            "deepagents",
            "分析一批理赔材料，生成理赔审核协同建议。",
            ("## 案件摘要", "## 材料核验", "## 审核建议", "## 风险控制"),
        ),
        "02-use-cases/manufacturing-quality/defect-analysis-langgraph": (
            "langgraph",
            "分析一批产线质检数据，生成质量改进计划。",
            ("## 质量概览", "## 缺陷归因", "## 改进措施", "## 验证指标"),
        ),
        "02-use-cases/manufacturing-quality/defect-analysis-adk": (
            "adk",
            "分析一批产线质检数据，生成质量改进计划。",
            ("## 质量概览", "## 缺陷归因", "## 改进措施", "## 验证指标"),
        ),
        "02-use-cases/manufacturing-quality/defect-analysis-langchain": (
            "langchain",
            "分析一批产线质检数据，生成质量改进计划。",
            ("## 质量概览", "## 缺陷归因", "## 改进措施", "## 验证指标"),
        ),
        "02-use-cases/manufacturing-quality/defect-analysis-deepagents": (
            "deepagents",
            "分析一批产线质检数据，生成质量改进计划。",
            ("## 质量概览", "## 缺陷归因", "## 改进措施", "## 验证指标"),
        ),
        "02-use-cases/retail-operations/store-optimizer-langgraph": (
            "langgraph",
            "分析一组门店销售和库存数据，生成零售运营优化方案。",
            ("## 门店表现", "## 库存结构", "## 运营动作", "## 复盘指标"),
        ),
        "02-use-cases/retail-operations/store-optimizer-adk": (
            "adk",
            "分析一组门店销售和库存数据，生成零售运营优化方案。",
            ("## 门店表现", "## 库存结构", "## 运营动作", "## 复盘指标"),
        ),
        "02-use-cases/retail-operations/store-optimizer-langchain": (
            "langchain",
            "分析一组门店销售和库存数据，生成零售运营优化方案。",
            ("## 门店表现", "## 库存结构", "## 运营动作", "## 复盘指标"),
        ),
        "02-use-cases/retail-operations/store-optimizer-deepagents": (
            "deepagents",
            "分析一组门店销售和库存数据，生成零售运营优化方案。",
            ("## 门店表现", "## 库存结构", "## 运营动作", "## 复盘指标"),
        ),
        "02-use-cases/logistics-fulfillment/delivery-exception-langgraph": (
            "langgraph",
            "分析一批履约异常订单，生成物流协同处置方案。",
            ("## 履约异常", "## 配送资源", "## 客户承诺", "## 复盘指标"),
        ),
        "02-use-cases/logistics-fulfillment/delivery-exception-adk": (
            "adk",
            "分析一批履约异常订单，生成物流协同处置方案。",
            ("## 履约异常", "## 配送资源", "## 客户承诺", "## 复盘指标"),
        ),
        "02-use-cases/logistics-fulfillment/delivery-exception-langchain": (
            "langchain",
            "分析一批履约异常订单，生成物流协同处置方案。",
            ("## 履约异常", "## 配送资源", "## 客户承诺", "## 复盘指标"),
        ),
        "02-use-cases/logistics-fulfillment/delivery-exception-deepagents": (
            "deepagents",
            "分析一批履约异常订单，生成物流协同处置方案。",
            ("## 履约异常", "## 配送资源", "## 客户承诺", "## 复盘指标"),
        ),
        "02-use-cases/real-estate-operations/asset-service-langgraph": (
            "langgraph",
            "分析一批园区资产和租户服务数据，生成运营协同方案。",
            ("## 资产状态", "## 租户服务", "## 工单协同", "## 收益风险"),
        ),
        "02-use-cases/real-estate-operations/asset-service-adk": (
            "adk",
            "分析一批园区资产和租户服务数据，生成运营协同方案。",
            ("## 资产状态", "## 租户服务", "## 工单协同", "## 收益风险"),
        ),
        "02-use-cases/real-estate-operations/asset-service-langchain": (
            "langchain",
            "分析一批园区资产和租户服务数据，生成运营协同方案。",
            ("## 资产状态", "## 租户服务", "## 工单协同", "## 收益风险"),
        ),
        "02-use-cases/real-estate-operations/asset-service-deepagents": (
            "deepagents",
            "分析一批园区资产和租户服务数据，生成运营协同方案。",
            ("## 资产状态", "## 租户服务", "## 工单协同", "## 收益风险"),
        ),
        "02-use-cases/agriculture-production/crop-planner-langgraph": (
            "langgraph",
            "分析一组农业生产数据，生成农事生产计划。",
            ("## 种植计划", "## 环境数据", "## 农事任务", "## 产量预测"),
        ),
        "02-use-cases/agriculture-production/crop-planner-adk": (
            "adk",
            "分析一组农业生产数据，生成农事生产计划。",
            ("## 种植计划", "## 环境数据", "## 农事任务", "## 产量预测"),
        ),
        "02-use-cases/agriculture-production/crop-planner-langchain": (
            "langchain",
            "分析一组农业生产数据，生成农事生产计划。",
            ("## 种植计划", "## 环境数据", "## 农事任务", "## 产量预测"),
        ),
        "02-use-cases/agriculture-production/crop-planner-deepagents": (
            "deepagents",
            "分析一组农业生产数据，生成农事生产计划。",
            ("## 种植计划", "## 环境数据", "## 农事任务", "## 产量预测"),
        ),
        "02-use-cases/telecom-operations/network-change-langgraph": (
            "langgraph",
            "分析一次通信网络割接计划，生成运维协同方案。",
            ("## 网络告警", "## 容量分析", "## 割接计划", "## 客户影响"),
        ),
        "02-use-cases/telecom-operations/network-change-adk": (
            "adk",
            "分析一次通信网络割接计划，生成运维协同方案。",
            ("## 网络告警", "## 容量分析", "## 割接计划", "## 客户影响"),
        ),
        "02-use-cases/telecom-operations/network-change-langchain": (
            "langchain",
            "分析一次通信网络割接计划，生成运维协同方案。",
            ("## 网络告警", "## 容量分析", "## 割接计划", "## 客户影响"),
        ),
        "02-use-cases/telecom-operations/network-change-deepagents": (
            "deepagents",
            "分析一次通信网络割接计划，生成运维协同方案。",
            ("## 网络告警", "## 容量分析", "## 割接计划", "## 客户影响"),
        ),
        "02-use-cases/travel-service/trip-recovery-langgraph": (
            "langgraph",
            "分析一批行程变更事件，生成旅游服务恢复方案。",
            ("## 行程变更", "## 资源协调", "## 客户通知", "## 服务补偿"),
        ),
        "02-use-cases/travel-service/trip-recovery-adk": (
            "adk",
            "分析一批行程变更事件，生成旅游服务恢复方案。",
            ("## 行程变更", "## 资源协调", "## 客户通知", "## 服务补偿"),
        ),
        "02-use-cases/travel-service/trip-recovery-langchain": (
            "langchain",
            "分析一批行程变更事件，生成旅游服务恢复方案。",
            ("## 行程变更", "## 资源协调", "## 客户通知", "## 服务补偿"),
        ),
        "02-use-cases/travel-service/trip-recovery-deepagents": (
            "deepagents",
            "分析一批行程变更事件，生成旅游服务恢复方案。",
            ("## 行程变更", "## 资源协调", "## 客户通知", "## 服务补偿"),
        ),
        "02-use-cases/equipment-maintenance/maintenance-planner-langgraph": (
            "langgraph",
            "分析一组设备维护数据，生成维修协同计划。",
            ("## 设备状态", "## 备件计划", "## 维修任务", "## 停机风险"),
        ),
        "02-use-cases/equipment-maintenance/maintenance-planner-adk": (
            "adk",
            "分析一组设备维护数据，生成维修协同计划。",
            ("## 设备状态", "## 备件计划", "## 维修任务", "## 停机风险"),
        ),
        "02-use-cases/equipment-maintenance/maintenance-planner-langchain": (
            "langchain",
            "分析一组设备维护数据，生成维修协同计划。",
            ("## 设备状态", "## 备件计划", "## 维修任务", "## 停机风险"),
        ),
        "02-use-cases/equipment-maintenance/maintenance-planner-deepagents": (
            "deepagents",
            "分析一组设备维护数据，生成维修协同计划。",
            ("## 设备状态", "## 备件计划", "## 维修任务", "## 停机风险"),
        ),
        "02-use-cases/media-operations/content-distribution-langgraph": (
            "langgraph",
            "分析一组媒体运营数据，生成内容分发协同方案。",
            ("## 内容排期", "## 热点监测", "## 版权风险", "## 多渠道发布"),
        ),
        "02-use-cases/media-operations/content-distribution-adk": (
            "adk",
            "分析一组媒体运营数据，生成内容分发协同方案。",
            ("## 内容排期", "## 热点监测", "## 版权风险", "## 多渠道发布"),
        ),
        "02-use-cases/media-operations/content-distribution-langchain": (
            "langchain",
            "分析一组媒体运营数据，生成内容分发协同方案。",
            ("## 内容排期", "## 热点监测", "## 版权风险", "## 多渠道发布"),
        ),
        "02-use-cases/media-operations/content-distribution-deepagents": (
            "deepagents",
            "分析一组媒体运营数据，生成内容分发协同方案。",
            ("## 内容排期", "## 热点监测", "## 版权风险", "## 多渠道发布"),
        ),
        "02-use-cases/financial-risk/risk-alert-langgraph": (
            "langgraph",
            "分析一批金融风控信号，生成风险处置方案。",
            ("## 交易异常", "## 风险规则", "## 人工复核", "## 审计留痕"),
        ),
        "02-use-cases/financial-risk/risk-alert-adk": (
            "adk",
            "分析一批金融风控信号，生成风险处置方案。",
            ("## 交易异常", "## 风险规则", "## 人工复核", "## 审计留痕"),
        ),
        "02-use-cases/financial-risk/risk-alert-langchain": (
            "langchain",
            "分析一批金融风控信号，生成风险处置方案。",
            ("## 交易异常", "## 风险规则", "## 人工复核", "## 审计留痕"),
        ),
        "02-use-cases/financial-risk/risk-alert-deepagents": (
            "deepagents",
            "分析一批金融风控信号，生成风险处置方案。",
            ("## 交易异常", "## 风险规则", "## 人工复核", "## 审计留痕"),
        ),
        "02-use-cases/urban-mobility/traffic-response-langgraph": (
            "langgraph",
            "分析一组城市交通事件，生成出行协同响应方案。",
            ("## 道路拥堵", "## 运力调度", "## 事件响应", "## 公众通知"),
        ),
        "02-use-cases/urban-mobility/traffic-response-adk": (
            "adk",
            "分析一组城市交通事件，生成出行协同响应方案。",
            ("## 道路拥堵", "## 运力调度", "## 事件响应", "## 公众通知"),
        ),
        "02-use-cases/urban-mobility/traffic-response-langchain": (
            "langchain",
            "分析一组城市交通事件，生成出行协同响应方案。",
            ("## 道路拥堵", "## 运力调度", "## 事件响应", "## 公众通知"),
        ),
        "02-use-cases/urban-mobility/traffic-response-deepagents": (
            "deepagents",
            "分析一组城市交通事件，生成出行协同响应方案。",
            ("## 道路拥堵", "## 运力调度", "## 事件响应", "## 公众通知"),
        ),
        "02-use-cases/real-estate-marketing/lead-conversion-langgraph": (
            "langgraph",
            "分析一批楼盘营销线索，生成转化协同方案。",
            ("## 楼盘线索", "## 渠道投放", "## 内容审核", "## 转化复盘"),
        ),
        "02-use-cases/real-estate-marketing/lead-conversion-adk": (
            "adk",
            "分析一批楼盘营销线索，生成转化协同方案。",
            ("## 楼盘线索", "## 渠道投放", "## 内容审核", "## 转化复盘"),
        ),
        "02-use-cases/real-estate-marketing/lead-conversion-langchain": (
            "langchain",
            "分析一批楼盘营销线索，生成转化协同方案。",
            ("## 楼盘线索", "## 渠道投放", "## 内容审核", "## 转化复盘"),
        ),
        "02-use-cases/real-estate-marketing/lead-conversion-deepagents": (
            "deepagents",
            "分析一批楼盘营销线索，生成转化协同方案。",
            ("## 楼盘线索", "## 渠道投放", "## 内容审核", "## 转化复盘"),
        ),
        "02-use-cases/public-safety/incident-coordination-langgraph": (
            "langgraph",
            "分析一批公共安全事件线索，生成联动处置方案。",
            ("## 事件线索", "## 资源联动", "## 风险通报", "## 处置复盘"),
        ),
        "02-use-cases/public-safety/incident-coordination-adk": (
            "adk",
            "分析一批公共安全事件线索，生成联动处置方案。",
            ("## 事件线索", "## 资源联动", "## 风险通报", "## 处置复盘"),
        ),
        "02-use-cases/public-safety/incident-coordination-langchain": (
            "langchain",
            "分析一批公共安全事件线索，生成联动处置方案。",
            ("## 事件线索", "## 资源联动", "## 风险通报", "## 处置复盘"),
        ),
        "02-use-cases/public-safety/incident-coordination-deepagents": (
            "deepagents",
            "分析一批公共安全事件线索，生成联动处置方案。",
            ("## 事件线索", "## 资源联动", "## 风险通报", "## 处置复盘"),
        ),
        "02-use-cases/industrial-inspection/safety-patrol-langgraph": (
            "langgraph",
            "分析一组工业巡检记录，生成安全复核方案。",
            ("## 巡检任务", "## 缺陷识别", "## 维修联动", "## 安全复核"),
        ),
        "02-use-cases/industrial-inspection/safety-patrol-adk": (
            "adk",
            "分析一组工业巡检记录，生成安全复核方案。",
            ("## 巡检任务", "## 缺陷识别", "## 维修联动", "## 安全复核"),
        ),
        "02-use-cases/industrial-inspection/safety-patrol-langchain": (
            "langchain",
            "分析一组工业巡检记录，生成安全复核方案。",
            ("## 巡检任务", "## 缺陷识别", "## 维修联动", "## 安全复核"),
        ),
        "02-use-cases/industrial-inspection/safety-patrol-deepagents": (
            "deepagents",
            "分析一组工业巡检记录，生成安全复核方案。",
            ("## 巡检任务", "## 缺陷识别", "## 维修联动", "## 安全复核"),
        ),
        "02-use-cases/environmental-monitoring/pollution-response-langgraph": (
            "langgraph",
            "分析一组环境监测数据，生成污染响应方案。",
            ("## 监测点位", "## 污染线索", "## 处置联动", "## 公众披露"),
        ),
        "02-use-cases/environmental-monitoring/pollution-response-adk": (
            "adk",
            "分析一组环境监测数据，生成污染响应方案。",
            ("## 监测点位", "## 污染线索", "## 处置联动", "## 公众披露"),
        ),
        "02-use-cases/environmental-monitoring/pollution-response-langchain": (
            "langchain",
            "分析一组环境监测数据，生成污染响应方案。",
            ("## 监测点位", "## 污染线索", "## 处置联动", "## 公众披露"),
        ),
        "02-use-cases/environmental-monitoring/pollution-response-deepagents": (
            "deepagents",
            "分析一组环境监测数据，生成污染响应方案。",
            ("## 监测点位", "## 污染线索", "## 处置联动", "## 公众披露"),
        ),
        "02-use-cases/restaurant-operations/store-ops-langgraph": (
            "langgraph",
            "分析一组餐饮门店运营数据，生成门店协同方案。",
            ("## 门店排班", "## 食安巡检", "## 库存损耗", "## 顾客反馈"),
        ),
        "02-use-cases/restaurant-operations/store-ops-adk": (
            "adk",
            "分析一组餐饮门店运营数据，生成门店协同方案。",
            ("## 门店排班", "## 食安巡检", "## 库存损耗", "## 顾客反馈"),
        ),
        "02-use-cases/restaurant-operations/store-ops-langchain": (
            "langchain",
            "分析一组餐饮门店运营数据，生成门店协同方案。",
            ("## 门店排班", "## 食安巡检", "## 库存损耗", "## 顾客反馈"),
        ),
        "02-use-cases/restaurant-operations/store-ops-deepagents": (
            "deepagents",
            "分析一组餐饮门店运营数据，生成门店协同方案。",
            ("## 门店排班", "## 食安巡检", "## 库存损耗", "## 顾客反馈"),
        ),
        "02-use-cases/game-operations/liveops-review-langgraph": (
            "langgraph",
            "分析一组游戏运营数据，生成版本复盘方案。",
            ("## 玩家反馈", "## 活动配置", "## 经济系统监控", "## 版本复盘"),
        ),
        "02-use-cases/game-operations/liveops-review-adk": (
            "adk",
            "分析一组游戏运营数据，生成版本复盘方案。",
            ("## 玩家反馈", "## 活动配置", "## 经济系统监控", "## 版本复盘"),
        ),
        "02-use-cases/game-operations/liveops-review-langchain": (
            "langchain",
            "分析一组游戏运营数据，生成版本复盘方案。",
            ("## 玩家反馈", "## 活动配置", "## 经济系统监控", "## 版本复盘"),
        ),
        "02-use-cases/game-operations/liveops-review-deepagents": (
            "deepagents",
            "分析一组游戏运营数据，生成版本复盘方案。",
            ("## 玩家反馈", "## 活动配置", "## 经济系统监控", "## 版本复盘"),
        ),
        "02-use-cases/advertising-operations/campaign-optimization-langgraph": (
            "langgraph",
            "分析一组广告投放数据，生成投放优化方案。",
            ("## 投放目标", "## 素材审核", "## 预算节奏", "## 效果复盘"),
        ),
        "02-use-cases/advertising-operations/campaign-optimization-adk": (
            "adk",
            "分析一组广告投放数据，生成投放优化方案。",
            ("## 投放目标", "## 素材审核", "## 预算节奏", "## 效果复盘"),
        ),
        "02-use-cases/advertising-operations/campaign-optimization-langchain": (
            "langchain",
            "分析一组广告投放数据，生成投放优化方案。",
            ("## 投放目标", "## 素材审核", "## 预算节奏", "## 效果复盘"),
        ),
        "02-use-cases/advertising-operations/campaign-optimization-deepagents": (
            "deepagents",
            "分析一组广告投放数据，生成投放优化方案。",
            ("## 投放目标", "## 素材审核", "## 预算节奏", "## 效果复盘"),
        ),
        "02-use-cases/community-operations/community-growth-langgraph": (
            "langgraph",
            "分析一组社群运营数据，生成社群增长方案。",
            ("## 社群画像", "## 内容日历", "## 互动风险", "## 转化复盘"),
        ),
        "02-use-cases/community-operations/community-growth-adk": (
            "adk",
            "分析一组社群运营数据，生成社群增长方案。",
            ("## 社群画像", "## 内容日历", "## 互动风险", "## 转化复盘"),
        ),
        "02-use-cases/community-operations/community-growth-langchain": (
            "langchain",
            "分析一组社群运营数据，生成社群增长方案。",
            ("## 社群画像", "## 内容日历", "## 互动风险", "## 转化复盘"),
        ),
        "02-use-cases/community-operations/community-growth-deepagents": (
            "deepagents",
            "分析一组社群运营数据，生成社群增长方案。",
            ("## 社群画像", "## 内容日历", "## 互动风险", "## 转化复盘"),
        ),
        "02-use-cases/customer-qa/service-quality-langgraph": (
            "langgraph",
            "分析一批客服质检样本，生成服务质量改进方案。",
            ("## 质检样本", "## 规则命中", "## 改进建议", "## 培训闭环"),
        ),
        "02-use-cases/customer-qa/service-quality-adk": (
            "adk",
            "分析一批客服质检样本，生成服务质量改进方案。",
            ("## 质检样本", "## 规则命中", "## 改进建议", "## 培训闭环"),
        ),
        "02-use-cases/customer-qa/service-quality-langchain": (
            "langchain",
            "分析一批客服质检样本，生成服务质量改进方案。",
            ("## 质检样本", "## 规则命中", "## 改进建议", "## 培训闭环"),
        ),
        "02-use-cases/customer-qa/service-quality-deepagents": (
            "deepagents",
            "分析一批客服质检样本，生成服务质量改进方案。",
            ("## 质检样本", "## 规则命中", "## 改进建议", "## 培训闭环"),
        ),
        "02-use-cases/store-service/store-advisor-langgraph": (
            "langgraph",
            "分析一组门店咨询记录，生成门店服务改进方案。",
            ("## 门店咨询", "## 服务承诺", "## 问题升级", "## 体验复盘"),
        ),
        "02-use-cases/store-service/store-advisor-adk": (
            "adk",
            "分析一组门店咨询记录，生成门店服务改进方案。",
            ("## 门店咨询", "## 服务承诺", "## 问题升级", "## 体验复盘"),
        ),
        "02-use-cases/store-service/store-advisor-langchain": (
            "langchain",
            "分析一组门店咨询记录，生成门店服务改进方案。",
            ("## 门店咨询", "## 服务承诺", "## 问题升级", "## 体验复盘"),
        ),
        "02-use-cases/store-service/store-advisor-deepagents": (
            "deepagents",
            "分析一组门店咨询记录，生成门店服务改进方案。",
            ("## 门店咨询", "## 服务承诺", "## 问题升级", "## 体验复盘"),
        ),
        "02-use-cases/after-sales-service/repair-coordinator-langgraph": (
            "langgraph",
            "分析一批售后工单，生成售后服务协同方案。",
            ("## 售后工单", "## 备件协同", "## 服务时效", "## 客户回访"),
        ),
        "02-use-cases/after-sales-service/repair-coordinator-adk": (
            "adk",
            "分析一批售后工单，生成售后服务协同方案。",
            ("## 售后工单", "## 备件协同", "## 服务时效", "## 客户回访"),
        ),
        "02-use-cases/after-sales-service/repair-coordinator-langchain": (
            "langchain",
            "分析一批售后工单，生成售后服务协同方案。",
            ("## 售后工单", "## 备件协同", "## 服务时效", "## 客户回访"),
        ),
        "02-use-cases/after-sales-service/repair-coordinator-deepagents": (
            "deepagents",
            "分析一批售后工单，生成售后服务协同方案。",
            ("## 售后工单", "## 备件协同", "## 服务时效", "## 客户回访"),
        ),
        "02-use-cases/content-safety/moderation-review-langgraph": (
            "langgraph",
            "分析一批内容安全样本，生成审核处置方案。",
            ("## 内容样本", "## 规则命中", "## 人工复核", "## 风险处置"),
        ),
        "02-use-cases/content-safety/moderation-review-adk": (
            "adk",
            "分析一批内容安全样本，生成审核处置方案。",
            ("## 内容样本", "## 规则命中", "## 人工复核", "## 风险处置"),
        ),
        "02-use-cases/content-safety/moderation-review-langchain": (
            "langchain",
            "分析一批内容安全样本，生成审核处置方案。",
            ("## 内容样本", "## 规则命中", "## 人工复核", "## 风险处置"),
        ),
        "02-use-cases/content-safety/moderation-review-deepagents": (
            "deepagents",
            "分析一批内容安全样本，生成审核处置方案。",
            ("## 内容样本", "## 规则命中", "## 人工复核", "## 风险处置"),
        ),
        "02-use-cases/live-commerce-operations/session-control-langgraph": (
            "langgraph",
            "分析一场直播运营数据，生成直播场控复盘方案。",
            ("## 直播场控", "## 商品讲解", "## 异常舆情", "## 转化复盘"),
        ),
        "02-use-cases/live-commerce-operations/session-control-adk": (
            "adk",
            "分析一场直播运营数据，生成直播场控复盘方案。",
            ("## 直播场控", "## 商品讲解", "## 异常舆情", "## 转化复盘"),
        ),
        "02-use-cases/live-commerce-operations/session-control-langchain": (
            "langchain",
            "分析一场直播运营数据，生成直播场控复盘方案。",
            ("## 直播场控", "## 商品讲解", "## 异常舆情", "## 转化复盘"),
        ),
        "02-use-cases/live-commerce-operations/session-control-deepagents": (
            "deepagents",
            "分析一场直播运营数据，生成直播场控复盘方案。",
            ("## 直播场控", "## 商品讲解", "## 异常舆情", "## 转化复盘"),
        ),
        "02-use-cases/membership-growth/member-lifecycle-langgraph": (
            "langgraph",
            "分析一组会员运营数据，生成会员增长方案。",
            ("## 会员分层", "## 权益推荐", "## 触达节奏", "## 留存复盘"),
        ),
        "02-use-cases/membership-growth/member-lifecycle-adk": (
            "adk",
            "分析一组会员运营数据，生成会员增长方案。",
            ("## 会员分层", "## 权益推荐", "## 触达节奏", "## 留存复盘"),
        ),
        "02-use-cases/membership-growth/member-lifecycle-langchain": (
            "langchain",
            "分析一组会员运营数据，生成会员增长方案。",
            ("## 会员分层", "## 权益推荐", "## 触达节奏", "## 留存复盘"),
        ),
        "02-use-cases/membership-growth/member-lifecycle-deepagents": (
            "deepagents",
            "分析一组会员运营数据，生成会员增长方案。",
            ("## 会员分层", "## 权益推荐", "## 触达节奏", "## 留存复盘"),
        ),
        "02-use-cases/search-recommendation/relevance-diagnostics-langgraph": (
            "langgraph",
            "分析一批搜索推荐样本，生成相关性诊断方案。",
            ("## 查询意图", "## 召回质量", "## 排序诊断", "## 反馈闭环"),
        ),
        "02-use-cases/search-recommendation/relevance-diagnostics-adk": (
            "adk",
            "分析一批搜索推荐样本，生成相关性诊断方案。",
            ("## 查询意图", "## 召回质量", "## 排序诊断", "## 反馈闭环"),
        ),
        "02-use-cases/search-recommendation/relevance-diagnostics-langchain": (
            "langchain",
            "分析一批搜索推荐样本，生成相关性诊断方案。",
            ("## 查询意图", "## 召回质量", "## 排序诊断", "## 反馈闭环"),
        ),
        "02-use-cases/search-recommendation/relevance-diagnostics-deepagents": (
            "deepagents",
            "分析一批搜索推荐样本，生成相关性诊断方案。",
            ("## 查询意图", "## 召回质量", "## 排序诊断", "## 反馈闭环"),
        ),
        "02-use-cases/payment-risk/payment-guard-langgraph": (
            "langgraph",
            "分析一批支付异常样本，生成支付风控处置方案。",
            ("## 支付异常", "## 风控规则", "## 人工复核", "## 审计留痕"),
        ),
        "02-use-cases/payment-risk/payment-guard-adk": (
            "adk",
            "分析一批支付异常样本，生成支付风控处置方案。",
            ("## 支付异常", "## 风控规则", "## 人工复核", "## 审计留痕"),
        ),
        "02-use-cases/payment-risk/payment-guard-langchain": (
            "langchain",
            "分析一批支付异常样本，生成支付风控处置方案。",
            ("## 支付异常", "## 风控规则", "## 人工复核", "## 审计留痕"),
        ),
        "02-use-cases/payment-risk/payment-guard-deepagents": (
            "deepagents",
            "分析一批支付异常样本，生成支付风控处置方案。",
            ("## 支付异常", "## 风控规则", "## 人工复核", "## 审计留痕"),
        ),
        "02-use-cases/shopping-assistant/product-advisor-langgraph": (
            "langgraph",
            "分析一组导购咨询样本，生成智能导购方案。",
            ("## 需求澄清", "## 商品对比", "## 库存价格", "## 导购转化"),
        ),
        "02-use-cases/shopping-assistant/product-advisor-adk": (
            "adk",
            "分析一组导购咨询样本，生成智能导购方案。",
            ("## 需求澄清", "## 商品对比", "## 库存价格", "## 导购转化"),
        ),
        "02-use-cases/shopping-assistant/product-advisor-langchain": (
            "langchain",
            "分析一组导购咨询样本，生成智能导购方案。",
            ("## 需求澄清", "## 商品对比", "## 库存价格", "## 导购转化"),
        ),
        "02-use-cases/shopping-assistant/product-advisor-deepagents": (
            "deepagents",
            "分析一组导购咨询样本，生成智能导购方案。",
            ("## 需求澄清", "## 商品对比", "## 库存价格", "## 导购转化"),
        ),
        "02-use-cases/devrel-operations/community-program-langgraph": (
            "langgraph",
            "分析一组开发者运营反馈，生成 DevRel 运营方案。",
            ("## 开发者反馈", "## 内容运营", "## 活动节奏", "## 社区复盘"),
        ),
        "02-use-cases/devrel-operations/community-program-adk": (
            "adk",
            "分析一组开发者运营反馈，生成 DevRel 运营方案。",
            ("## 开发者反馈", "## 内容运营", "## 活动节奏", "## 社区复盘"),
        ),
        "02-use-cases/devrel-operations/community-program-langchain": (
            "langchain",
            "分析一组开发者运营反馈，生成 DevRel 运营方案。",
            ("## 开发者反馈", "## 内容运营", "## 活动节奏", "## 社区复盘"),
        ),
        "02-use-cases/devrel-operations/community-program-deepagents": (
            "deepagents",
            "分析一组开发者运营反馈，生成 DevRel 运营方案。",
            ("## 开发者反馈", "## 内容运营", "## 活动节奏", "## 社区复盘"),
        ),
        "02-use-cases/brand-reputation/reputation-response-langgraph": (
            "langgraph",
            "分析一组品牌舆情线索，生成品牌回应复盘方案。",
            ("## 舆情线索", "## 传播路径", "## 回应策略", "## 品牌复盘"),
        ),
        "02-use-cases/brand-reputation/reputation-response-adk": (
            "adk",
            "分析一组品牌舆情线索，生成品牌回应复盘方案。",
            ("## 舆情线索", "## 传播路径", "## 回应策略", "## 品牌复盘"),
        ),
        "02-use-cases/brand-reputation/reputation-response-langchain": (
            "langchain",
            "分析一组品牌舆情线索，生成品牌回应复盘方案。",
            ("## 舆情线索", "## 传播路径", "## 回应策略", "## 品牌复盘"),
        ),
        "02-use-cases/brand-reputation/reputation-response-deepagents": (
            "deepagents",
            "分析一组品牌舆情线索，生成品牌回应复盘方案。",
            ("## 舆情线索", "## 传播路径", "## 回应策略", "## 品牌复盘"),
        ),
        "02-use-cases/channel-operations/channel-health-langgraph": (
            "langgraph",
            "分析一组渠道运营数据，生成渠道经营复盘方案。",
            ("## 渠道表现", "## 库存协同", "## 价格治理", "## 经营复盘"),
        ),
        "02-use-cases/channel-operations/channel-health-adk": (
            "adk",
            "分析一组渠道运营数据，生成渠道经营复盘方案。",
            ("## 渠道表现", "## 库存协同", "## 价格治理", "## 经营复盘"),
        ),
        "02-use-cases/channel-operations/channel-health-langchain": (
            "langchain",
            "分析一组渠道运营数据，生成渠道经营复盘方案。",
            ("## 渠道表现", "## 库存协同", "## 价格治理", "## 经营复盘"),
        ),
        "02-use-cases/channel-operations/channel-health-deepagents": (
            "deepagents",
            "分析一组渠道运营数据，生成渠道经营复盘方案。",
            ("## 渠道表现", "## 库存协同", "## 价格治理", "## 经营复盘"),
        ),
        "02-use-cases/enterprise-training/training-planner-langgraph": (
            "langgraph",
            "分析一组企业培训需求，生成培训计划复盘方案。",
            ("## 培训对象", "## 课程设计", "## 练习评估", "## 学习复盘"),
        ),
        "02-use-cases/enterprise-training/training-planner-adk": (
            "adk",
            "分析一组企业培训需求，生成培训计划复盘方案。",
            ("## 培训对象", "## 课程设计", "## 练习评估", "## 学习复盘"),
        ),
        "02-use-cases/enterprise-training/training-planner-langchain": (
            "langchain",
            "分析一组企业培训需求，生成培训计划复盘方案。",
            ("## 培训对象", "## 课程设计", "## 练习评估", "## 学习复盘"),
        ),
        "02-use-cases/enterprise-training/training-planner-deepagents": (
            "deepagents",
            "分析一组企业培训需求，生成培训计划复盘方案。",
            ("## 培训对象", "## 课程设计", "## 练习评估", "## 学习复盘"),
        ),
        "02-use-cases/contract-fulfillment/fulfillment-monitor-langgraph": (
            "langgraph",
            "分析一组合同履约记录，生成履约风险复盘方案。",
            ("## 履约节点", "## 风险预警", "## 协同动作", "## 验收复盘"),
        ),
        "02-use-cases/contract-fulfillment/fulfillment-monitor-adk": (
            "adk",
            "分析一组合同履约记录，生成履约风险复盘方案。",
            ("## 履约节点", "## 风险预警", "## 协同动作", "## 验收复盘"),
        ),
        "02-use-cases/contract-fulfillment/fulfillment-monitor-langchain": (
            "langchain",
            "分析一组合同履约记录，生成履约风险复盘方案。",
            ("## 履约节点", "## 风险预警", "## 协同动作", "## 验收复盘"),
        ),
        "02-use-cases/contract-fulfillment/fulfillment-monitor-deepagents": (
            "deepagents",
            "分析一组合同履约记录，生成履约风险复盘方案。",
            ("## 履约节点", "## 风险预警", "## 协同动作", "## 验收复盘"),
        ),
        "02-use-cases/tender-collaboration/bid-evaluator-langgraph": (
            "langgraph",
            "分析一组招投标协同材料，生成评分协同复盘方案。",
            ("## 招标需求", "## 供应商响应", "## 评分协同", "## 风险复盘"),
        ),
        "02-use-cases/tender-collaboration/bid-evaluator-adk": (
            "adk",
            "分析一组招投标协同材料，生成评分协同复盘方案。",
            ("## 招标需求", "## 供应商响应", "## 评分协同", "## 风险复盘"),
        ),
        "02-use-cases/tender-collaboration/bid-evaluator-langchain": (
            "langchain",
            "分析一组招投标协同材料，生成评分协同复盘方案。",
            ("## 招标需求", "## 供应商响应", "## 评分协同", "## 风险复盘"),
        ),
        "02-use-cases/tender-collaboration/bid-evaluator-deepagents": (
            "deepagents",
            "分析一组招投标协同材料，生成评分协同复盘方案。",
            ("## 招标需求", "## 供应商响应", "## 评分协同", "## 风险复盘"),
        ),
        "02-use-cases/campus-operations/campus-service-langgraph": (
            "langgraph",
            "分析一组园区运营事件，生成园区服务复盘方案。",
            ("## 园区工单", "## 能耗资源", "## 访客安全", "## 运营复盘"),
        ),
        "02-use-cases/campus-operations/campus-service-adk": (
            "adk",
            "分析一组园区运营事件，生成园区服务复盘方案。",
            ("## 园区工单", "## 能耗资源", "## 访客安全", "## 运营复盘"),
        ),
        "02-use-cases/campus-operations/campus-service-langchain": (
            "langchain",
            "分析一组园区运营事件，生成园区服务复盘方案。",
            ("## 园区工单", "## 能耗资源", "## 访客安全", "## 运营复盘"),
        ),
        "02-use-cases/campus-operations/campus-service-deepagents": (
            "deepagents",
            "分析一组园区运营事件，生成园区服务复盘方案。",
            ("## 园区工单", "## 能耗资源", "## 访客安全", "## 运营复盘"),
        ),
        "02-use-cases/property-leasing/leasing-copilot-langgraph": (
            "langgraph",
            "分析一组物业招商线索，生成租赁转化复盘方案。",
            ("## 招商线索", "## 租赁方案", "## 合同协同", "## 转化复盘"),
        ),
        "02-use-cases/property-leasing/leasing-copilot-adk": (
            "adk",
            "分析一组物业招商线索，生成租赁转化复盘方案。",
            ("## 招商线索", "## 租赁方案", "## 合同协同", "## 转化复盘"),
        ),
        "02-use-cases/property-leasing/leasing-copilot-langchain": (
            "langchain",
            "分析一组物业招商线索，生成租赁转化复盘方案。",
            ("## 招商线索", "## 租赁方案", "## 合同协同", "## 转化复盘"),
        ),
        "02-use-cases/property-leasing/leasing-copilot-deepagents": (
            "deepagents",
            "分析一组物业招商线索，生成租赁转化复盘方案。",
            ("## 招商线索", "## 租赁方案", "## 合同协同", "## 转化复盘"),
        ),
        "02-use-cases/support-knowledge-operations/knowledge-feedback-langgraph": (
            "langgraph",
            "分析一批客服知识反馈，生成知识运营复盘方案。",
            ("## 知识缺口", "## 工单反馈", "## 内容更新", "## 发布复盘"),
        ),
        "02-use-cases/support-knowledge-operations/knowledge-feedback-adk": (
            "adk",
            "分析一批客服知识反馈，生成知识运营复盘方案。",
            ("## 知识缺口", "## 工单反馈", "## 内容更新", "## 发布复盘"),
        ),
        "02-use-cases/support-knowledge-operations/knowledge-feedback-langchain": (
            "langchain",
            "分析一批客服知识反馈，生成知识运营复盘方案。",
            ("## 知识缺口", "## 工单反馈", "## 内容更新", "## 发布复盘"),
        ),
        "02-use-cases/support-knowledge-operations/knowledge-feedback-deepagents": (
            "deepagents",
            "分析一批客服知识反馈，生成知识运营复盘方案。",
            ("## 知识缺口", "## 工单反馈", "## 内容更新", "## 发布复盘"),
        ),
        "02-use-cases/event-operations/event-runbook-langgraph": (
            "langgraph",
            "分析一组活动会务数据，生成活动运营复盘方案。",
            ("## 活动报名", "## 现场执行", "## 资源调度", "## 效果复盘"),
        ),
        "02-use-cases/event-operations/event-runbook-adk": (
            "adk",
            "分析一组活动会务数据，生成活动运营复盘方案。",
            ("## 活动报名", "## 现场执行", "## 资源调度", "## 效果复盘"),
        ),
        "02-use-cases/event-operations/event-runbook-langchain": (
            "langchain",
            "分析一组活动会务数据，生成活动运营复盘方案。",
            ("## 活动报名", "## 现场执行", "## 资源调度", "## 效果复盘"),
        ),
        "02-use-cases/event-operations/event-runbook-deepagents": (
            "deepagents",
            "分析一组活动会务数据，生成活动运营复盘方案。",
            ("## 活动报名", "## 现场执行", "## 资源调度", "## 效果复盘"),
        ),
        "02-use-cases/meeting-minutes/action-tracker-langgraph": (
            "langgraph",
            "分析一组会议材料，生成会议纪要和行动跟踪方案。",
            ("## 会议材料", "## 行动项", "## 决策追踪", "## 纪要复盘"),
        ),
        "02-use-cases/meeting-minutes/action-tracker-adk": (
            "adk",
            "分析一组会议材料，生成会议纪要和行动跟踪方案。",
            ("## 会议材料", "## 行动项", "## 决策追踪", "## 纪要复盘"),
        ),
        "02-use-cases/meeting-minutes/action-tracker-langchain": (
            "langchain",
            "分析一组会议材料，生成会议纪要和行动跟踪方案。",
            ("## 会议材料", "## 行动项", "## 决策追踪", "## 纪要复盘"),
        ),
        "02-use-cases/meeting-minutes/action-tracker-deepagents": (
            "deepagents",
            "分析一组会议材料，生成会议纪要和行动跟踪方案。",
            ("## 会议材料", "## 行动项", "## 决策追踪", "## 纪要复盘"),
        ),
        "02-use-cases/enterprise-okr/okr-review-langgraph": (
            "langgraph",
            "分析一组企业 OKR 进展，生成季度复盘方案。",
            ("## 目标拆解", "## 进度风险", "## 协同动作", "## 季度复盘"),
        ),
        "02-use-cases/enterprise-okr/okr-review-adk": (
            "adk",
            "分析一组企业 OKR 进展，生成季度复盘方案。",
            ("## 目标拆解", "## 进度风险", "## 协同动作", "## 季度复盘"),
        ),
        "02-use-cases/enterprise-okr/okr-review-langchain": (
            "langchain",
            "分析一组企业 OKR 进展，生成季度复盘方案。",
            ("## 目标拆解", "## 进度风险", "## 协同动作", "## 季度复盘"),
        ),
        "02-use-cases/enterprise-okr/okr-review-deepagents": (
            "deepagents",
            "分析一组企业 OKR 进展，生成季度复盘方案。",
            ("## 目标拆解", "## 进度风险", "## 协同动作", "## 季度复盘"),
        ),
        "02-use-cases/organization-knowledge-graph/graph-curator-langgraph": (
            "langgraph",
            "分析一组组织知识材料，生成知识图谱更新复盘方案。",
            ("## 实体抽取", "## 关系校验", "## 知识更新", "## 图谱复盘"),
        ),
        "02-use-cases/organization-knowledge-graph/graph-curator-adk": (
            "adk",
            "分析一组组织知识材料，生成知识图谱更新复盘方案。",
            ("## 实体抽取", "## 关系校验", "## 知识更新", "## 图谱复盘"),
        ),
        "02-use-cases/organization-knowledge-graph/graph-curator-langchain": (
            "langchain",
            "分析一组组织知识材料，生成知识图谱更新复盘方案。",
            ("## 实体抽取", "## 关系校验", "## 知识更新", "## 图谱复盘"),
        ),
        "02-use-cases/organization-knowledge-graph/graph-curator-deepagents": (
            "deepagents",
            "分析一组组织知识材料，生成知识图谱更新复盘方案。",
            ("## 实体抽取", "## 关系校验", "## 知识更新", "## 图谱复盘"),
        ),
    }

    for relative_dir, (framework, question, sections) in samples.items():
        sample_dir = ROOT / relative_dir
        required_files = ["README.md", "agent.py", "prompts.py", "tools.py", "data.py", "demo.py", "agentengine.yaml", "requirements.txt"]
        if framework == "langgraph":
            required_files.append("workflow.py")
        for filename in required_files:
            assert (sample_dir / filename).is_file(), f"{relative_dir} missing {filename}"

        module_name = "sample_best_practice_" + "_".join(sample_dir.relative_to(ROOT).parts)
        sys.path.insert(0, str(ROOT))
        sys.path.insert(0, str(sample_dir))
        try:
            spec = importlib.util.spec_from_file_location(module_name, sample_dir / "agent.py")
            assert spec is not None
            assert spec.loader is not None
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            assert hasattr(module, "root_agent")
            if framework == "langgraph":
                assert hasattr(module, "ksadk_prepare_state"), f"{relative_dir} missing ksadk_prepare_state"
                state = module.ksadk_prepare_state({"input": question}, {})
                assert state["query"] == question
                assert state["answer"] == ""
            tools = importlib.import_module("tools")
            answer = tools.render_demo_answer(question)
            for section in sections:
                assert section in answer
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
        if readme_path.parent == ROOT / "02-use-cases/agentengine-toolsets/langgraph":
            continue
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
