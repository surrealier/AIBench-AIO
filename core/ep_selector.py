"""
EP runtime selector.

Called at startup before onnxruntime is imported.
Detects hardware, selects the best EP, and inserts its path into sys.path.
Records fallback reasons for UI display.
"""
import os
import platform
import subprocess
import sys
from pathlib import Path

# exe: _MEIPASS/ep_runtimes/  |  source: ep_venvs
if getattr(sys, "frozen", False):
    _BASE = Path(sys._MEIPASS) / "ep_runtimes"
    _MODE = "frozen"
else:
    _PROJECT = Path(__file__).resolve().parent.parent
    _ep_runtimes = _PROJECT / "ep_runtimes"
    _ep_venvs = _PROJECT / "ep_venvs"
    _BASE = _ep_runtimes if _ep_runtimes.is_dir() else _ep_venvs
    _MODE = "source"

_PRIORITY = {
    "Windows": ["cuda", "directml", "openvino", "cpu"],
    "Linux":   ["cuda", "openvino", "cpu"],
    "Darwin":  ["coreml", "cpu"],
}

_EP_LABELS = {
    "cuda": "CUDA (NVIDIA GPU)",
    "directml": "DirectML (Windows GPU)",
    "openvino": "OpenVINO (Intel)",
    "coreml": "CoreML (Apple Silicon)",
    "cpu": "CPU",
}

_EP_PROVIDER_MAP = {
    "cuda": "CUDAExecutionProvider",
    "directml": "DmlExecutionProvider",
    "openvino": "OpenVINOExecutionProvider",
    "coreml": "CoreMLExecutionProvider",
    "cpu": "CPUExecutionProvider",
}

# --- selection result (populated after full init) ---
ep_result: dict = {
    "selected": None,
    "provider": None,
    "available_eps": [],
    "bundled_eps": [],
    "skipped": [],
    "fallback": False,
    "fallback_reason": None,
    "fallback_fix": None,
}


def _has_nvidia_gpu() -> bool:
    try:
        r = subprocess.run(
            ["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"],
            capture_output=True, timeout=5, text=True,
            creationflags=0x08000000 if sys.platform == "win32" else 0,
        )
        return r.returncode == 0 and bool(r.stdout.strip())
    except Exception:
        return False


def _has_intel_gpu() -> bool:
    if sys.platform == "win32":
        try:
            r = subprocess.run(
                ["wmic", "path", "win32_videocontroller", "get", "name"],
                capture_output=True, timeout=5, text=True,
                creationflags=0x08000000,
            )
            return "intel" in r.stdout.lower()
        except Exception:
            return False
    return os.path.exists("/dev/dri")


def _resolve_ep_path(key: str) -> "str | None":
    if _MODE == "frozen":
        d = _BASE / key
        return str(d) if (d / "onnxruntime").is_dir() else None
    venv = _BASE / key
    if sys.platform == "win32":
        sp = venv / "Lib" / "site-packages"
    else:
        lib = venv / "lib"
        sp = None
        if lib.is_dir():
            for d in sorted(lib.iterdir(), reverse=True):
                if d.name.startswith("python"):
                    sp = d / "site-packages"
                    break
    if sp and (sp / "onnxruntime").is_dir():
        return str(sp)
    return None


