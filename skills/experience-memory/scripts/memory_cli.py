from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


KIND_CHOICES = (
    "error_fix",
    "best_practice",
    "project_preference",
    "decision",
)

DOC_KIND_CHOICES = ("solution", "decision")


@dataclass(slots=True)
class MemoryPaths:
    project_root: Path
    project_slug: str
    project_memory_root: Path
    project_learnings: Path
    project_solutions: Path
    project_decisions: Path
    project_profile: Path
    project_state: Path
    global_root: Path
    global_registry: Path
    global_shared_root: Path
    global_shared_learnings: Path
    global_shared_solutions: Path
    global_shared_decisions: Path
    global_project_catalog: Path


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def slugify(value: str) -> str:
    normalized = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower())
    collapsed = re.sub(r"-{2,}", "-", normalized).strip("-")
    return collapsed or "project"


def find_project_root(start: Path) -> Path:
    current = start.resolve()
    for candidate in (current, *current.parents):
        if (candidate / ".git").exists():
            return candidate
    return current


def resolve_project_root(project_root: str | None) -> Path:
    if project_root:
        return Path(project_root).resolve()
    return find_project_root(Path.cwd())


def build_paths(project_root: str | None) -> MemoryPaths:
    root = resolve_project_root(project_root)
    slug = slugify(root.name)
    project_memory_root = root / "docs" / "experience-memory"
    global_root = Path.home() / ".experience-memory"
    shared_root = global_root / "shared"

    return MemoryPaths(
        project_root=root,
        project_slug=slug,
        project_memory_root=project_memory_root,
        project_learnings=project_memory_root / "learnings.jsonl",
        project_solutions=project_memory_root / "solutions",
        project_decisions=project_memory_root / "decisions",
        project_profile=project_memory_root / "profile.json",
        project_state=project_memory_root / "state.json",
        global_root=global_root,
        global_registry=global_root / "registry" / "projects.json",
        global_shared_root=shared_root,
        global_shared_learnings=shared_root / "learnings.jsonl",
        global_shared_solutions=shared_root / "solutions",
        global_shared_decisions=shared_root / "decisions",
        global_project_catalog=(
            global_root / "projects" / slug / "catalog.json"
        ),
    )


def ensure_json_file(path: Path, default: dict[str, Any]) -> None:
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(default, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def ensure_jsonl_file(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.touch(exist_ok=True)


def read_json(path: Path, default: dict[str, Any]) -> dict[str, Any]:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []

    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        rows.append(json.loads(stripped))
    return rows


def append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False) + "\n")


def split_multi_values(values: list[str] | None) -> list[str]:
    if not values:
        return []

    items: list[str] = []
    for value in values:
        parts = [part.strip() for part in value.split(",")]
        items.extend(part for part in parts if part)
    return items


def ensure_unique_id(path: Path, base_id: str) -> str:
    existing_ids = {entry["id"] for entry in read_jsonl(path)}
    if base_id not in existing_ids:
        return base_id

    counter = 2
    while True:
        candidate = f"{base_id}-{counter}"
        if candidate not in existing_ids:
            return candidate
        counter += 1


def entry_score(entry: dict[str, Any], tokens: list[str]) -> int:
    haystacks = [
        str(entry.get("title", "")).lower(),
        str(entry.get("summary", "")).lower(),
        str(entry.get("rule", "")).lower(),
        " ".join(entry.get("tags", [])).lower(),
        " ".join(entry.get("files", [])).lower(),
        str(entry.get("kind", "")).lower(),
    ]
    score = 0

    for token in tokens:
        if token in haystacks[0]:
            score += 6
        if token in haystacks[1]:
            score += 4
        if token in haystacks[2]:
            score += 5
        if token in haystacks[3]:
            score += 3
        if token in haystacks[4]:
            score += 2
        if token in haystacks[5]:
            score += 1

    confidence = float(entry.get("confidence", 0))
    score += int(confidence * 10)
    if entry.get("scope") == "project":
        score += 2
    return score


def count_markdown_files(path: Path) -> int:
    if not path.exists():
        return 0
    return sum(1 for child in path.iterdir() if child.suffix.lower() == ".md")


