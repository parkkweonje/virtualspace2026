# CLAUDE.md

## ⚠️ 먼저 알아둘 것 — aptsojang.com 소스 위치
**aptsojang.com 은 이 저장소가 아니다.** Higgsfield 웹사이트 빌더로 만든 사이트이며,
소스는 GitHub이 아니라 Higgsfield 저장소에 있다. 계속 수정·운영하는 실사이트.

- 사이트: `ancient-mesa-109` / website_id: `1a976d4b-5bd4-4ef6-8711-d2170403cbc9`
- Higgsfield 사용자: `hfu-user3BjtPnyjmR21yupGPQY2qSWpzIG`
- Git repo: `apps-repos.higgsfield.ai/hfu-user3BjtPnyjmR21yupGPQY2qSWpzIG/ancient-mesa-109-1a976d4b-5bd4-4ef6-8711-d2170403cbc9.git` (branch `main`)
- 라이브: https://ancient-mesa-109.higgsfield.app → 커스텀 도메인 **aptsojang.com**
- 수정: Higgsfield MCP `list_websites` → `website_repo_access(website_id)`(토큰 발급) → clone/edit/push → `deploy_website`
- 주의: clone/push는 `apps-repos.higgsfield.ai` 접근 필요. **이 환경은 해당 도메인을 차단(403)** 하므로 편집은 higgsfield 접근이 허용된 세션에서 할 것.
- 상세: **[APTSOJANG_SITE_LOCATION.md](./APTSOJANG_SITE_LOCATION.md)** 참고.

## 이 저장소(virtualspace2026)는 무엇인가
- 대입 정보 정적 사이트. 배포 도메인: **daeip24.com** (`CNAME` 참고).
- 순수 정적 HTML/CSS/JS (수시·정시·의대·성적 계산 등 페이지). 브랜치 직접 배포(GitHub Pages, `.nojekyll`).

## 부가 자료
- `apt-meeting-doc-skills/` — 삼부4단지 입주자대표회의 문서 자동화 스킬 백업
  (공고문→회의록, 안건→안건제안서 생성 / HWPX 변환). 세션 임시 스킬이 사라지지 않도록 보관한 사본.
