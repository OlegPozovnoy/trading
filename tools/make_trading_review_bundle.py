#!/usr/bin/env python3
"""Create a safe full or incremental review bundle for a local code repository.

The script never modifies repository files and never launches the application.
It excludes secrets, sessions, media, logs, datasets, databases and model files;
clears Jupyter outputs in the copy; redacts credential-like literals in the copy;
and adds Git metadata, optional test output, and optional PostgreSQL DDL.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import platform
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import time
import zipfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

SCRIPT_VERSION = "1.1.0"
MAX_TEXT_BYTES = 2 * 1024 * 1024
MAX_DATA_BYTES = 1 * 1024 * 1024

TEXT_EXTENSIONS = {
    ".py", ".pyi", ".sql", ".sh", ".bash", ".zsh", ".fish",
    ".md", ".rst", ".txt", ".toml", ".yaml", ".yml", ".ini",
    ".cfg", ".conf", ".json", ".xml", ".properties", ".html",
    ".css", ".scss", ".js", ".jsx", ".ts", ".tsx", ".java",
    ".kt", ".kts", ".scala", ".go", ".rs", ".c", ".h", ".cpp",
    ".hpp", ".dockerfile", ".ipynb",
}
DATA_EXTENSIONS = {".csv", ".tsv"}
ALWAYS_INCLUDE_NAMES = {
    ".gitignore", ".gitattributes", ".dockerignore", ".editorconfig",
    "dockerfile", "makefile", "requirements.txt", "requirements-dev.txt",
    "pyproject.toml", "setup.py", "setup.cfg", "tox.ini", "pytest.ini",
    "environment.yml", "environment.yaml", "poetry.lock", "pdm.lock",
}

EXCLUDED_DIR_NAMES = {
    ".git", ".idea", ".vscode", ".venv", "venv", "env",
    "__pycache__", ".ipynb_checkpoints", ".pytest_cache", ".mypy_cache",
    ".ruff_cache", ".tox", ".nox", "node_modules", "dist", "build",
    "logs", "log", "data", "datasets", "results", "artifacts",
    "models", "checkpoints", "wandb", "mlruns", "catboost_info",
    "jsonlogs", "deal_imp_images", "level_images",
}

BINARY_OR_BULK_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".tif", ".tiff",
    ".ico", ".svg", ".pdf", ".mp3", ".wav", ".mp4", ".mov", ".avi",
    ".mkv", ".zip", ".7z", ".rar", ".tar", ".gz", ".bz2", ".xz",
    ".db", ".sqlite", ".sqlite3", ".parquet", ".feather", ".arrow",
    ".pkl", ".pickle", ".joblib", ".h5", ".hdf5", ".keras", ".pt",
    ".pth", ".onnx", ".npy", ".npz", ".ods", ".xls", ".xlsx",
    ".xlsm", ".tfevents", ".class", ".so", ".dll", ".dylib", ".exe",
}

SENSITIVE_SUFFIXES = {
    ".pem", ".key", ".p12", ".pfx", ".jks", ".keystore",
    ".session", ".session-journal", ".session-shm", ".session-wal",
}

SENSITIVE_NAME_RE = re.compile(
    r"(^|[._-])(\.env|env)([._-]|$)|"
    r"(^|[._-])(credentials?|secrets?)([._-]|$)|"
    r"(^|[._-])(id_rsa|id_ed25519)([._-]|$)",
    re.IGNORECASE,
)

# High-confidence token formats. Values are never written to reports.
TOKEN_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("private_key", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")),
    ("openai_key", re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b")),
    ("github_token", re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})\b")),
    ("aws_access_key", re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b")),
    ("google_api_key", re.compile(r"\bAIza[0-9A-Za-z_-]{30,}\b")),
    ("huggingface_token", re.compile(r"\bhf_[A-Za-z0-9]{20,}\b")),
    ("slack_token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{20,}\b")),
    ("telegram_bot_token", re.compile(r"\b\d{6,12}:[A-Za-z0-9_-]{30,}\b")),
    ("basic_auth_url", re.compile(r"(?i)\b(?:postgres(?:ql)?|mysql|mongodb(?:\+srv)?|redis)://[^\s/:]+:[^\s/@]+@")),
]

# Literal assignments such as password = "...". Only the staged copy is changed.
CREDENTIAL_ASSIGNMENT_RE = re.compile(
    r"(?im)(?P<prefix>\b(?:password|passwd|secret|api[_-]?key|api[_-]?hash|"
    r"app[_-]?password|access[_-]?token|refresh[_-]?token|openai_key|"
    r"yagptkey|tg_key|invest_token|token_write)\b\s*[:=]\s*)"
    r"(?P<quote>['\"])(?P<value>[^'\"\r\n]{4,})(?P=quote)"
)

ENV_KEY_RE = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=", re.MULTILINE)


@dataclass(frozen=True)
class SelectedFile:
    relative_path: str
    source_path: Path
    size_bytes: int
    sha256: str


@dataclass(frozen=True)
class ExcludedFile:
    relative_path: str
    size_bytes: int
    reason: str


def eprint(*args: object) -> None:
    print(*args, file=sys.stderr)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def is_probably_text(path: Path) -> bool:
    try:
        sample = path.read_bytes()[:8192]
    except OSError:
        return False
    if b"\x00" in sample:
        return False
    try:
        sample.decode("utf-8")
        return True
    except UnicodeDecodeError:
        return False


def sensitive_filename(name: str) -> bool:
    lower = name.lower()
    if lower == "my.env" or lower == ".env" or lower.startswith(".env."):
        return True
    if lower.endswith(".env") or lower.startswith("env."):
        return True
    if any(lower.endswith(suffix) for suffix in SENSITIVE_SUFFIXES):
        return True
    return bool(SENSITIVE_NAME_RE.search(lower))


def classify_file(path: Path, relative_path: str) -> tuple[bool, str]:
    name = path.name
    lower_name = name.lower()
    suffix = path.suffix.lower()

    if sensitive_filename(name):
        return False, "sensitive filename"
    if suffix in BINARY_OR_BULK_EXTENSIONS:
        return False, f"binary/bulk extension {suffix or '[none]'}"

    try:
        size = path.stat().st_size
    except OSError as exc:
        return False, f"stat error: {exc}"

    if lower_name in ALWAYS_INCLUDE_NAMES:
        return size <= MAX_TEXT_BYTES, "included project metadata" if size <= MAX_TEXT_BYTES else "metadata file too large"
    if suffix in DATA_EXTENSIONS:
        return size <= MAX_DATA_BYTES, "small text data" if size <= MAX_DATA_BYTES else "data file over 1 MiB"
    if suffix in TEXT_EXTENSIONS:
        return size <= MAX_TEXT_BYTES, "text/source" if size <= MAX_TEXT_BYTES else "text/source over 2 MiB"
    if suffix == "":
        if size > MAX_TEXT_BYTES:
            return False, "extensionless file over 2 MiB"
        return (True, "extensionless text") if is_probably_text(path) else (False, "extensionless binary")
    return False, f"extension not selected: {suffix or '[none]'}"


def discover(repo: Path) -> tuple[list[SelectedFile], list[ExcludedFile], list[str]]:
    selected: list[SelectedFile] = []
    excluded: list[ExcludedFile] = []
    tree_entries: list[str] = []

    for root, dirs, files in os.walk(repo):
        root_path = Path(root)
        relative_root = root_path.relative_to(repo)

        kept_dirs: list[str] = []
        for directory in sorted(dirs):
            rel = (relative_root / directory).as_posix()
            if (
                directory in EXCLUDED_DIR_NAMES
                or directory.startswith(".review_bundle")
                or directory.endswith("_review_exports")
            ):
                tree_entries.append(f"D_EXCLUDED\t{rel}\tname-based exclusion")
            else:
                kept_dirs.append(directory)
                tree_entries.append(f"D\t{rel}\t")
        dirs[:] = kept_dirs

        for filename in sorted(files):
            source = root_path / filename
            rel = source.relative_to(repo).as_posix()
            if source.is_symlink():
                excluded.append(ExcludedFile(rel, 0, "symbolic link"))
                tree_entries.append(f"F_EXCLUDED\t{rel}\tsymbolic link")
                continue
            try:
                size = source.stat().st_size
            except OSError as exc:
                excluded.append(ExcludedFile(rel, 0, f"stat error: {exc}"))
                tree_entries.append(f"F_EXCLUDED\t{rel}\tstat error")
                continue

            include, reason = classify_file(source, rel)
            if include:
                try:
                    digest = sha256_file(source)
                except OSError as exc:
                    excluded.append(ExcludedFile(rel, size, f"read error: {exc}"))
                    tree_entries.append(f"F_EXCLUDED\t{rel}\tread error")
                    continue
                selected.append(SelectedFile(rel, source, size, digest))
                tree_entries.append(f"F\t{rel}\t{size}")
            else:
                excluded.append(ExcludedFile(rel, size, reason))
                tree_entries.append(f"F_EXCLUDED\t{rel}\t{reason}")

    selected.sort(key=lambda item: item.relative_path)
    excluded.sort(key=lambda item: item.relative_path)
    tree_entries.sort()
    return selected, excluded, tree_entries


def read_previous_manifest(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    result: dict[str, str] = {}
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        for row in reader:
            rel = row.get("relative_path")
            digest = row.get("sha256")
            if rel and digest:
                result[rel] = digest
    return result


def write_manifest(path: Path, selected: Iterable[SelectedFile]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t")
        writer.writerow(["relative_path", "size_bytes", "sha256"])
        for item in selected:
            writer.writerow([item.relative_path, item.size_bytes, item.sha256])


def safe_text_read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def sanitize_text(text: str, relative_path: str, redactions: list[tuple[str, int, str]]) -> str:
    def replace_token(rule_name: str, pattern: re.Pattern[str], current: str) -> str:
        def repl(match: re.Match[str]) -> str:
            line = current.count("\n", 0, match.start()) + 1
            redactions.append((relative_path, line, rule_name))
            token = match.group(0)
            if token.startswith("-----BEGIN"):
                return "-----BEGIN REDACTED PRIVATE KEY-----"
            if "://" in token and "@" in token:
                return re.sub(r"(://[^\s/:]+:)[^\s/@]+(@)", r"\1***REDACTED***\2", token)
            return "***REDACTED***"
        return pattern.sub(repl, current)

    sanitized = text
    for rule_name, pattern in TOKEN_PATTERNS:
        sanitized = replace_token(rule_name, pattern, sanitized)

    def assignment_repl(match: re.Match[str]) -> str:
        value = match.group("value")
        lowered = value.lower()
        if any(marker in lowered for marker in ("redacted", "example", "changeme", "placeholder", "dummy", "none", "null")):
            return match.group(0)
        line = sanitized.count("\n", 0, match.start()) + 1
        redactions.append((relative_path, line, "literal_credential_assignment"))
        quote = match.group("quote")
        return f"{match.group('prefix')}{quote}***REDACTED***{quote}"

    sanitized = CREDENTIAL_ASSIGNMENT_RE.sub(assignment_repl, sanitized)
    return sanitized


def clean_notebook_text(text: str) -> str:
    notebook = json.loads(text)
    for cell in notebook.get("cells", []):
        if cell.get("cell_type") == "code":
            cell["outputs"] = []
            cell["execution_count"] = None
    metadata = notebook.get("metadata")
    if isinstance(metadata, dict):
        metadata.pop("widgets", None)
    return json.dumps(notebook, ensure_ascii=False, indent=1) + "\n"


def copy_selected_file(item: SelectedFile, destination: Path, redactions: list[tuple[str, int, str]]) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    try:
        text = safe_text_read(item.source_path)
    except UnicodeDecodeError:
        shutil.copy2(item.source_path, destination)
        return

    if item.source_path.suffix.lower() == ".ipynb":
        try:
            text = clean_notebook_text(text)
        except (json.JSONDecodeError, TypeError, ValueError):
            pass
    text = sanitize_text(text, item.relative_path, redactions)
    destination.write_text(text, encoding="utf-8")


def run_command(command: list[str], cwd: Path, timeout: int = 120) -> tuple[int, str]:
    try:
        completed = subprocess.run(
            command,
            cwd=cwd,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=timeout,
            check=False,
            env=os.environ.copy(),
        )
        return completed.returncode, completed.stdout
    except FileNotFoundError:
        return 127, f"Command not found: {command[0]}\n"
    except subprocess.TimeoutExpired as exc:
        partial = exc.stdout or ""
        return 124, f"{partial}\nTimed out after {timeout} seconds.\n"


def write_git_metadata(repo: Path, meta: Path, redactions: list[tuple[str, int, str]]) -> None:
    git_dir = repo / ".git"
    if not git_dir.exists():
        (meta / "git_status.txt").write_text("Not a Git working tree.\n", encoding="utf-8")
        return

    commands = {
        "git_status.txt": ["git", "status", "--short", "--branch"],
        "git_log.txt": ["git", "log", "-20", "--date=iso-strict", "--pretty=format:%H%x09%ad%x09%an%x09%s"],
        "git_diff.patch": ["git", "diff", "--no-ext-diff", "--no-color", "HEAD"],
        "git_branch.txt": ["git", "branch", "--show-current"],
        "git_head.txt": ["git", "rev-parse", "HEAD"],
        "git_remote_names.txt": ["git", "remote"],
    }
    for filename, command in commands.items():
        code, output = run_command(command, repo, timeout=120)
        text = f"exit_code={code}\n{output}"
        text = sanitize_text(text, f"bundle_meta/{filename}", redactions)
        (meta / filename).write_text(text, encoding="utf-8")


def write_environment_metadata(meta: Path) -> None:
    lines = [
        f"script_version={SCRIPT_VERSION}",
        f"created_at_utc={datetime.now(timezone.utc).isoformat()}",
        f"platform={platform.platform()}",
        f"python={sys.version.replace(os.linesep, ' ')}",
    ]
    for command in (["git", "--version"], ["pg_dump", "--version"], ["psql", "--version"]):
        code, output = run_command(command, Path.cwd(), timeout=15)
        lines.append(f"{' '.join(command)} exit_code={code}: {output.strip()}")
    (meta / "environment.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


def export_env_key_names(excluded: list[ExcludedFile], repo: Path, meta: Path) -> None:
    rows: list[tuple[str, str]] = []
    for item in excluded:
        path = repo / item.relative_path
        if not path.exists() or not sensitive_filename(path.name):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for key in ENV_KEY_RE.findall(text):
            rows.append((item.relative_path, key))
    if rows:
        with (meta / "excluded_env_keys.tsv").open("w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle, delimiter="\t")
            writer.writerow(["excluded_file", "variable_name"])
            writer.writerows(sorted(set(rows)))


def export_postgres(args: argparse.Namespace, repo: Path, meta: Path, redactions: list[tuple[str, int, str]]) -> None:
    database = args.pg_database or os.getenv("REVIEW_PGDATABASE")
    if not database:
        (meta / "postgres_export.txt").write_text(
            "Skipped: set REVIEW_PGDATABASE and REVIEW_PGUSER, or pass --pg-database/--pg-user.\n",
            encoding="utf-8",
        )
        return

    host = args.pg_host or os.getenv("REVIEW_PGHOST", "127.0.0.1")
    port = str(args.pg_port or os.getenv("REVIEW_PGPORT", "5432"))
    user = args.pg_user or os.getenv("REVIEW_PGUSER")
    if not user:
        (meta / "postgres_export.txt").write_text("Skipped: PostgreSQL user is missing.\n", encoding="utf-8")
        return

    ddl_command = [
        "pg_dump", "-h", host, "-p", port, "-U", user, "-d", database,
        "--schema-only", "--no-owner", "--no-privileges",
    ]
    code, output = run_command(ddl_command, repo, timeout=args.db_timeout)
    if code == 0:
        output = sanitize_text(output, "bundle_meta/postgres_schema.sql", redactions)
        (meta / "postgres_schema.sql").write_text(output, encoding="utf-8")
    else:
        safe_error = sanitize_text(output, "bundle_meta/postgres_export.txt", redactions)
        (meta / "postgres_export.txt").write_text(
            f"pg_dump exit_code={code}\n{safe_error}", encoding="utf-8"
        )
        return

    query = """
