#!/usr/bin/env python3
"""
Module content validation script.
Run before committing to learning-modules repo to catch:
- Orphaned assessment exercise references
- Asset checksum mismatches
- Markdown images without corresponding files
- Missing required fields
- Diagram edge integrity
- Flashcard completeness

Usage: python3 validate.py [--ci]
  --ci: exit non-zero on errors (for GitHub Actions)
"""

import json, os, re, hashlib, sys
from pathlib import Path
from collections import defaultdict

REPO = Path(__file__).resolve().parent
MODULES_JSON = REPO / 'modules.json'
MODULES_DIR = REPO / 'modules'

errors = []
warnings = []
stats = defaultdict(int)
is_ci = '--ci' in sys.argv

def err(msg, path=None):
    errors.append(f"{path + ': ' if path else ''}{msg}")
def warn(msg, path=None):
    warnings.append(f"{path + ': ' if path else ''}{msg}")

# ── Load index ──────────────────────────────────────────────────────
if not MODULES_JSON.exists():
    err("modules.json not found"); sys.exit(1)

with open(MODULES_JSON) as f:
    index = json.load(f)

stats['modules_in_index'] = len(index.get('modules', []))

# ── Index structure ─────────────────────────────────────────────────
if 'version' not in index: err("index missing 'version' field")
if 'lastUpdated' not in index: err("index missing 'lastUpdated' field")
if 'modules' not in index: err("index missing 'modules' array")

seen_ids = set()
for i, entry in enumerate(index.get('modules', [])):
    mid = entry.get('id', f'entry[{i}]')
    path = f"modules.json › {mid}"
    stats['total_entries'] += 1

    for field in ['id', 'title', 'version', 'checksum', 'downloadUrl']:
        if not entry.get(field):
            err(f"missing required field '{field}'", path)

    if mid in seen_ids:
        err(f"duplicate module ID", path)
    seen_ids.add(mid)

    chk = entry.get('checksum', '')
    if chk and not chk.startswith('sha256:'):
        err(f"checksum must start with 'sha256:'", path)

    ver = entry.get('version', '')
    if ver and not re.match(r'^\d+\.\d+\.\d+$', ver):
        warn(f"non-semver version '{ver}'", path)

    url = entry.get('downloadUrl', '')
    if url and not url.startswith('https://'):
        err(f"downloadUrl not HTTPS", path)

    # ── Module.json existence + checksum ─────────────────────────
    module_file = MODULES_DIR / mid / 'module.json'
    if module_file.exists():
        with open(module_file, 'rb') as f:
            actual = hashlib.sha256(f.read()).hexdigest()
        expected = chk.replace('sha256:', '')
        if actual != expected:
            err(f"module.json checksum mismatch: declared={expected[:12]}… actual={actual[:12]}…", path)
        else:
            stats['checksums_valid'] += 1
    else:
        err(f"module.json not found at {MODULES_DIR/mid/'module.json'}", path)
        continue

    with open(module_file) as f:
        try:
            module = json.load(f)
        except json.JSONDecodeError as e:
            err(f"invalid JSON: {e}", path)
            continue

    # ── Assessment referential integrity ─────────────────────────
    section_ex_ids = set()
    for s in module.get('sections', []):
        for ex in s.get('exercises', []):
            eid = ex.get('id', '')
            if eid:
                section_ex_ids.add(eid)

    assessment = module.get('assessment', {})
    for aex in assessment.get('exercises', []):
        ref_id = aex.get('exerciseId', '')
        if ref_id and ref_id not in section_ex_ids:
            err(f"assessment references orphaned exercise '{ref_id}'", path)
        stats['assessment_refs'] += 1

    # ── Exercise count ──────────────────────────────────────────
    total_ex = sum(len(s.get('exercises', [])) for s in module.get('sections', []))
    stats['total_exercises'] += total_ex
    if total_ex == 0:
        warn("zero exercises", path)

    # ── Assets ──────────────────────────────────────────────────
    declared_assets = {a['path']: a.get('checksum', '') for a in entry.get('assets', [])}
    stats['declared_assets'] += len(declared_assets)

    for apath, achk in declared_assets.items():
        afile = MODULES_DIR / mid / apath
        if not afile.exists():
            err(f"declared asset not found: {apath}", path)
        elif achk:
            with open(afile, 'rb') as f:
                actual = hashlib.sha256(f.read()).hexdigest()
            expected = achk.replace('sha256:', '')
            if actual != expected:
                err(f"asset checksum mismatch: {apath}", path)
            else:
                stats['asset_checksums_valid'] += 1

    # ── Markdown image references ───────────────────────────────
    img_refs = set()
    for s in module.get('sections', []):
        for l in s.get('lessons', []):
            for match in re.finditer(r'!\[.*?\]\(([^)]+)\)', l.get('content', '')):
                img_refs.add(match.group(1))

    for ref in img_refs:
        ref_path = MODULES_DIR / mid / ref
        if not ref_path.exists():
            if ref not in declared_assets:
                err(f"markdown image '{ref}' not on disk and not in asset manifest", f"{path} › {ref}")
            else:
                warn(f"markdown image '{ref}' in asset manifest but file not found locally (download-only)", f"{path} › {ref}")
        else:
            stats['markdown_images_found'] += 1

    # ── Prerequisite chain ──────────────────────────────────────
    for prereq in module.get('prerequisites', []):
        if prereq not in seen_ids:
            warn(f"prerequisite '{prereq}' not in index", path)

    # ── Flashcards ──────────────────────────────────────────────
    deck = module.get('flashcardDeck', {})
    for card in deck.get('cards', []):
        if not card.get('term'):
            warn(f"flashcard missing 'term'", path)
        if not card.get('definition'):
            warn(f"flashcard '{card.get('term','?')}' missing 'definition'", path)
        stats['flashcard_cards'] += 1

    # ── Diagram edges ───────────────────────────────────────────
    for s in module.get('sections', []):
        for l in s.get('lessons', []):
            for diag in l.get('diagrams', []):
                node_ids = {n['id'] for n in diag.get('nodes', [])}
                for edge in diag.get('edges', []):
                    if edge.get('from') not in node_ids:
                        err(f"diagram edge from='{edge['from']}' references nonexistent node", 
                            f"{path} › {l.get('title','?')} › {diag.get('id','?')}")
                    if edge.get('to') not in node_ids:
                        err(f"diagram edge to='{edge['to']}' references nonexistent node",
                            f"{path} › {l.get('title','?')} › {diag.get('id','?')}")

# ── Report ──────────────────────────────────────────────────────────
WIDTH = 60
print("=" * WIDTH)
print("  MODULE CONTENT VALIDATION")
print("=" * WIDTH)
print(f"\n  {'Stat':<40} {'Count'}")
print(f"  {'-'*40} {'-'*6}")
for k, v in sorted(stats.items()):
    print(f"  {k:<40} {v}")
print(f"\n  Errors:   {len(errors)}")
print(f"  Warnings: {len(warnings)}")

if errors:
    print(f"\n{'─' * WIDTH}")
    print("  ERRORS:")
    for e in errors:
        print(f"  ❌ {e}")
if warnings:
    print(f"\n{'─' * WIDTH}")
    print("  WARNINGS:")
    for w in warnings:
        print(f"  ⚠️  {w}")

if errors:
    print(f"\n  🔴 {len(errors)} errors — {'BLOCKING' if is_ci else 'must fix before deploy'}")
    if is_ci:
        sys.exit(1)
else:
    print(f"\n  🟢 All checks passed")
