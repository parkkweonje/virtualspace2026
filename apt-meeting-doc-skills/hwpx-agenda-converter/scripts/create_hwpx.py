#!/usr/bin/env python3
"""
안건제안서 HWPX 파일 생성 스크립트
삼부4단지 아파트 입주자대표회의 안건제안서 형식으로 HWPX 생성
"""

import zipfile
import json
import sys
import os
from datetime import datetime


# HWPX 네임스페이스
NS_HSP = "http://www.hancom.co.kr/hwpml/2012/section"
NS_HP = "http://www.hancom.co.kr/hwpml/2012/paragraph"
NS_HC = "http://www.hancom.co.kr/hwpml/2012/common"
NS_HH = "http://www.hancom.co.kr/hwpml/2012/head"


def make_paragraph_xml(text, style="본문", bold=False, center=False, indent=0, font_size=1000):
    """단락 XML 생성 (HWPX 형식)"""
    align = "Center" if center else "Justify"
    bold_val = "1" if bold else "0"
    indent_val = str(indent * 400)  # 1칸 = 400 unit

    return f'''<hp:P xmlns:hp="http://www.hancom.co.kr/hwpml/2012/paragraph" id="0" styleId="0">
      <hp:Run charPrIDRef="0">
        <hp:T>{text}</hp:T>
      </hp:Run>
    </hp:P>'''


def make_section_xml(agenda_data):
    """안건제안서 내용을 Section XML로 변환"""
    title = agenda_data.get("제목", "")
    proposer = agenda_data.get("제안자", "입주자대표회의")
    date = agenda_data.get("일자", datetime.now().strftime("%Y. %m. %d."))
    reason = agenda_data.get("제안이유", "")
    current_status = agenda_data.get("현황및문제점", "")
    budget = agenda_data.get("소요예산", "")
    effect = agenda_data.get("기대효과및향후계획", "")
    agenda_no = agenda_data.get("안건번호", "")

    paragraphs_xml = []

    def add_para(text, bold=False, center=False, indent=0):
        """단락 추가 헬퍼"""
        safe_text = str(text).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')
        paragraphs_xml.append(make_paragraph_xml(safe_text, bold=bold, center=center, indent=indent))

    # 제목 영역
    add_para("삼부4단지 아파트 입주자대표회의", bold=True, center=True)
    add_para("")
    add_para("안  건  제  안  서", bold=True, center=True)
    add_para("")

    # 안건 정보 테이블 대신 텍스트로 표현
    if agenda_no:
        add_para(f"안 건 번 호 : {agenda_no}", bold=False)
    add_para(f"제        목 : {title}", bold=True)
    add_para(f"제  안  자 : {proposer}")
    add_para(f"제 안 일 자 : {date}")
    add_para("")
    add_para("─" * 40)
    add_para("")

    # 1. 제안 이유
    add_para("1. 제안 이유", bold=True)
    add_para("")
    if reason:
        for line in reason.split('\n'):
            if line.strip():
                add_para(f"  {line.strip()}", indent=1)
    else:
        add_para("  (내용을 입력하세요)", indent=1)
    add_para("")

    # 2. 현황 및 문제점
    add_para("2. 현황 및 문제점", bold=True)
    add_para("")
    if current_status:
        for line in current_status.split('\n'):
            if line.strip():
                add_para(f"  {line.strip()}", indent=1)
    else:
        add_para("  (내용을 입력하세요)", indent=1)
    add_para("")

    # 3. 소요 예산
    add_para("3. 소요 예산", bold=True)
    add_para("")
    if budget:
        for line in budget.split('\n'):
            if line.strip():
                add_para(f"  {line.strip()}", indent=1)
    else:
        add_para("  (예산 내역 없음 또는 별도 산출)", indent=1)
    add_para("")

    # 4. 기대 효과 및 향후 계획
    add_para("4. 기대 효과 및 향후 계획", bold=True)
    add_para("")
    if effect:
        for line in effect.split('\n'):
            if line.strip():
                add_para(f"  {line.strip()}", indent=1)
    else:
        add_para("  (내용을 입력하세요)", indent=1)
    add_para("")

    add_para("─" * 40)
    add_para("")
    add_para(f"                                           끝.")
    add_para("")
    add_para(f"                          {date}")
    add_para(f"                          삼부4단지 아파트 입주자대표회의", bold=True)

    # Section XML 조합
    paragraphs_joined = '\n    '.join(paragraphs_xml)
    section_xml = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<hs:HSect xmlns:hs="http://www.hancom.co.kr/hwpml/2012/section"
          xmlns:hp="http://www.hancom.co.kr/hwpml/2012/paragraph"
          xmlns:hc="http://www.hancom.co.kr/hwpml/2012/common"
          version="1.3" subVersion="0">
    {paragraphs_joined}
