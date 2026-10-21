#!/usr/bin/env bash
# HyperFrames 로컬 AI 기능 설치 (Linux/macOS)
#  - 음성 인식: whisper.cpp (whisper-cli)
#  - 음성 합성: Kokoro (kokoro-onnx) + espeak-ng (한국어 등 비영어 필수)
#  - 배경음악: MusicGen (transformers + torch)
# 모델 파일은 각 기능 첫 실행 시 자동 다운로드됩니다.
set -euo pipefail

PY="${HYPERFRAMES_PYTHON:-python3}"
PREFIX="${WHISPER_PREFIX:-/usr/local}"
SRC="${HOME}/.cache/hyperframes/whisper.cpp"

echo "==> espeak-ng"
if ! command -v espeak-ng >/dev/null; then
  if command -v apt-get >/dev/null; then
    SUDO=""; [ "$(id -u)" -ne 0 ] && SUDO="sudo"
    $SUDO apt-get update -qq && $SUDO apt-get install -y -qq espeak-ng
  elif command -v brew >/dev/null; then
    brew install espeak-ng
  fi
fi

echo "==> Python 패키지 (Kokoro, MusicGen)"
"$PY" -m pip install -q kokoro-onnx soundfile transformers torch numpy

echo "==> whisper.cpp"
if ! command -v whisper-cli >/dev/null; then
  if command -v brew >/dev/null; then
    brew install whisper-cpp
  else
    [ -d "$SRC" ] || git clone -q --depth 1 https://github.com/ggml-org/whisper.cpp "$SRC"
    cmake -S "$SRC" -B "$SRC/build" -DCMAKE_BUILD_TYPE=Release >/dev/null
    cmake --build "$SRC/build" --config Release -j >/dev/null
    SUDO=""; [ -w "$PREFIX/bin" ] || SUDO="sudo"
    $SUDO cmake --install "$SRC/build" --prefix "$PREFIX" >/dev/null
  fi
fi

echo "==> 확인"
npx --yes hyperframes doctor | grep -E 'whisper|TTS|BGM' || true