def bootstrap(paths: MemoryPaths) -> None:
    for directory in (
        paths.project_memory_root,
        paths.project_solutions,
        paths.project_decisions,
        paths.global_registry.parent,
        paths.global_shared_root,
        paths.global_shared_solutions,
        paths.global_shared_decisions,
        paths.global_project_catalog.parent,
    ):
        directory.mkdir(parents=True, exist_ok=True)

    ensure_jsonl_file(paths.project_learnings)
    ensure_jsonl_file(paths.global_shared_learnings)
    ensure_json_file(
        paths.project_profile,
        {
            "version": 1,
            "project": paths.project_slug,
            "project_root": str(paths.project_root),
            "memory_root": str(paths.project_memory_root),
            "global_memory_root": str(paths.global_root),
            "created_at": now_iso(),
        },
    )
    ensure_json_file(
        paths.project_state,
        {
            "version": 1,
            "project": paths.project_slug,
            "last_search_at": None,
            "last_write_at": None,
            "last_promote_at": None,
        },
    )
    ensure_json_file(
        paths.global_registry,
        {
            "version": 1,
            "projects": {},
        },
    )

    register_project(paths)
    refresh_catalog(paths)


def register_project(paths: MemoryPaths) -> None:
    registry = read_json(paths.global_registry, {"version": 1, "projects": {}})
    projects = registry.setdefault("projects", {})
    existing = projects.get(paths.project_slug, {})

    first_seen = existing.get("first_seen_at", now_iso())
    projects[paths.project_slug] = {
        "slug": paths.project_slug,
        "project_root": str(paths.project_root),
        "project_memory_root": str(paths.project_memory_root),
        "first_seen_at": first_seen,
        "last_seen_at": now_iso(),
    }
    write_json(paths.global_registry, registry)


def refresh_catalog(paths: MemoryPaths) -> None:
    payload = {
        "version": 1,
        "project": {
            "slug": paths.project_slug,
            "project_root": str(paths.project_root),
            "memory_root": str(paths.project_memory_root),
        },
        "counts": {
            "learnings": len(read_jsonl(paths.project_learnings)),
            "solutions": count_markdown_files(paths.project_solutions),
            "decisions": count_markdown_files(paths.project_decisions),
        },
        "updated_at": now_iso(),
    }
    write_json(paths.global_project_catalog, payload)


def update_state(
    paths: MemoryPaths,
    *,
    search: bool = False,
    write: bool = False,
    promote: bool = False,
) -> None:
    state = read_json(
        paths.project_state,
        {
            "version": 1,
            "project": paths.project_slug,
            "last_search_at": None,
            "last_write_at": None,
            "last_promote_at": None,
        },
    )
    timestamp = now_iso()
    if search:
        state["last_search_at"] = timestamp
    if write:
        state["last_write_at"] = timestamp
    if promote:
        state["last_promote_at"] = timestamp
    write_json(paths.project_state, state)


def command_paths(args: argparse.Namespace) -> int:
    paths = build_paths(args.project_root)
    print(f"project_root={paths.project_root}")
    print(f"project_slug={paths.project_slug}")
    print(f"project_memory_root={paths.project_memory_root}")
    print(f"global_root={paths.global_root}")
    print(f"project_learnings={paths.project_learnings}")
    print(f"global_learnings={paths.global_shared_learnings}")
    return 0


def command_init(args: argparse.Namespace) -> int:
    paths = build_paths(args.project_root)
    bootstrap(paths)
    print(f"initialized project memory: {paths.project_memory_root}")
    print(f"initialized global memory: {paths.global_root}")
    return 0


def command_add(args: argparse.Namespace) -> int:
    paths = build_paths(args.project_root)
    bootstrap(paths)

    target = (
        paths.global_shared_learnings
        if args.scope == "global"
        else paths.project_learnings
    )
    base_id = f"{datetime.now().date().isoformat()}-{slugify(args.title)}"
    entry_id = ensure_unique_id(target, base_id)

    entry = {
        "id": entry_id,
        "kind": args.kind,
        "scope": args.scope,
        "project": paths.project_slug,
        "title": args.title,
        "summary": args.summary,
        "rule": args.rule,
        "confidence": round(args.confidence, 2),
        "tags": split_multi_values(args.tag),
        "files": split_multi_values(args.file),
        "source": args.source,
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "status": args.status,
    }

    append_jsonl(target, entry)
    refresh_catalog(paths)
    update_state(paths, write=True)
    print(f"added learning: {entry_id}")
    print(f"scope={args.scope}")
    print(f"file={target}")
    return 0


def command_search(args: argparse.Namespace) -> int:
    paths = build_paths(args.project_root)
    bootstrap(paths)

    tokens = [token.lower() for token in args.query.split() if token.strip()]
    sources: list[tuple[str, Path]] = []
    if args.scope in {"project", "both"}:
        sources.append(("project", paths.project_learnings))
    if args.scope in {"global", "both"}:
        sources.append(("global", paths.global_shared_learnings))

    matches: list[dict[str, Any]] = []
    for source_name, path in sources:
        for entry in read_jsonl(path):
            if args.kind and entry.get("kind") != args.kind:
                continue
            score = entry_score(entry, tokens)
            if tokens and score <= 0:
                continue
            matches.append(
                {
                    "score": score,
                    "source": source_name,
                    "entry": entry,
                }
            )

    matches.sort(
        key=lambda item: (
            item["score"],
            item["entry"].get("updated_at", ""),
        ),
        reverse=True,
    )

    for item in matches[: args.limit]:
        entry = item["entry"]
        print(
            f"[{item['score']:02d}] "
            f"[{item['source']}/{entry['kind']}] "
            f"{entry['id']} {entry['title']}"
        )
        print(f"  rule: {entry['rule']}")
        print(f"  tags: {', '.join(entry.get('tags', []))}")
        files = ", ".join(entry.get("files", []))
        if files:
            print(f"  files: {files}")

    update_state(paths, search=True)
    return 0