</hs:HSect>'''
    return section_xml


def make_content_hpf():
    """content.hpf (헤더 파일) 생성"""
    return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<hh:Head xmlns:hh="http://www.hancom.co.kr/hwpml/2012/head"
         xmlns:hc="http://www.hancom.co.kr/hwpml/2012/common"
         version="1.3" subVersion="0">
  <hh:DocInfo>
    <hc:CaretPos listID="0" paraID="0" pos="0"/>
  </hh:DocInfo>
  <hh:DocBody>
    <hh:SectionList>
      <hh:Section start="0" path="BodyText/Section0.xml"/>
    </hh:SectionList>
  </hh:DocBody>
</hh:Head>'''


def make_container_xml():
    """META-INF/container.xml 생성"""
    return '''<?xml version="1.0" encoding="UTF-8"?>
<rootfiles xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfile full-path="Contents/content.hpf"
            media-type="application/hwp+zip"/>
</rootfiles>'''


def make_manifest_xml(sections=1):
    """META-INF/manifest.xml 생성"""
    section_entries = '\n'.join([
        f'  <file full-path="BodyText/Section{i}.xml" media-type="application/xml"/>'
        for i in range(sections)
    ])
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<manifest xmlns="urn:oasis:names:tc:opendocument:xmlns:manifest:1.0">
  <file full-path="/" media-type="application/hwp+zip"/>
  <file full-path="Contents/content.hpf" media-type="application/xml"/>
{section_entries}
  <file full-path="Preview/PrvText.txt" media-type="text/plain"/>
</manifest>'''


def create_hwpx(agenda_data, output_path):
    """안건제안서 HWPX 파일 생성"""
    section_xml = make_section_xml(agenda_data)
    content_hpf = make_content_hpf()
    container_xml = make_container_xml()
    manifest_xml = make_manifest_xml(sections=1)

    # 미리보기 텍스트
    preview_text = f"{agenda_data.get('제목', '')}\n삼부4단지 아파트 입주자대표회의 안건제안서"

    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as z:
        # mimetype은 반드시 첫 번째로, 압축 없이
        z.writestr(zipfile.ZipInfo('mimetype'), 'application/hwp+zip', compress_type=zipfile.ZIP_STORED)
        z.writestr('META-INF/container.xml', container_xml)
        z.writestr('META-INF/manifest.xml', manifest_xml)
        z.writestr('Contents/content.hpf', content_hpf)
        z.writestr('BodyText/Section0.xml', section_xml)
        z.writestr('Preview/PrvText.txt', preview_text)

    return output_path


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("사용법: python create_hwpx.py <agenda.json> <output.hwpx>")
        print("")
        print("agenda.json 형식:")
        print(json.dumps({
            "안건번호": "제X안",
            "제목": "안건 제목",
            "제안자": "입주자대표회의",
            "일자": "2026. 06. 11.",
            "제안이유": "제안 이유 텍스트",
            "현황및문제점": "현황 및 문제점 텍스트",
            "소요예산": "금 X,XXX,XXX원",
            "기대효과및향후계획": "기대 효과 및 향후 계획"
        }, ensure_ascii=False, indent=2))
        sys.exit(1)

    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        agenda_data = json.load(f)

    output_path = create_hwpx(agenda_data, sys.argv[2])
    print(f"HWPX 생성 완료: {output_path}")
