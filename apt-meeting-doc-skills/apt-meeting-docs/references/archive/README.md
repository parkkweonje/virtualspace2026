# 아카이브 폴더 구조

- agendas/{연도}/{회차}_{안건번호}_{제목}.md — 안건 및 안건자료
- minutes/{연도}/{회차}_회의록.md — 회의록

각 md 파일은 YAML frontmatter(type, year, session, date, title, category, keywords 등) 필수.
파일 추가·수정 후 반드시 scripts/build_index.py 로 index.json 재생성.
