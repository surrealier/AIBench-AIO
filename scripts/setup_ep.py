#!/usr/bin/env python3
"""
EP venv setup script.

Usage:
    python scripts/setup_ep.py                  # install all EPs for current platform
    python scripts/setup_ep.py cuda directml    # install specific EPs
    python scripts/setup_ep.py --list           # list available EPs
    python scripts/setup_ep.py --status         # check install status
"""
import argparse
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from core.ep_manager import EP_VENVS_DIR, EP_VARIANTS, get_platform_variants, is_ep_available


def _run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess:
    print(f"  > {' '.join(cmd)}")
    return subprocess.run(cmd, check=True, **kwargs)


def create_venv(ep_key: str, info: dict) -> bool:
    venv_dir = EP_VENVS_DIR / ep_key
    python = venv_dir / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")

    print(f"\n{'='*60}")
    print(f"  {info['label']}")
    print(f"  {info['desc']}")
    print(f"  -> {venv_dir}")
    print(f"{'='*60}")

    if not python.is_file():
        print("  [venv] creating...")
        _run([sys.executable, "-m", "venv", str(venv_dir)])
    else:
        print("  [venv] exists -- updating packages")

    _run([str(python), "-m", "pip", "install", "--upgrade", "pip", "-q"])

    pkg = info["pkg"]
    print(f"  [pip] installing {pkg}...")
    _run([str(python), "-m", "pip", "install", pkg, "--upgrade", "-q"])

    for extra in info.get("extra_pkgs", []):
        print(f"  [pip] installing {extra}...")
        _run([str(python), "-m", "pip", "install", extra, "--upgrade", "-q"])

    req_file = PROJECT_ROOT / "requirements-ep.txt"
    if req_file.is_file():
        print("  [pip] installing requirements-ep.txt...")
        _run([str(python), "-m", "pip", "install", "-r", str(req_file), "-q"])
    else:
        minimal = ["numpy", "opencv-python", "psutil", "PyYAML"]
        print(f"  [pip] installing minimal deps ({', '.join(minimal)})...")
        _run([str(python), "-m", "pip", "install", *minimal, "-q"])

    print(f"  [OK] {ep_key} installed")
    return True


def show_status():
    variants = get_platform_variants()
    print(f"\n{'EP':<12} {'Status':<12} {'Package':<30} Description")
    print("-" * 80)
    for key, info in variants.items():
        status = "installed" if is_ep_available(key) else "not found"
        print(f"{key:<12} {status:<12} {info['pkg']:<30} {info['desc']}")


def main():
    parser = argparse.ArgumentParser(description="EP venv setup")
    parser.add_argument("eps", nargs="*", help="EP keys to install (all if omitted)")
    parser.add_argument("--list", action="store_true", help="List available EPs")
    parser.add_argument("--status", action="store_true", help="Check install status")
    args = parser.parse_args()

    if args.list or args.status:
        show_status()
        return

    variants = get_platform_variants()
    targets = args.eps if args.eps else list(variants.keys())

    for key in targets:
        if key not in variants:
            available = ", ".join(variants.keys())
            print(f"ERROR: '{key}' not available on this platform. Options: {available}")
            sys.exit(1)

    EP_VENVS_DIR.mkdir(exist_ok=True)

    success, failed = [], []
    for key in targets:
        try:
            create_venv(key, variants[key])
            success.append(key)
        except subprocess.CalledProcessError as e:
            print(f"  [FAIL] {key}: {e}")
            failed.append(key)

    print(f"\n{'='*60}")
    print(f"  Done: {len(success)} succeeded", end="")
    if failed:
        print(f", {len(failed)} failed ({', '.join(failed)})")
    else:
        print()
    print(f"{'='*60}")

    show_status()


if __name__ == "__main__":
    main()
