#!/usr/bin/env python3
"""
EP별 exe 빌드 스크립트.

해당 EP venv의 Python으로 PyInstaller를 실행하여
올바른 onnxruntime 변종이 _internal/에 번들되도록 한다.

Usage:
    python scripts/build.py --ep cuda       # CUDA GPU 빌드
    python scripts/build.py --ep directml   # DirectML 빌드
    python scripts/build.py --ep cpu        # CPU 전용 빌드
    python scripts/build.py                 # 자동 선택
"""
import argparse
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from core.ep_manager import (
    EP_VARIANTS, get_platform_variants, is_ep_available,
    auto_select_ep, _get_venv_python,
)


def _run(cmd: list[str], **kw):
    print(f"  → {' '.join(cmd)}")
    subprocess.check_call(cmd, **kw)


def ensure_build_deps(python: Path):
    """venv에 PyInstaller + 프로젝트 의존성 설치."""
    py = str(python)

    # PyInstaller
    _run([py, "-m", "pip", "install", "pyinstaller", "-q"])

    # 프로젝트 의존성 (requirements-web.txt에서 onnxruntime 행 제외)
    req = PROJECT_ROOT / "requirements-web.txt"
    if req.is_file():
        lines = req.read_text().splitlines()
        filtered = [l for l in lines if l.strip() and not l.strip().startswith("#")
                    and "onnxruntime" not in l.lower()]
        if filtered:
            _run([py, "-m", "pip", "install", *filtered, "-q"])

    # 선택적 의존성
    for pkg in ["pywebview", "matplotlib", "scikit-learn", "openpyxl"]:
        try:
            _run([py, "-m", "pip", "install", pkg, "-q"])
        except subprocess.CalledProcessError:
            print(f"  ⚠ {pkg} 설치 실패 (선택적, 무시)")


def build(ep_key: str):
    python = _get_venv_python(ep_key)
    if not python.is_file():
        print(f"오류: ep_venvs/{ep_key} venv가 없습니다. 먼저 설치하세요:")
        print(f"  python scripts/setup_ep.py {ep_key}")
        sys.exit(1)

    info = EP_VARIANTS[ep_key]
    print(f"\n{'='*60}")
    print(f"  빌드 EP: {info['label']}")
    print(f"  Python:  {python}")
    print(f"{'='*60}\n")

    ensure_build_deps(python)

    # PyInstaller 실행
    spec = PROJECT_ROOT / "ssook.spec"
    _run([str(python), "-m", "PyInstaller", str(spec), "--noconfirm"],
         cwd=str(PROJECT_ROOT))

    print(f"\n{'='*60}")
    print(f"  ✓ 빌드 완료: dist/ssook/  (EP: {ep_key})")
    print(f"{'='*60}")


def main():
    parser = argparse.ArgumentParser(description="EP별 exe 빌드")
    parser.add_argument("--ep", default=None,
                        help="빌드할 EP (cuda/directml/openvino/coreml/cpu). 생략 시 자동 선택")
    args = parser.parse_args()

    if args.ep:
        ep_key = args.ep
        variants = get_platform_variants()
        if ep_key not in variants:
            print(f"오류: '{ep_key}'는 현재 플랫폼에서 사용 불가. 가능: {', '.join(variants)}")
            sys.exit(1)
    else:
        ep_key = auto_select_ep()
        if ep_key == "auto":
            ep_key = "cpu"
            print(f"설치된 EP venv 없음 → cpu로 빌드")
        else:
            print(f"자동 선택: {ep_key}")

    if not is_ep_available(ep_key):
        print(f"오류: ep_venvs/{ep_key} 미설치. 먼저:")
        print(f"  python scripts/setup_ep.py {ep_key}")
        sys.exit(1)

    build(ep_key)


if __name__ == "__main__":
    main()
