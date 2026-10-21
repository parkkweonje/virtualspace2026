# HyperFrames 영상 프로젝트

HTML + GSAP으로 작성하고 MP4로 렌더하는 프로젝트입니다.

```bash
cd hyperframes
npm install
npm run dev      # 미리보기 (Studio)
npm run check    # 검사
npm run render   # renders/ 에 MP4 렌더
```

- 컴포지션: `index.html` (1080x1920, 3초 샘플)
- 처음 렌더 시 Chrome Headless Shell을 자동으로 받습니다 (`npx hyperframes browser ensure`)
- 에이전트 스킬: 저장소 루트 `.claude/skills/` (`/hyperframes` 부터 시작)
