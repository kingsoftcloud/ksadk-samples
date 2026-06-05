from __future__ import annotations

import sys
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
FRAMEWORKS = {"adk", "langgraph", "langchain", "deepagents"}
REQUIRED_FILES = {"README.md", "agent.py", "agentengine.yaml", "requirements.txt"}


def iter_sample_dirs() -> list[Path]:
    sample_dirs: list[Path] = []
    for config_path in ROOT.glob("0*/**/agentengine.yaml"):
        sample_dirs.append(config_path.parent)
    return sorted(sample_dirs)


def validate_sample(sample_dir: Path) -> list[str]:
    errors: list[str] = []
    missing = sorted(name for name in REQUIRED_FILES if not (sample_dir / name).is_file())
    if missing:
        errors.append(f"{sample_dir.relative_to(ROOT)} missing files: {', '.join(missing)}")
        return errors

    config = yaml.safe_load((sample_dir / "agentengine.yaml").read_text(encoding="utf-8")) or {}
    framework = str(config.get("framework") or "")
    if framework not in FRAMEWORKS:
        errors.append(f"{sample_dir.relative_to(ROOT)} invalid framework: {framework}")

    entry_point = str(config.get("entry_point") or "")
    if not entry_point:
        errors.append(f"{sample_dir.relative_to(ROOT)} missing entry_point")
    elif not (sample_dir / entry_point).is_file():
        errors.append(f"{sample_dir.relative_to(ROOT)} entry_point not found: {entry_point}")

    agent_variable = str(config.get("agent_variable") or "")
    if not agent_variable:
        errors.append(f"{sample_dir.relative_to(ROOT)} missing agent_variable")
    else:
        agent_text = (sample_dir / entry_point).read_text(encoding="utf-8")
        if agent_variable not in agent_text:
            errors.append(f"{sample_dir.relative_to(ROOT)} agent_variable not present in agent.py: {agent_variable}")

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
            errors.append(f"{sample_dir.relative_to(ROOT)} import smoke failed: {exc}")
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
    for sample_dir in sample_dirs:
        errors.extend(validate_sample(sample_dir))
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