SELECT
    n.nspname AS schema_name,
    c.relname AS object_name,
    CASE c.relkind
        WHEN 'r' THEN 'table'
        WHEN 'p' THEN 'partitioned_table'
        WHEN 'v' THEN 'view'
        WHEN 'm' THEN 'materialized_view'
        ELSE c.relkind::text
    END AS object_type,
    c.reltuples::bigint AS estimated_rows,
    pg_relation_size(c.oid) AS table_bytes,
    pg_indexes_size(c.oid) AS indexes_bytes,
    pg_total_relation_size(c.oid) AS total_bytes
FROM pg_class c
JOIN pg_namespace n ON n.oid = c.relnamespace
WHERE c.relkind IN ('r', 'p', 'v', 'm')
  AND n.nspname NOT IN ('pg_catalog', 'information_schema')
  AND n.nspname !~ '^pg_toast'
ORDER BY pg_total_relation_size(c.oid) DESC;
""".strip()
    psql_command = [
        "psql", "-h", host, "-p", port, "-U", user, "-d", database,
        "--csv", "--no-psqlrc", "-c", query,
    ]
    code, output = run_command(psql_command, repo, timeout=args.db_timeout)
    if code == 0:
        output = sanitize_text(output, "bundle_meta/postgres_objects.csv", redactions)
        (meta / "postgres_objects.csv").write_text(output, encoding="utf-8")
    else:
        safe_error = sanitize_text(output, "bundle_meta/postgres_inventory_error.txt", redactions)
        (meta / "postgres_inventory_error.txt").write_text(
            f"psql exit_code={code}\n{safe_error}", encoding="utf-8"
        )


def run_optional_tests(args: argparse.Namespace, repo: Path, meta: Path, redactions: list[tuple[str, int, str]]) -> None:
    command = args.test_cmd or os.getenv("REVIEW_TEST_CMD")
    if not command:
        (meta / "tests.txt").write_text(
            "Skipped. The script never launches trading or tests automatically. "
            "Pass --test-cmd 'pytest -q' only when that command is safe.\n",
            encoding="utf-8",
        )
        return

    start = time.monotonic()
    try:
        completed = subprocess.run(
            command,
            cwd=repo,
            shell=True,
            executable="/bin/bash",
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=args.test_timeout,
            check=False,
            env=os.environ.copy(),
        )
        code = completed.returncode
        output = completed.stdout
    except subprocess.TimeoutExpired as exc:
        code = 124
        output = (exc.stdout or "") + f"\nTimed out after {args.test_timeout} seconds.\n"
    elapsed = time.monotonic() - start
    text = f"command={command}\nexit_code={code}\nelapsed_seconds={elapsed:.2f}\n\n{output}"
    text = sanitize_text(text, "bundle_meta/tests.txt", redactions)
    (meta / "tests.txt").write_text(text, encoding="utf-8")


def create_zip(source_dir: Path, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    compression = zipfile.ZIP_DEFLATED
    with zipfile.ZipFile(output_path, "w", compression=compression, compresslevel=9) as archive:
        for path in sorted(source_dir.rglob("*")):
            if path.is_file():
                archive.write(path, path.relative_to(source_dir.parent).as_posix())


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a sanitized full/incremental bundle for code review."
    )
    parser.add_argument(
        "--repo",
        type=Path,
        default=None,
        help=(
            "Repository path. By default the script finds the Git root from the "
            "current directory or from its own location."
        ),
    )
    parser.add_argument("--output-dir", type=Path, default=None, help="Output directory; default: sibling trading_review_exports")
    parser.add_argument("--full", action="store_true", help="Force a full bundle instead of an incremental update")
    parser.add_argument("--reset-state", action="store_true", help="Forget the previous manifest before this run")
    parser.add_argument("--test-cmd", default=None, help="Optional safe test command, e.g. 'pytest -q'")
    parser.add_argument("--test-timeout", type=int, default=600, help="Test timeout in seconds; default: 600")
    parser.add_argument("--pg-host", default=None)
    parser.add_argument("--pg-port", type=int, default=None)
    parser.add_argument("--pg-user", default=None)
    parser.add_argument("--pg-database", default=None)
    parser.add_argument("--db-timeout", type=int, default=120, help="PostgreSQL export timeout in seconds")
    return parser.parse_args()


def detect_repository(explicit_repo: Path | None) -> Path:
    """Resolve the intended repository even when PyCharm uses tools/ as cwd."""

    if explicit_repo is not None:
        return explicit_repo.expanduser().resolve()

    candidates = [
        Path.cwd().resolve(),
        Path(__file__).resolve().parent,
        Path(__file__).resolve().parent.parent,
    ]

    checked: set[Path] = set()
    for candidate in candidates:
        if candidate in checked or not candidate.exists():
            continue
        checked.add(candidate)

        code, output = run_command(
            ["git", "rev-parse", "--show-toplevel"],
            candidate,
            timeout=15,
        )
        if code == 0:
            root = output.strip().splitlines()
            if root:
                return Path(root[-1]).expanduser().resolve()

    # Last-resort fallback: when the script lives in <repo>/tools/.
    script_parent = Path(__file__).resolve().parent
    if script_parent.name == "tools" and script_parent.parent.is_dir():
        return script_parent.parent

    return Path.cwd().resolve()


def main() -> int:
    args = parse_args()
    repo = detect_repository(args.repo)
    if not repo.is_dir():
        eprint(f"Repository directory does not exist: {repo}")
        return 2

    output_dir = (args.output_dir.expanduser().resolve() if args.output_dir else repo.parent / f"{repo.name}_review_exports")
    state_id = hashlib.sha256(str(repo).encode("utf-8")).hexdigest()[:16]
    state_dir = Path.home() / ".cache" / "review-bundle" / state_id
    state_manifest = state_dir / "manifest.tsv"
    if args.reset_state and state_dir.exists():
        shutil.rmtree(state_dir)

    selected, excluded, tree_entries = discover(repo)
    previous = read_previous_manifest(state_manifest)
    current = {item.relative_path: item.sha256 for item in selected}

    mode = "full" if args.full or not previous else "update"
    if mode == "full":
        included_now = selected
        deleted: list[str] = []
    else:
        included_now = [item for item in selected if previous.get(item.relative_path) != item.sha256]
        deleted = sorted(set(previous) - set(current))

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    bundle_name = f"{repo.name}_review_{mode}_{timestamp}"
    output_path = output_dir / f"{bundle_name}.zip"

    redactions: list[tuple[str, int, str]] = []

    with tempfile.TemporaryDirectory(prefix="review_bundle_") as temp_name:
        temp = Path(temp_name)
        bundle_root = temp / bundle_name
        files_root = bundle_root / "files"
        meta = bundle_root / "bundle_meta"
        meta.mkdir(parents=True, exist_ok=True)

        for item in included_now:
            copy_selected_file(item, files_root / item.relative_path, redactions)

        with (meta / "current_manifest.tsv").open("w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle, delimiter="\t")
            writer.writerow(["relative_path", "size_bytes", "sha256"])
            for item in selected:
                writer.writerow([item.relative_path, item.size_bytes, item.sha256])

        with (meta / "included_in_this_bundle.tsv").open("w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle, delimiter="\t")
            writer.writerow(["relative_path", "size_bytes", "sha256"])
            for item in included_now:
                writer.writerow([item.relative_path, item.size_bytes, item.sha256])

        with (meta / "excluded_files.tsv").open("w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle, delimiter="\t")
            writer.writerow(["relative_path", "size_bytes", "reason"])
            for item in excluded:
                writer.writerow([item.relative_path, item.size_bytes, item.reason])

        (meta / "deleted_since_previous_bundle.txt").write_text(
            "\n".join(deleted) + ("\n" if deleted else ""), encoding="utf-8"
        )
        (meta / "project_tree.tsv").write_text("\n".join(tree_entries) + "\n", encoding="utf-8")

        write_git_metadata(repo, meta, redactions)
        write_environment_metadata(meta)
        export_env_key_names(excluded, repo, meta)
        run_optional_tests(args, repo, meta, redactions)
        export_postgres(args, repo, meta, redactions)

        readme = f"""Trading review bundle
