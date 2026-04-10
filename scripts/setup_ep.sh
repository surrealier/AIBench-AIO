#!/bin/bash
echo "============================================================"
echo " EP venv Setup — onnxruntime 변종별 격리 venv 생성"
echo "============================================================"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 "$SCRIPT_DIR/setup_ep.py" "$@"
