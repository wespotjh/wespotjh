#!/usr/bin/env bash
# 젠제네틱스 카페24 상세 회귀 테스트 — 한 번에 전부 돌리는 진입점.
#   ./run.sh              전체 (A 보존 · B 정적 · C 실렌더 · D 계측 · E 라이브대조)
#   ./run.sh --fast       정적만 (A·B) — 브라우저·네트워크 안 씀
#   ./run.sh --only C,D   골라서
#   ./run.sh --refresh    라이브 응답 재수집
#   ./run.sh --update-baseline   기준선 갱신 (의도적 변경 시에만. 커밋 메시지에 이유를 남길 것)
set -u
cd "$(dirname "$0")"
exec python3 run.py "$@"
