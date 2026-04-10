#!/usr/bin/env python3
"""
EP venv 셋업 스크립트 — onnxruntime 변종별 격리 venv 생성.

Usage:
    python scripts/setup_ep.py                  # 현재 플랫폼에 맞는 전체 EP 설치
    python scripts/setup_ep.py cuda directml    # 특정 EP만 설치
    python scripts/setup_ep.py --list           # 설치 가능한 EP 목록
    python scripts/setup_ep.py --status         # 설치 상태 확인
"""
import argparse
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from core.ep_manager import EP_VENVS_DIR, EP_VARIANTS, get_platform_variants, is_ep_available


def _run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess:
    print(f"  → {' '.join(cmd)}")
    return subprocess.run(cmd, check=True, **kwargs)


def create_venv(ep_key: str, info: dict) -> bool:
    """단일 EP용 venv 생성 및 패키지 설치."""
    venv_dir = EP_VENVS_DIR / ep_key
    python = venv_dir / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")

    print(f"\n{'='*60}")
    print(f"  {info['label']}")
    print(f"  {info['desc']}")
    print(f"  → {venv_dir}")
    print(f"{'='*60}")

    # venv 생성
    if not python.is_file():
        print("  [venv] 생성 중...")
        _run([sys.executable, "-m", "venv", str(venv_dir)])
    else:
        print("  [venv] 이미 존재 — 패키지만 업데이트")

    # pip 업그레이드
    _run([str(python), "-m", "pip", "install", "--upgrade", "pip", "-q"])

    # 메인 onnxruntime 패키지 설치
    pkg = info["pkg"]
    print(f"  [pip] {pkg} 설치 중...")
    _run([str(python), "-m", "pip", "install", pkg, "--upgrade", "-q"])

    # 추가 패키지 (예: coreml → coremltools)
    for extra in info.get("extra_pkgs", []):
        print(f"  [pip] {extra} 설치 중...")
        _run([str(python), "-m", "pip", "install", extra, "--upgrade", "-q"])

    # 프로젝트 공통 의존성 (inference에 필요한 최소 패키지)
    req_file = PROJECT_ROOT / "requirements-ep.txt"
    if req_file.is_file():
        print("  [pip] requirements-ep.txt 설치 중...")
        _run([str(python), "-m", "pip", "install", "-r", str(req_file), "-q"])
    else:
        # requirements-ep.txt가 없으면 최소 필수 패키지만
        minimal = ["numpy", "opencv-python", "psutil", "PyYAML"]
        print(f"  [pip] 최소 의존성 설치 중... ({', '.join(minimal)})")
        _run([str(python), "-m", "pip", "install", *minimal, "-q"])

    print(f"  ✓ {ep_key} 설치 완료")
    return True


def show_status():
    """설치 상태 출력."""
    variants = get_platform_variants()
    print(f"\n{'EP':<12} {'상태':<8} {'패키지':<30} {'설명'}")
    print("-" * 80)
    for key, info in variants.items():
        status = "✓ 설치됨" if is_ep_available(key) else "✗ 미설치"
        print(f"{key:<12} {status:<8} {info['pkg']:<30} {info['desc']}")


def main():
    parser = argparse.ArgumentParser(description="EP venv 셋업")
    parser.add_argument("eps", nargs="*", help="설치할 EP 키 (생략 시 플랫폼 전체)")
    parser.add_argument("--list", action="store_true", help="설치 가능한 EP 목록")
    parser.add_argument("--status", action="store_true", help="설치 상태 확인")
    args = parser.parse_args()

    if args.list or args.status:
        show_status()
        return

    variants = get_platform_variants()
    targets = args.eps if args.eps else list(variants.keys())

    # 유효성 검사
    for key in targets:
        if key not in variants:
            available = ", ".join(variants.keys())
            print(f"오류: '{key}'는 현재 플랫폼에서 사용할 수 없습니다. 가능: {available}")
            sys.exit(1)

    EP_VENVS_DIR.mkdir(exist_ok=True)

    success, failed = [], []
    for key in targets:
        try:
            create_venv(key, variants[key])
            success.append(key)
        except subprocess.CalledProcessError as e:
            print(f"  ✗ {key} 설치 실패: {e}")
            failed.append(key)

    print(f"\n{'='*60}")
    print(f"  완료: {len(success)}개 성공", end="")
    if failed:
        print(f", {len(failed)}개 실패 ({', '.join(failed)})")
    else:
        print()
    print(f"{'='*60}")

    show_status()


if __name__ == "__main__":
    main()
