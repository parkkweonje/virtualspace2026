#!/usr/bin/env python3
"""
HWPX 파일에서 텍스트를 추출하는 스크립트
HWPX는 ZIP 기반 포맷으로, BodyText/Section*.xml 에 본문이 있습니다.
"""

import zipfile
import xml.etree.ElementTree as ET
import sys
import json
import re
import os


def clean_text(text):
    """텍스트 정리: 불필요한 공백 제거"""
    if not text:
        return ""
    return re.sub(r'\s+', ' ', text).strip()


def extract_text_from_section_xml(xml_content):
    """Section XML에서 단락별 텍스트 추출"""
    paragraphs = []
    try:
        # 네임스페이스 제거하여 파싱 단순화
        clean_xml = re.sub(r' xmlns[^"]*"[^"]*"', '', xml_content)
        clean_xml = re.sub(r'<[a-z]+:', '<', clean_xml)
        clean_xml = re.sub(r'</[a-z]+:', '</', clean_xml)

        root = ET.fromstring(clean_xml)

        for p in root.iter('P'):
            para_texts = []
            for t in p.iter('T'):
                if t.text:
                    para_texts.append(t.text)

            para_line = ''.join(para_texts)
            para_line = clean_text(para_line)
            if para_line:
                paragraphs.append(para_line)

    except ET.ParseError as e:
        # XML 파싱 실패시 정규식으로 텍스트 추출
        text_matches = re.findall(r'<[a-z]+:T[^>]*>([^<]+)</[a-z]+:T>', xml_content)
        for t in text_matches:
            cleaned = clean_text(t)
            if cleaned:
                paragraphs.append(cleaned)

    return paragraphs


def extract_hwpx(hwpx_path):
    """HWPX 파일에서 전체 텍스트 추출"""
    result = {
        "file": os.path.basename(hwpx_path),
        "paragraphs": [],
        "raw_text": ""
    }

    if not os.path.exists(hwpx_path):
        result["error"] = f"파일을 찾을 수 없습니다: {hwpx_path}"
        return result

    try:
        with zipfile.ZipFile(hwpx_path, 'r') as z:
            namelist = z.namelist()

            # BodyText 폴더의 Section XML 파일들 처리
            section_files = sorted([
                n for n in namelist
                if 'BodyText' in n and n.endswith('.xml')
            ])

            if not section_files:
                # 다른 경로도 시도
                section_files = sorted([
                    n for n in namelist
                    if 'section' in n.lower() and n.endswith('.xml')
                ])

            all_paragraphs = []
            for section_file in section_files:
                with z.open(section_file) as f:
                    xml_content = f.read().decode('utf-8', errors='ignore')
                    paras = extract_text_from_section_xml(xml_content)
                    all_paragraphs.extend(paras)

            result["paragraphs"] = all_paragraphs
            result["raw_text"] = '\n'.join(all_paragraphs)

            if not all_paragraphs:
                # PrvText.txt (미리보기 텍스트) 시도
                if 'Preview/PrvText.txt' in namelist:
                    with z.open('Preview/PrvText.txt') as f:
                        result["raw_text"] = f.read().decode('utf-8', errors='ignore')
                        result["paragraphs"] = [
                            line.strip() for line in result["raw_text"].split('\n')
                            if line.strip()
                        ]

    except zipfile.BadZipFile:
        result["error"] = "유효한 HWPX 파일이 아닙니다."
    except Exception as e:
        result["error"] = f"파일 읽기 오류: {str(e)}"

    return result


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("사용법: python extract_hwpx.py <hwpx_file> [output.json]")
        sys.exit(1)

    hwpx_path = sys.argv[1]
    result = extract_hwpx(hwpx_path)

    if len(sys.argv) >= 3:
        with open(sys.argv[2], 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"추출 완료: {sys.argv[2]}")
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))
