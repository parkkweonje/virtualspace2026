# 🧭 입시나침반 (Ipsi Compass)

수능·대학입시 정보를 쉽고 정확하게 전하는 **정적(static) 웹사이트**입니다.
자기소개서 작성, 대학정보, 지역의사제, 의치한약수 등 대학입시에 필요한 정보를
한 곳에 모았습니다.

## 📄 페이지 구성

| 파일 | 내용 |
|------|------|
| `index.html` | 홈 — 수능 D-day 카운터, 핵심 메뉴, 통계 |
| `jaso.html` | 자기소개서 작성 — 5단계 프로세스, 문항별 전략, 좋은/나쁜 예시, 최종 체크리스트 |
| `universities.html` | 대학정보 — 대학 검색·지역/유형 필터 |
| `medical.html` | 의치한약수 — 의·치·한·약·수 계열별 학제·과목·모집대학 |
| `regional.html` | 지역의사제 — 지역인재전형/지역의사제 개념, 권역별 대학, FAQ |
| `admission.html` | 입시전형 — 수시·정시 구조, 전형별 설명, 연간 일정 |
| `calculator.html` | 합격 진단 — 내신·계열 입력 → 안정/적정/도전/상향 진단 |
| `compare.html` | 대학 비교표 — 관심 대학 선택 후 나란히 비교 |
| `community.html` | 커뮤니티 — 질문·정보·후기 게시판(브라우저 저장) |

## 🗂 폴더 구조

```
.
├── index.html            # 홈
├── jaso.html             # 자소서 작성
├── universities.html     # 대학정보
├── medical.html          # 의치한약수
├── regional.html         # 지역의사제
├── admission.html        # 입시전형
├── css/
│   └── style.css         # 공통 디자인 시스템
├── js/
│   ├── data.js           # 대학·의치한약수·일정 데이터
│   └── main.js           # D-day, 네비, 아코디언, 필터, 체크리스트
└── README.md
```

## 🚀 실행 방법

빌드 과정이 없는 순수 HTML/CSS/JS 사이트입니다. 별도 설치 없이 바로 열립니다.

```bash
# 방법 1) 파일을 브라우저로 바로 열기
open index.html          # macOS

# 방법 2) 간단한 로컬 서버 (권장 — JS가 정상 동작)
python3 -m http.server 8000
# → 브라우저에서 http://localhost:8000 접속
```

## 🌐 배포 (GitHub Pages)

`.github/workflows/deploy.yml` 이 포함되어 있어, **`main` 브랜치에 push되면**
자동으로 GitHub Pages에 배포됩니다.

워크플로의 `configure-pages` 단계에 `enablement: true` 가 설정되어 있어,
**최초 실행 시 Pages 설정이 자동으로 켜집니다** (별도 수동 설정 불필요).
배포가 끝나면 Actions 로그와 저장소 **Settings → Pages** 에서 공개 URL을 확인할 수 있습니다.

> 조직 정책 등으로 자동 활성화가 막혀 있다면, 저장소 **Settings → Pages → Source** 를
> **GitHub Actions** 로 한 번만 수동 설정해 주세요.

## 🛠 기술 스택

- **HTML5 / CSS3 / Vanilla JavaScript** (프레임워크·빌드 도구 없음)
- 웹폰트: [Pretendard](https://github.com/orioncactus/pretendard) (CDN)
- 데이터는 `js/data.js`에서 관리 → 내용 수정이 쉬움

## ✏️ 내용 수정 가이드

- **대학 추가/수정**: `js/data.js`의 `UNIVERSITIES` 배열 편집
- **의치한약수 정보**: `js/data.js`의 `MEDICAL` 객체 편집
- **수능 날짜/일정**: `js/data.js`의 `EXAM_DATE`, `KEY_DATES` 수정
- **지역 권역**: `js/data.js`의 `REGIONAL` 편집

## ⚠️ 안내

수록된 정보(대학·전형·커트라인·일정)는 **학습·안내용 예시**입니다.
실제 모집요강과 일정은 반드시 각 대학 입학처와 아래 공식 기관에서 확인하세요.

- [대입정보포털 어디가](https://www.adiga.kr)
- [한국대학교육협의회](https://www.kcue.or.kr)
- [한국교육과정평가원(수능)](https://www.suneung.re.kr)

---

© 2026 입시나침반 (Ipsi Compass) · 학습·정보 제공용 사이트
