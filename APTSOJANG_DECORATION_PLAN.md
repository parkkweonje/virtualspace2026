# aptsojang.com 이미지 꾸미기 — 작업 계획 & 생성 에셋

> 이 환경(daeip24 샌드박스)은 higgsfield/CloudFront 도메인을 모두 차단하므로
> **사이트 편집은 여기서 불가**. 아래 에셋과 계획을 가지고 **higgsfield 접근이 되는
> 세션**에서 완성한다. (사이트 좌표는 `APTSOJANG_SITE_LOCATION.md` 참고.)

## 이미 생성한 에셋 (Higgsfield 계정에 저장됨)
모델: `nano_banana_pro` (nano_banana_2) · 16:9 · "산뜻/밝은" 톤

| 용도 | job_id | 프롬프트 요지 |
|---|---|---|
| 히어로 A | `ff90fb85-2605-4558-a05b-13695b0eb121` | 맑은 날 모던 고층 아파트 단지, 파스텔 블루/그린, 상단 여백(헤드라인용) |
| 히어로 B | `71dc47a6-fd98-41b3-bd13-3edc866a11b7` | (동일 프롬프트 변형) |

> Higgsfield 세션에서 `job_display <id>` 또는 갤러리에서 확인 가능.
> 사이트에 넣을 때는 그 세션에서 CDN URL을 받아 repo에 다운로드 → 커밋.

## 아직 안 만든 것 (다음 세션에서 생성 권장)
- 섹션 아이콘/이미지: ① 회의록·안건 서류 자동화(깔끔한 플랫레이) ② 관리사무소/입주자대표회의 커뮤니티 ③ 섹션 구분용 부드러운 추상 배경
- 파비콘/로고 (선택)

## 적용 절차 (higgsfield 접근 세션에서)
1. `website_repo_access(1a976d4b-5bd4-4ef6-8711-d2170403cbc9)` → 토큰·repo
2. clone → `app/src/layouts/AGENTS.md`, `app/src/components/AGENTS.md` 먼저 읽기
3. 히어로/섹션 이미지 파일을 `public/`(또는 assets 경로)에 넣고 컴포넌트에서 참조
4. `git push origin main` → `deploy_website(1a976d4b-...)` → `website_status`로 확인

## 디자인 방향 (합의된 톤)
- 키워드: **산뜻·밝음·신뢰감**. 파스텔 라이트블루 + 화이트 + 프레시 그린.
- 아파트 관리/입주자대표회의 문서 자동화 서비스에 맞는 전문적이고 깨끗한 무드.
