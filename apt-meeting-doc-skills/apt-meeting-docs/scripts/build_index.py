#!/usr/bin/env python3
"""archive/ 하위의 .md 파일 YAML 메타데이터를 스캔해 index.json 생성.
사용법: python build_index.py <archive경로>
"""
import sys, json, re
from pathlib import Path


def parse_frontmatter(text: str) -> dict:
    m = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if not m:
        return {}
    meta = {}
    for line in m.group(1).splitlines():
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        k, v = k.strip(), v.split("#")[0].strip()
        if v.startswith("[") and v.endswith("]"):
            meta[k] = [x.strip() for x in v[1:-1].split(",") if x.strip()]
        else:
            meta[k] = v
    return meta


def main(archive: Path):
    entries = []
    for md in sorted(archive.rglob("*.md")):
        if md.name.lower() == "readme.md":
            continue
        try:
            meta = parse_frontmatter(md.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"[warn] {md}: {e}", file=sys.stderr)
            continue
        if not meta:
            continue
        meta["path"] = str(md.relative_to(archive))
        entries.append(meta)

    entries.sort(key=lambda e: (e.get("date", ""), e.get("session", "")), reverse=True)
    index = {
        "updated_entries": len(entries),
        "agendas": [e for e in entries if e.get("type") == "agenda"],
        "minutes": [e for e in entries if e.get("type") == "minutes"],
    }
    out = archive / "index.json"
    out.write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"index.json 생성: 안건 {len(index['agendas'])}건, 회의록 {len(index['minutes'])}건")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("사용법: python build_index.py <archive경로>")
        sys.exit(1)
    main(Path(sys.argv[1]))
