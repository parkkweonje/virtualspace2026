# aptsojang.com 이미지 꾸미기 — 작업 계획 & 생성 에셋

> 이 환경(daeip24 샌드박스)은 higgsfield/CloudFront 도메인을 모두 차단하므로
> **사이트 편집은 여기서 불가**. 아래 에셋과 계획을 가지고 **higgsfield 접근이 되는
> 세션**에서 완성한다. (사이트 좌표는 `APTSOJANG_SITE_LOCATION.md` 참고.)

## 생성 완료 에셋 (Higgsfield 계정에 저장됨)
모델: `nano_banana_pro` (nano_banana_2) · "산뜻/밝은" 파스텔 블루·그린 톤. 모두 1k.

| 용도 | 비율 | job_id | 채택 |
|---|---|---|---|
| 히어로 A (데스크탑) | 16:9 | `ff90fb85-2605-4558-a05b-13695b0eb121` | |
| **히어로 B (데스크탑)** | 16:9 | `71dc47a6-fd98-41b3-bd13-3edc866a11b7` | ✅ **사용자 채택** |
| 섹션 — 문서 자동화 플랫레이 | 16:9 | `440e74ab-8a6e-41c6-898b-137c2f35f067` | |
| 섹션 — 대표회의/커뮤니티 공간 | 16:9 | `e5699aa6-01e4-4373-8e29-88b75c38f7fc` | |
| 섹션 구분 추상 배경 | 16:9 | `0d1d0f12-759b-4457-a810-380ea7a81a8d` | |
| 모바일 세로 히어로 | 9:16 | `1a2e208e-8039-436f-b2b9-e14076aebf0d` | |

> Higgsfield 세션에서 `job_display <id>` 또는 갤러리에서 확인 가능.
> 사이트에 넣을 때는 그 세션에서 CDN URL(rawUrl)을 받아 repo에 다운로드 → 커밋.

## 추가 생성 후보 (선택)
- 파비콘/로고, 각 서비스 기능별 아이콘 세트

## 적용 절차 (higgsfield 접근 세션에서)
1. `website_repo_access(1a976d4b-5bd4-4ef6-8711-d2170403cbc9)` → 토큰·repo
2. clone → `app/src/layouts/AGENTS.md`, `app/src/components/AGENTS.md` 먼저 읽기
3. 히어로/섹션 이미지 파일을 `public/`(또는 assets 경로)에 넣고 컴포넌트에서 참조
4. `git push origin main` → `deploy_website(1a976d4b-...)` → `website_status`로 확인

## 디자인 방향 (합의된 톤)
- 키워드: **산뜻·밝음·신뢰감**. 파스텔 라이트블루 + 화이트 + 프레시 그린.
- 아파트 관리/입주자대표회의 문서 자동화 서비스에 맞는 전문적이고 깨끗한 무드.
