# Remotion 영상 프로젝트

```bash
cd video
npm install
npm run studio   # 미리보기 (http://localhost:3000)
npm run render   # out/hello.mp4 렌더
```

- 컴포지션: `src/Root.tsx`, 샘플 씬: `src/HelloWorld.tsx` (1080x1920, 30fps, 3초)
- 브라우저 다운로드가 막힌 환경: `REMOTION_BROWSER=/path/to/chrome npm run render`
