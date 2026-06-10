from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEXT_SUFFIXES = {
    ".env",
    ".example",
    ".md",
    ".py",
    ".txt",
    ".toml",
    ".yaml",
    ".yml",
}
EXCLUDED_PARTS = {
    ".git",
    ".venv",
    ".pytest_cache",
    ".ruff_cache",
    "__pycache__",
    "dist",
    "build",
}

FORBIDDEN_PATTERNS = (
    re.compile(r"(?i)\bpre[\W_]*online\b"),
    re.compile(r"(?i)\b[\w.-]*(?:inner|internal)[\w.-]*\.(?:api|example|com|cn|net|org)\b"),
    re.compile(r"(?i)\b[\w.-]+\.(?:inner|internal)\b"),
    re.compile(r"(?i)\b[\w.-]*(?:api|gateway|service)[\W_]*pre\b"),
    re.compile(r"(?i)\bX[\W_]*K(?:SC|sc)[\W_]*(?:Region|CUSTOM[\W_]*SOURCE|Account[\W_]*Id|[^\\s`|:=]*)\b"),
    re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
    re.compile(r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b", re.IGNORECASE),
    re.compile(r"-----BEGIN (?:RSA |OPENSSH |EC |DSA )?PRIVATE KEY-----"),
)
SECRET_ASSIGNMENT_PATTERN = re.compile(
    r"^\s*(?:export\s+)?[A-Z0-9_]*(?:ACCESS_KEY|SECRET_KEY|API_KEY|PASSWORD|TOKEN)\s*=\s*['\"]?([^'\"\s`#]+)"
)
PLACEHOLDER_PREFIXES = ("your-", "example-", "test-", "dummy-", "placeholder-")


def iter_public_text_files() -> list[Path]:
    files: list[Path] = []
    for path in ROOT.rglob("*"):
        if path.is_dir():
            continue
        relative = path.relative_to(ROOT)
        if any(part in EXCLUDED_PARTS for part in relative.parts):
            continue
        if path.name == ".DS_Store" or path.suffix == ".pyc":
            continue
        if path.suffix in TEXT_SUFFIXES or path.name in {"Makefile", ".gitignore"}:
            files.append(path)
    return sorted(files)


def scan_file(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8", errors="replace")
    errors: list[str] = []
    for pattern in FORBIDDEN_PATTERNS:
        if pattern.search(text):
            errors.append(f"matches forbidden pattern: {pattern.pattern}")
    for line_number, line in enumerate(text.splitlines(), start=1):
        match = SECRET_ASSIGNMENT_PATTERN.search(line)
        if not match:
            continue
        value = match.group(1).strip()
        lowered = value.lower()
        if not value or lowered.startswith(PLACEHOLDER_PREFIXES) or (value.startswith("<") and value.endswith(">")):
            continue
        if len(value) >= 16:
            errors.append(f"line {line_number} contains non-placeholder secret assignment")
    return errors


def main() -> int:
    errors: list[str] = []
    for path in iter_public_text_files():
        for error in scan_file(path):
            errors.append(f"{path.relative_to(ROOT)}: {error}")

    if errors:
        print("Public readiness scan failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Public readiness scan passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
