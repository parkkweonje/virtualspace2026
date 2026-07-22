#!/usr/bin/env python3
"""HWPX(ZIP 기반) 파일에서 텍스트를 추출해 JSON으로 저장.
사용법: python extract_hwpx.py <입력.hwpx> <출력.json>
"""
import sys, json, zipfile, re
import xml.etree.ElementTree as ET


def extract(path: str) -> dict:
    result = {"source": path, "paragraphs": [], "preview": ""}
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        # 1) Contents/section*.xml 에서 본문 추출
        sections = sorted(n for n in names if re.match(r"Contents/section\d+\.xml", n))
        for sec in sections:
            try:
                xml = z.read(sec).decode("utf-8", errors="ignore")
                # 네임스페이스 무시하고 <hp:t> 텍스트 노드 수집
                root = ET.fromstring(xml)
                for p in root.iter():
                    if p.tag.endswith("}p"):
                        texts = [t.text for t in p.iter() if t.tag.endswith("}t") and t.text]
                        line = "".join(texts).strip()
                        if line:
                            result["paragraphs"].append(line)
            except Exception as e:
                print(f"[warn] {sec}: {e}", file=sys.stderr)
        # 2) fallback: Preview/PrvText.txt
        for cand in ("Preview/PrvText.txt", "PrvText.txt"):
            if cand in names:
                try:
                    result["preview"] = z.read(cand).decode("utf-16", errors="ignore").strip()
                except Exception:
                    result["preview"] = z.read(cand).decode("utf-8", errors="ignore").strip()
                break
    return result


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("사용법: python extract_hwpx.py <입력.hwpx> <출력.json>")
        sys.exit(1)
    data = extract(sys.argv[1])
    with open(sys.argv[2], "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"추출 완료: 문단 {len(data['paragraphs'])}개, preview {'있음' if data['preview'] else '없음'}")
