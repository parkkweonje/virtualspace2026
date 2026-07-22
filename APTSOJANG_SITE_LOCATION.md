# aptsojang.com — 소스 위치 (영구 기록)

> **이 파일의 목적:** aptsojang.com 사이트의 소스가 어디에 있는지 다시는 잃어버리지 않도록
> 좌표를 GitHub에 박아둔다. 세션이 초기화돼도 이 파일만 보면 바로 찾아 이어서 수정할 수 있다.
> 계속 수정·운영하는 실사이트임.

## 한 줄 요약
aptsojang.com 은 **Higgsfield 웹사이트 빌더**로 만든 사이트이며, 소스는 GitHub이 아니라
**Higgsfield 저장소**에 있다. (그래서 이 daeip24/virtualspace2026 저장소에는 코드가 없다.)

## 좌표
| 항목 | 값 |
|---|---|
| 서비스 도메인 | https://aptsojang.com (Higgsfield 사이트에 연결한 커스텀 도메인) |
| 플랫폼 | Higgsfield (website builder) |
| 사이트 이름/slug | `ancient-mesa-109` |
| website_id | `1a976d4b-5bd4-4ef6-8711-d2170403cbc9` |
| Higgsfield 사용자 | `hfu-user3BjtPnyjmR21yupGPQY2qSWpzIG` |
| Git 저장소 | `https://apps-repos.higgsfield.ai/hfu-user3BjtPnyjmR21yupGPQY2qSWpzIG/ancient-mesa-109-1a976d4b-5bd4-4ef6-8711-d2170403cbc9.git` (branch: `main`) |
| 배포 URL | https://ancient-mesa-109.higgsfield.app |
| 생성일 | 2026-07-06 |

> 접근 토큰은 매번 바뀌므로 여기 저장하지 않는다. 아래 절차로 그때그때 새로 발급받는다.

## 수정·배포 방법 (Higgsfield MCP)
1. `list_websites` → website_id 확인 (`1a976d4b-5bd4-4ef6-8711-d2170403cbc9`)
2. `website_repo_access(website_id)` → repo_url + 그 순간용 토큰 발급
3. 발급된 토큰으로 clone:
   `git -c http.extraHeader="Authorization: token <TOKEN>" clone <repo_url> ancient-mesa-109`
4. 파일 수정 → commit → 같은 헤더로 `push origin main`
   - 앱 레이아웃 수정 전 `app/src/layouts/AGENTS.md`, `app/src/components/AGENTS.md` 먼저 읽기 (홈 화면 처음부터 새로 만들지 말 것)
5. `deploy_website(website_id)` → 라이브 반영. `website_status(website_id)`로 확인.

## ⚠️ 환경 주의 (중요)
- clone/push는 `apps-repos.higgsfield.ai` 도메인에 붙어야 한다.
- **이 환경(virtualspace2026 / daeip24.com용)은 네트워크 정책상 그 도메인을 차단(403)한다.**
  따라서 여기서는 코드를 clone 하거나 편집할 수 없다.
- 편집이 필요하면 **higgsfield 도메인 접근이 허용된 환경/세션**에서 위 절차를 수행할 것.
- Higgsfield MCP 도구(list_websites / website_repo_access / deploy_website 등) 자체는
  MCP 서버를 통하므로 대부분 환경에서 동작한다. 막히는 건 "직접 git clone" 단계뿐이다.

## GitHub 백업 하려면
higgsfield 접근이 되는 환경에서 위 3번으로 clone 한 뒤, 이 저장소(또는 새 repo)에
소스를 복사해 커밋하면 GitHub에도 사본이 남는다. (현재 환경에서는 clone이 막혀 미완료 상태.)

---
_최종 확인: 2026-07-22 — 사이트 production_deployed=true (라이브 정상)._
