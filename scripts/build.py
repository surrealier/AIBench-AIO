#!/usr/bin/env python3
"""
EP exe build script.

Usage:
    python scripts/build.py --ep cuda       # CUDA GPU build
    python scripts/build.py --ep directml   # DirectML build
    python scripts/build.py --ep cpu        # CPU-only build
    python scripts/build.py                 # auto-select
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
    print(f"  > {' '.join(cmd)}")
    subprocess.check_call(cmd, **kw)


def ensure_build_deps(python: Path):
    py = str(python)
    _run([py, "-m", "pip", "install", "pyinstaller", "-q"])

    req = PROJECT_ROOT / "requirements-web.txt"
    if req.is_file():
        lines = req.read_text().splitlines()
        filtered = [l for l in lines if l.strip() and not l.strip().startswith("#")
                    and "onnxruntime" not in l.lower()]
        if filtered:
            _run([py, "-m", "pip", "install", *filtered, "-q"])

    for pkg in ["pywebview", "matplotlib", "scikit-learn", "openpyxl"]:
        try:
            _run([py, "-m", "pip", "install", pkg, "-q"])
        except subprocess.CalledProcessError:
            print(f"  [WARN] {pkg} install failed (optional, skipped)")


def build(ep_key: str):
    python = _get_venv_python(ep_key)
    if not python.is_file():
        print(f"ERROR: ep_venvs/{ep_key} not found. Run first:")
        print(f"  python scripts/setup_ep.py {ep_key}")
        sys.exit(1)

    info = EP_VARIANTS[ep_key]
    print(f"\n{'='*60}")
    print(f"  Build EP: {info['label']}")
    print(f"  Python:   {python}")
    print(f"{'='*60}\n")

    ensure_build_deps(python)

    spec = PROJECT_ROOT / "ssook.spec"
    _run([str(python), "-m", "PyInstaller", str(spec), "--noconfirm"],
         cwd=str(PROJECT_ROOT))

    print(f"\n{'='*60}")
    print(f"  Done: dist/ssook/  (EP: {ep_key})")
    print(f"{'='*60}")


def main():
    parser = argparse.ArgumentParser(description="EP exe build")
    parser.add_argument("--ep", default=None,
                        help="EP to build (cuda/directml/openvino/coreml/cpu). Auto if omitted")
    args = parser.parse_args()

    if args.ep:
        ep_key = args.ep
        variants = get_platform_variants()
        if ep_key not in variants:
            print(f"ERROR: '{ep_key}' not available. Options: {', '.join(variants)}")
            sys.exit(1)
    else:
        ep_key = auto_select_ep()
        if ep_key == "auto":
            ep_key = "cpu"
            print("No EP venv found -> building with cpu")
        else:
            print(f"Auto-selected: {ep_key}")

    if not is_ep_available(ep_key):
        print(f"ERROR: ep_venvs/{ep_key} not installed. Run first:")
        print(f"  python scripts/setup_ep.py {ep_key}")
        sys.exit(1)

    build(ep_key)


if __name__ == "__main__":
    main()
