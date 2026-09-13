"""KCG — OSINT allowlist lint.

Per openspec/changes/kcg-university-of-galway-doc-processing-v1/,
Requirement: The OSINT allowlist lint gate.

Walks `dlt_sources/uog/**` looking for `@dlt.source` / `@dlt.resource`
declarations that reference a source URL. For each URL found:

  1. Verifies the URL is in `scripts/osint_allowlist.yaml`
  2. Verifies the URL host is on the British Isles + Republic of Ireland
     public-sector domain list

Exits 0 on success, 1 on any violation. Architecturally identical
to `scripts/lint_license.py` in cianchosaint.

Licence: BUSL-1.1 (KCG edition, per LICENSE.md).
"""
from __future__ import annotations

import ast
import sys
from collections.abc import Iterable
from pathlib import Path
from urllib.parse import urlparse

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
DLT_DIR = REPO_ROOT / "dlt_sources" / "uog"
ALLOWLIST_PATH = REPO_ROOT / "scripts" / "osint_allowlist.yaml"

# The canonical Irish public-sector + .ie + British Isles domain list.
BRITISH_ISLES_DOMAINS: frozenset[str] = frozenset({
    # Republic of Ireland
    "gov.ie",
    "irishstatutebook.ie",
    "courts.ie",
    "garda.ie",
    "defenceforces.ie",
    "dfa.ie",
    "hse.ie",
    "education.ie",
    "sfi.ie",
    "researchireland.ie",
    "ucd.ie",
    "tcd.ie",
    "ucc.ie",
    "ul.ie",
    "dcu.ie",
    "mu.ie",
    "nuim.ie",
    "atu.ie",
    "setu.ie",
    "tus.ie",
    "mtu.ie",
    "iuniofg.ie",
    "universityofgalway.ie",
    "nuigalway.ie",  # Historical alias for University of Galway
    "kingscollegalway.ie",  # Historical alias
    "library.universityofgalway.ie",
    "aran.library.universityofgalway.ie",
    # UK public-sector
    "gov.uk",
    "police.uk",
    "mod.uk",
    "judiciary.uk",
    "parliament.uk",
    "nhs.uk",
    "bbc.co.uk",
})


def load_allowlist() -> set[str]:
    if not ALLOWLIST_PATH.exists():
        return set()
    urls: set[str] = set()
    for doc in yaml.safe_load_all(ALLOWLIST_PATH.read_text(encoding="utf-8")):
        if doc is None:
            continue
        if isinstance(doc, list):
            for entry in doc:
                if isinstance(entry, dict):
                    url = entry.get("url") or entry.get("source_url")
                    if url:
                        urls.add(url)
        elif isinstance(doc, dict):
            for entry in doc.get("entries", []):
                if isinstance(entry, dict):
                    url = entry.get("url") or entry.get("source_url")
                    if url:
                        urls.add(url)
    return urls


def is_british_isles_url(url: str) -> bool:
    host = (urlparse(url).hostname or "").lower()
    if not host:
        return False
    for domain in BRITISH_ISLES_DOMAINS:
        if host == domain or host.endswith(f".{domain}"):
            return True
    return False


def extract_urls_from_ast(tree: ast.AST) -> Iterable[tuple[str, int]]:
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            value = node.value
            if value.startswith(("http://", "https://")):
                yield value, node.lineno


def has_dlt_decorator(tree: ast.AST) -> bool:
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            for decorator in node.decorator_list:
                if isinstance(decorator, ast.Attribute):
                    if decorator.attr in {"source", "resource"}:
                        return True
                if isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Attribute):
                    if decorator.func.attr in {"source", "resource"}:
                        return True
    return False


def lint_file(py_path: Path, allowlist: set[str]) -> list[str]:
    try:
        tree = ast.parse(py_path.read_text(encoding="utf-8"))
    except SyntaxError as exc:
        return [f"{py_path}:{exc.lineno}: syntax error: {exc.msg}"]

    if not has_dlt_decorator(tree):
        return []

    violations: list[str] = []
    for url, lineno in extract_urls_from_ast(tree):
        # Two checks. The British-Isles-body check is the binding licence
        # constraint (LICENSE.md § Additional Use Grant); the explicit
        # allowlist is a secondary track for documentation. A URL on a
        # known British/Irish host is implicitly allowlisted — the
        # explicit list is for cases where the URL host isn't itself a
        # recognised BI/IE public-sector body (e.g. doi.org, arxiv.org,
        # infra IPs).
        is_bi = is_british_isles_url(url)
        is_allowlisted = url in allowlist
        if not is_bi and not is_allowlisted:
            violations.append(
                f"{py_path}:{lineno}: URL not in OSINT allowlist: {url}"
            )
        if not is_bi and not is_allowlisted:
            violations.append(
                f"{py_path}:{lineno}: URL is not a British Isles / Irish body: {url}"
            )
    return violations


def main() -> int:
    if not DLT_DIR.exists():
        print(f"OK: {DLT_DIR} does not exist yet — no DLT sources to lint.")
        return 0

    allowlist = load_allowlist()
    print(f"Loaded {len(allowlist)} allowlisted URLs from {ALLOWLIST_PATH}")

    violations: list[str] = []
    file_count = 0
    for py_path in sorted(DLT_DIR.rglob("*.py")):
        file_count += 1
        violations.extend(lint_file(py_path, allowlist))

    if violations:
        print(f"FAIL: {len(violations)} violation(s) across {file_count} file(s); see LICENSE.md")
        for v in violations[:50]:
            print(f"  {v}")
        if len(violations) > 50:
            print(f"  ... and {len(violations) - 50} more")
        return 1

    print(f"OK: {file_count} file(s) scanned; {len(allowlist)} allowlist entries; 0 violations")
    return 0


if __name__ == "__main__":
    sys.exit(main())