def command_promote(args: argparse.Namespace) -> int:
    paths = build_paths(args.project_root)
    bootstrap(paths)

    entries = read_jsonl(paths.project_learnings)
    target_entry = next(
        (entry for entry in entries if entry.get("id") == args.id),
        None,
    )
    if target_entry is None:
        raise SystemExit(f"learning not found: {args.id}")

    promoted = dict(target_entry)
    promoted["scope"] = "global"
    promoted["source"] = "promoted"
    promoted["promoted_at"] = now_iso()
    promoted["promoted_from"] = str(paths.project_learnings)
    promoted["updated_at"] = now_iso()
    promoted["id"] = ensure_unique_id(
        paths.global_shared_learnings,
        promoted["id"],
    )

    append_jsonl(paths.global_shared_learnings, promoted)
    update_state(paths, promote=True)
    print(f"promoted learning: {promoted['id']}")
    print(f"file={paths.global_shared_learnings}")
    return 0


def load_template(doc_kind: str) -> str:
    skill_root = Path(__file__).resolve().parent.parent
    template_path = skill_root / "assets" / f"{doc_kind}-template.md"
    return template_path.read_text(encoding="utf-8")


def command_new_doc(args: argparse.Namespace) -> int:
    paths = build_paths(args.project_root)
    bootstrap(paths)

    target_dir = (
        paths.project_solutions
        if args.doc_kind == "solution"
        else paths.project_decisions
    )
    title_slug = slugify(args.slug or args.title)
    filename = f"{datetime.now().date().isoformat()}-{title_slug}.md"
    target = target_dir / filename

    if target.exists():
        raise SystemExit(f"document already exists: {target}")

    template = load_template(args.doc_kind)
    content = template.format(
        title=args.title,
        project=paths.project_slug,
        created_at=now_iso(),
    )
    target.write_text(content, encoding="utf-8")
    refresh_catalog(paths)
    update_state(paths, write=True)
    print(f"created document: {target}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Experience memory helper for project and global learning.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    paths_parser = subparsers.add_parser("paths")
    paths_parser.add_argument("--project-root")
    paths_parser.set_defaults(func=command_paths)

    init_parser = subparsers.add_parser("init")
    init_parser.add_argument("--project-root")
    init_parser.set_defaults(func=command_init)

    add_parser = subparsers.add_parser("add")
    add_parser.add_argument("--project-root")
    add_parser.add_argument("--kind", choices=KIND_CHOICES, required=True)
    add_parser.add_argument("--title", required=True)
    add_parser.add_argument("--summary", required=True)
    add_parser.add_argument("--rule", required=True)
    add_parser.add_argument(
        "--scope",
        choices=("project", "global"),
        default="project",
    )
    add_parser.add_argument("--confidence", type=float, default=0.8)
    add_parser.add_argument("--source", default="observed")
    add_parser.add_argument("--status", default="active")
    add_parser.add_argument("--tag", action="append")
    add_parser.add_argument("--file", action="append")
    add_parser.set_defaults(func=command_add)

    search_parser = subparsers.add_parser("search")
    search_parser.add_argument("query")
    search_parser.add_argument("--project-root")
    search_parser.add_argument("--kind", choices=KIND_CHOICES)
    search_parser.add_argument(
        "--scope",
        choices=("project", "global", "both"),
        default="both",
    )
    search_parser.add_argument("--limit", type=int, default=5)
    search_parser.set_defaults(func=command_search)

    promote_parser = subparsers.add_parser("promote")
    promote_parser.add_argument("--project-root")
    promote_parser.add_argument("--id", required=True)
    promote_parser.set_defaults(func=command_promote)

    doc_parser = subparsers.add_parser("new-doc")
    doc_parser.add_argument("--project-root")
    doc_parser.add_argument(
        "--doc-kind",
        choices=DOC_KIND_CHOICES,
        required=True,
    )
    doc_parser.add_argument("--title", required=True)
    doc_parser.add_argument("--slug")
    doc_parser.set_defaults(func=command_new_doc)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