=====================

Repository: {repo}
Mode: {mode}
Created (local): {datetime.now().astimezone().isoformat()}
Files selected in repository: {len(selected)}
Files included in this bundle: {len(included_now)}
Files excluded: {len(excluded)}
Files deleted since previous bundle: {len(deleted)}
Credential-like values redacted in staged copy: {len(redactions)}

Safety properties:
- Source repository files were not modified.
- The application and live trading were not launched.
- Environment files, sessions, keys, media, logs, databases, models and large datasets were excluded.
- Jupyter outputs were removed from copied notebooks.
- Credential-like literals were redacted only in the copied bundle.
- PostgreSQL export, when configured, contains schema only and no table rows.

Workflow:
- First run creates a full bundle.
- Later runs create incremental bundles containing new/changed selected files,
  deletion list, full current manifest, Git status/diff/log, and optional diagnostics.
- Use --full to create another complete snapshot.
"""
        (meta / "README.txt").write_text(readme, encoding="utf-8")

        if redactions:
            with (meta / "redactions.tsv").open("w", encoding="utf-8", newline="") as handle:
                writer = csv.writer(handle, delimiter="\t")
                writer.writerow(["relative_path", "line_number", "rule"])
                writer.writerows(sorted(set(redactions)))

        # Final high-confidence scan after sanitization. Abort rather than package a known token.
        residual_findings: list[tuple[str, int, str]] = []
        for path in bundle_root.rglob("*"):
            if not path.is_file():
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            rel = path.relative_to(bundle_root).as_posix()
            for rule_name, pattern in TOKEN_PATTERNS:
                for match in pattern.finditer(text):
                    if "REDACTED" in match.group(0):
                        continue
                    line = text.count("\n", 0, match.start()) + 1
                    residual_findings.append((rel, line, rule_name))
        if residual_findings:
            eprint("Bundle was NOT created: residual high-confidence credential patterns remain.")
            for rel, line, rule in residual_findings[:50]:
                eprint(f"  {rel}:{line}: {rule}")
            return 3

        create_zip(bundle_root, output_path)

    write_manifest(state_manifest, selected)

    print(f"Created: {output_path}")
    print(f"Mode: {mode}")
    print(f"Selected files in project: {len(selected)}")
    print(f"Included in this bundle: {len(included_now)}")
    print(f"Excluded files: {len(excluded)}")
    print(f"Deleted since previous bundle: {len(deleted)}")
    print(f"Redactions in staged copy: {len(redactions)}")
    print(f"Size: {output_path.stat().st_size / (1024 * 1024):.2f} MiB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
