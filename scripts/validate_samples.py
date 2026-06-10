from __future__ import annotations

import sys
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import check_public_readiness

FRAMEWORKS = {"adk", "langgraph", "langchain", "deepagents"}
REQUIRED_FILES = {"README.md", "agent.py", "agentengine.yaml", "requirements.txt"}
ROOT_README_REQUIRED_CONTENT = (
    "默认使用中文 README",
    "场景导航",
    "Samples",
    "Examples",
    "按场景选择",
    "推荐主推 Demo",
    "02-use-cases/agentengine-toolsets/langgraph",
    "Skill Runtime",
    "Workspace",
    "Sandbox",
    "知识库",
    "长期记忆",
    "KSYUN_REGION=cn-beijing-6",
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
)
SAMPLE_README_REQUIRED_SECTIONS = (
    "适用场景",
    "环境准备",
    "本地运行",
    "Web UI 调试",
    "部署",
    "示例问题",
    "常见问题",
)


def iter_sample_dirs() -> list[Path]:
    sample_dirs: list[Path] = []
    for config_path in ROOT.glob("0*/**/agentengine.yaml"):
        sample_dirs.append(config_path.parent)
    return sorted(sample_dirs)


def _relative(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def validate_sample(sample_dir: Path) -> list[str]:
    errors: list[str] = []
    missing = sorted(name for name in REQUIRED_FILES if not (sample_dir / name).is_file())
    if missing:
        errors.append(f"{_relative(sample_dir)} missing files: {', '.join(missing)}")
        return errors

    config = yaml.safe_load((sample_dir / "agentengine.yaml").read_text(encoding="utf-8")) or {}
    framework = str(config.get("framework") or "")
    if framework not in FRAMEWORKS:
        errors.append(f"{_relative(sample_dir)} invalid framework: {framework}")

    entry_point = str(config.get("entry_point") or "")
    if not entry_point:
        errors.append(f"{_relative(sample_dir)} missing entry_point")
    elif not (sample_dir / entry_point).is_file():
        errors.append(f"{_relative(sample_dir)} entry_point not found: {entry_point}")

    agent_variable = str(config.get("agent_variable") or "")
    if not agent_variable:
        errors.append(f"{sample_dir.relative_to(ROOT)} missing agent_variable")
    else:
        agent_text = (sample_dir / entry_point).read_text(encoding="utf-8")
        if agent_variable not in agent_text:
            errors.append(f"{_relative(sample_dir)} agent_variable not present in agent.py: {agent_variable}")

    return errors


def validate_root_readme() -> list[str]:
    readme_path = ROOT / "README.md"
    if not readme_path.is_file():
        return ["README.md missing"]

    text = readme_path.read_text(encoding="utf-8")
    errors: list[str] = []
    for required in ROOT_README_REQUIRED_CONTENT:
        if required not in text:
            errors.append(f"README.md missing required content: {required}")
    return errors


def validate_sample_readme(sample_dir: Path) -> list[str]:
    readme_path = sample_dir / "README.md"
    if not readme_path.is_file():
        return [f"{_relative(sample_dir)} missing README.md"]

    text = readme_path.read_text(encoding="utf-8")
    errors: list[str] = []
    first_line = text.splitlines()[0] if text.splitlines() else ""
    if not any("\u4e00" <= character <= "\u9fff" for character in first_line):
        errors.append(f"{_relative(sample_dir)} README title must be Chinese-first")
    if len(text.splitlines()) < 35:
        errors.append(f"{_relative(sample_dir)} README is too short")
    for section in SAMPLE_README_REQUIRED_SECTIONS:
        if section not in text:
            errors.append(f"{_relative(sample_dir)} missing README section: {section}")
    return errors


def validate_public_safety() -> list[str]:
    check_public_readiness.ROOT = ROOT
    errors: list[str] = []
    for path in check_public_readiness.iter_public_text_files():
        for error in check_public_readiness.scan_file(path):
            errors.append(f"{_relative(path)}: {error}")
    return errors


def validate_sample_imports(sample_dirs: list[Path]) -> list[str]:
    errors: list[str] = []
    sys.path.insert(0, str(ROOT))
    for sample_dir in sample_dirs:
        config = yaml.safe_load((sample_dir / "agentengine.yaml").read_text(encoding="utf-8")) or {}
        entry_point = str(config.get("entry_point") or "")
        agent_variable = str(config.get("agent_variable") or "")
        module_name = entry_point.removesuffix(".py").replace("/", ".").replace("\\", ".")
        sys.path.insert(0, str(sample_dir))
        try:
            source = (sample_dir / entry_point).read_text(encoding="utf-8")
            compile(source, str(sample_dir / entry_point), "exec")
            if agent_variable not in source:
                errors.append(f"{sample_dir.relative_to(ROOT)} source does not mention {agent_variable}")
        except Exception as exc:
            errors.append(f"{_relative(sample_dir)} import smoke failed: {exc}")
        finally:
            try:
                sys.path.remove(str(sample_dir))
            except ValueError:
                pass
            sys.modules.pop(module_name, None)
    return errors


def main() -> int:
    sample_dirs = iter_sample_dirs()
    errors: list[str] = []
    errors.extend(validate_root_readme())
    errors.extend(validate_public_safety())
    for sample_dir in sample_dirs:
        errors.extend(validate_sample(sample_dir))
        errors.extend(validate_sample_readme(sample_dir))
    errors.extend(validate_sample_imports(sample_dirs))

    if not sample_dirs:
        errors.append("no samples found")

    if errors:
        print("Sample validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"Validated {len(sample_dirs)} samples.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
