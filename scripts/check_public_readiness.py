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

def _forbidden_literal_fragments() -> tuple[str, ...]:
    return (
        ".".join(("aicp", "inner", "api", "ksyun", "com")),
        ".".join(("mgr", "cn-beijing-6", "sandbox", "ksyun", "com")),
        ".".join(("100", "91", "6", "15")),
        "-".join(("7673e478", "277d", "4ebf", "")),
        "-".join(("15fd0bc7", "908a", "")),
        "AKLT" + "W9dW7YHYQ",
        "OHLW" + "iYdvCl1C",
        "-".join(("ab10091f", "ec89", "")),
        "pre" + "-online",
        "agent" + "-api-pre",
        "kspmas" + "-internal",
        "X-Ksc" + "-Region",
        "X-KSC" + "-CUSTOM-SOURCE",
    )

FORBIDDEN_PATTERNS = (
    re.compile(r"-----BEGIN (?:RSA |OPENSSH |EC |DSA )?PRIVATE KEY-----"),
    re.compile(r"(?i)(?:password|secret|token)\s*=\s*['\"]?[A-Za-z0-9_./+=-]{16,}"),
)


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
    for fragment in _forbidden_literal_fragments():
        if fragment in text:
            errors.append(f"contains forbidden internal fragment: {fragment}")
    for pattern in FORBIDDEN_PATTERNS:
        if pattern.search(text):
            errors.append(f"matches forbidden pattern: {pattern.pattern}")
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