def select_and_activate() -> str:
    """
    Phase 1: If ep_runtimes bundles exist, pick the best and inject into sys.path.
    If no bundles, do nothing -- system/PyInstaller-bundled onnxruntime will be used.
    Actual provider detection happens in get_ep_status() after onnxruntime is loaded.
    """
    plat = platform.system()
    priority = _PRIORITY.get(plat, ["cpu"])

    bundled = [k for k in priority if _resolve_ep_path(k)]
    ep_result["bundled_eps"] = bundled

    if not bundled:
        # No ep_runtimes -- will use system onnxruntime, detect later
        ep_result["selected"] = "system"
        print("[EP Selector] no ep_runtimes found, using system onnxruntime")
        return "system"

    selected = None
    for key in priority:
        if not _resolve_ep_path(key):
            continue
        if key == "cuda" and not _has_nvidia_gpu():
            ep_result["skipped"].append({
                "ep": key,
                "reason": "NVIDIA GPU not detected (nvidia-smi failed)",
                "fix": "Install NVIDIA driver, or check GPU connection",
            })
            continue
        if key == "openvino" and not _has_intel_gpu():
            ep_result["skipped"].append({
                "ep": key,
                "reason": "Intel GPU not detected",
                "fix": "This EP requires Intel iGPU/dGPU",
            })
            continue
        selected = key
        break

    if selected is None and _resolve_ep_path("cpu"):
        selected = "cpu"

    if selected:
        ep_path = _resolve_ep_path(selected)
        if ep_path not in sys.path:
            sys.path.insert(0, ep_path)
        if sys.platform == "win32":
            for libs_name in ["onnxruntime.libs", "onnxruntime_gpu.libs"]:
                libs = Path(ep_path) / libs_name
                if not libs.is_dir():
                    libs = _BASE / selected / libs_name
                if libs.is_dir():
                    os.add_dll_directory(str(libs))
        ep_result["selected"] = selected
        print(f"[EP Selector] selected: {selected} -> {ep_path}")
    else:
        ep_result["selected"] = "system"
        print("[EP Selector] no suitable EP bundle, using system onnxruntime")

    return ep_result["selected"]


def get_ep_status() -> dict:
    """
    Full EP status for API/UI.
    Called after onnxruntime is loaded -- detects actual providers and
    determines the real active provider + fallback info.
    """
    try:
        import onnxruntime as ort
        providers = ort.get_available_providers()
    except Exception:
        providers = []

    ep_result["available_eps"] = providers

    # Determine actual active provider from what onnxruntime reports
    plat = platform.system()
    priority_providers = {
        "Windows": ["CUDAExecutionProvider", "DmlExecutionProvider",
                     "OpenVINOExecutionProvider", "CPUExecutionProvider"],
        "Linux":   ["CUDAExecutionProvider", "OpenVINOExecutionProvider",
                     "CPUExecutionProvider"],
        "Darwin":  ["CoreMLExecutionProvider", "CPUExecutionProvider"],
    }.get(plat, ["CPUExecutionProvider"])

    active_provider = "CPUExecutionProvider"
    for p in priority_providers:
        if p in providers:
            active_provider = p
            break

    ep_result["provider"] = active_provider

    # Reverse map provider to EP key
    _prov_to_key = {v: k for k, v in _EP_PROVIDER_MAP.items()}
    active_key = _prov_to_key.get(active_provider, "cpu")
    if ep_result["selected"] == "system":
        ep_result["selected"] = active_key

    # Determine fallback: did we end up on a lower-priority provider?
    top_provider = priority_providers[0] if priority_providers else None
    if active_provider != top_provider:
        ep_result["fallback"] = True
        # Build skip reasons for providers that were available but not active
        if not ep_result["skipped"]:
            for p in priority_providers:
                if p == active_provider:
                    break
                key = _prov_to_key.get(p, p)
                label = _EP_LABELS.get(key, key)
                if p not in providers:
                    reason = f"{label} not available in this onnxruntime build"
                    if key == "cuda":
                        fix = "Build with onnxruntime-gpu, or run: python scripts/setup_ep.py cuda"
                    elif key == "directml":
                        fix = "Build with onnxruntime-directml, or run: python scripts/setup_ep.py directml"
                    else:
                        fix = f"Run: python scripts/setup_ep.py {key}"
                    ep_result["skipped"].append({"ep": key, "reason": reason, "fix": fix})
                elif key == "cuda" and not _has_nvidia_gpu():
                    ep_result["skipped"].append({
                        "ep": key,
                        "reason": "NVIDIA GPU not detected (nvidia-smi failed)",
                        "fix": "Install NVIDIA driver, or check GPU connection",
                    })
        if ep_result["skipped"]:
            first = ep_result["skipped"][0]
            ep_result["fallback_reason"] = first["reason"]
            ep_result["fallback_fix"] = first["fix"]
    else:
        ep_result["fallback"] = False

    return ep_result
