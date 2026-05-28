#!/usr/bin/env python3
"""
Regenerates modules.json from all module.json files in modules/*/.

Validates:
  - Required fields (id, title, description, version, author, sections)
  - At least one section with at least one lesson
  - All exercise types are recognized
  - Assessment questions have valid correctIndex
  - SHA-256 checksums are fresh

Usage:
  python3 tools/update_index.py          # regenerate modules.json
  python3 tools/update_index.py --check  # validate only, don't write
"""

import hashlib
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MODULES_DIR = ROOT / "modules"
INDEX_FILE = ROOT / "modules.json"

VALID_EXERCISE_TYPES = {"mcq", "worked_example", "socratic", "drag_sequence", "error_spotting"}
REQUIRED_MODULE_FIELDS = {"id", "title", "description", "version", "author", "sections"}
REQUIRED_SECTION_FIELDS = {"id", "title", "order", "lessons"}
REQUIRED_LESSON_FIELDS = {"id", "title", "content"}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def validate_module(data: dict, path: Path) -> list[str]:
    """Validate a parsed module.json. Returns list of errors (empty = valid).."""
    errors = []

    # Required fields
    missing = REQUIRED_MODULE_FIELDS - set(data.keys())
    if missing:
        errors.append(f"{path}: missing fields: {missing}")
        return errors  # can't validate further without basics

    # Sections
    sections = data.get("sections", [])
    if not sections:
        errors.append(f"{path}: no sections defined")
        return errors

    section_ids = set()
    for i, section in enumerate(sections):
        s_missing = REQUIRED_SECTION_FIELDS - set(section.keys())
        if s_missing:
            errors.append(f"{path}: section[{i}] missing fields: {s_missing}")

        sid = section.get("id", f"section[{i}]")
        if sid in section_ids:
            errors.append(f"{path}: duplicate section id '{sid}'")
        section_ids.add(sid)

        # Lessons
        lessons = section.get("lessons", [])
        if not lessons:
            errors.append(f"{path}: section '{sid}' has no lessons")

        for j, lesson in enumerate(lessons):
            l_missing = REQUIRED_LESSON_FIELDS - set(lesson.keys())
            if l_missing:
                errors.append(f"{path}: section '{sid}' lesson[{j}] missing fields: {l_missing}")

            # Exercises
            for k, ex in enumerate(lesson.get("exercises", [])):
                etype = ex.get("type")
                if etype and etype not in VALID_EXERCISE_TYPES:
                    errors.append(f"{path}: {sid}/{lesson.get('id', j)}/exercise[{k}] unknown type '{etype}'")

                if etype == "mcq":
                    ci = ex.get("correctIndex")
                    opts = ex.get("options", [])
                    if ci is not None and (ci < 0 or ci >= len(opts)):
                        errors.append(f"{path}: {sid}/exercise[{k}] correctIndex {ci} out of range (0..{len(opts)-1})")

                if etype == "drag_sequence":
                    items = ex.get("items", [])
                    order = ex.get("correctOrder", [])
                    if len(items) != len(order):
                        errors.append(f"{path}: {sid}/exercise[{k}] drag_sequence items/order length mismatch")

            # Flashcards
            for fc in lesson.get("flashcards", []):
                if "term" not in fc or "definition" not in fc:
                    errors.append(f"{path}: {sid}/{lesson.get('id', j)} flashcard missing term/definition")

        # Assessment
        assessment = section.get("assessment")
        if assessment:
            for q in assessment.get("questions", []):
                ci = q.get("correctIndex")
                opts = q.get("options", [])
                if ci is not None and opts and (ci < 0 or ci >= len(opts)):
                    errors.append(f"{path}: {sid} assessment question '{q.get('id', '?')}' correctIndex out of range")
                if not q.get("text"):
                    errors.append(f"{path}: {sid} assessment question '{q.get('id', '?')}' missing text")

    return errors


def main():
    check_only = "--check" in sys.argv

    all_errors = []
    module_entries = []

    # Find all modules
    if not MODULES_DIR.exists():
        print("ERROR: modules/ directory not found")
        sys.exit(1)

    for module_dir in sorted(MODULES_DIR.iterdir()):
        if not module_dir.is_dir():
            continue
        module_file = module_dir / "module.json"
        if not module_file.exists():
            continue

        print(f"Validating {module_dir.name}/module.json ...")

        try:
            data = json.loads(module_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            all_errors.append(f"{module_file}: invalid JSON: {e}")
            continue

        errors = validate_module(data, module_file)
        all_errors.extend(errors)

        if not errors:
            checksum = sha256_file(module_file)
            download_url = f"https://raw.githubusercontent.com/DuaneJaspers/learning-modules/main/{data['id']}/module.json"
            module_entries.append({
                "id": data["id"],
                "title": data["title"],
                "description": data["description"],
                "author": data.get("author", ""),
                "version": data.get("version", "1.0.0"),
                "estimatedMinutes": data.get("estimatedMinutes", 60),
                "checksum": f"sha256:{checksum}",
                "downloadUrl": download_url,
            })

    # Report
    if all_errors:
        print(f"\n❌ {len(all_errors)} validation error(s):")
        for err in all_errors:
            print(f"  • {err}")
        sys.exit(1)

    print(f"\n✅ All {len(module_entries)} modules valid")

    # Generate index
    from datetime import datetime, timezone
    index = {
        "version": "1",
        "lastUpdated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "modules": module_entries,
    }

    if check_only:
        # Compare with existing
        if INDEX_FILE.exists():
            existing = json.loads(INDEX_FILE.read_text(encoding="utf-8"))
            if existing.get("modules") == index["modules"]:
                print("modules.json is up to date")
            else:
                print("modules.json is STALE — needs regeneration")
                sys.exit(1)
        else:
            print("modules.json does not exist")
            sys.exit(1)
    else:
        INDEX_FILE.write_text(json.dumps(index, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"Updated modules.json ({len(module_entries)} modules)")


if __name__ == "__main__":
    main()
