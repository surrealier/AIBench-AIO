# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for ssook (Web UI)
# Build: python scripts/build.py --ep cuda

import glob, os, importlib

block_cipher = None

# ── onnxruntime GPU 바이너리 자동 수집 ──
_ort_binaries = []
try:
    _ort_pkg = os.path.dirname(importlib.import_module('onnxruntime').__file__)
    _capi = os.path.join(_ort_pkg, 'capi')
    for pattern in ['*.dll', '*.so', '*.dylib', '*.pyd']:
        for f in glob.glob(os.path.join(_capi, pattern)):
            _ort_binaries.append((f, 'onnxruntime/capi'))
    # CUDA/TensorRT/cuDNN DLL (onnxruntime-gpu 패키지에 포함)
    for f in glob.glob(os.path.join(_ort_pkg, '*.dll')):
        _ort_binaries.append((f, 'onnxruntime'))
except Exception:
    pass

a = Analysis(
    ['run_web.py'],
    pathex=['.'],
    binaries=_ort_binaries,
    datas=[
        ('web',         'web'),
        ('settings',    'settings'),
        ('assets',      'assets'),
        ('server.py',   '.'),
        ('core',        'core'),
    ],
    hiddenimports=[
        'uvicorn', 'uvicorn.logging', 'uvicorn.loops', 'uvicorn.loops.auto',
        'uvicorn.protocols', 'uvicorn.protocols.http', 'uvicorn.protocols.http.auto',
        'uvicorn.protocols.websockets', 'uvicorn.protocols.websockets.auto',
        'uvicorn.lifespan', 'uvicorn.lifespan.on',
        'fastapi', 'starlette', 'pydantic', 'anyio',
        'onnxruntime', 'onnxruntime.capi', 'onnxruntime.capi.onnxruntime_pybind11_state',
        'cv2', 'numpy', 'yaml', 'psutil',
        'core.app_config', 'core.model_loader', 'core.inference',
        'core.benchmark_runner', 'core.evaluation',
        'server',
        'webview', 'webview.platforms', 'webview.platforms.edgechromium',
        'clr_loader', 'pythonnet',
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=[
        'PySide6', 'PyQt5', 'PyQt6',
        'torch', 'torchvision', 'torchaudio',
        'IPython', 'jupyter', 'notebook', 'ultralytics',
    ],
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='ssook',
    debug=False,
    strip=False,
    upx=True,
    console=False,
    icon='assets/icon.ico',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=['onnxruntime_providers_*.dll', 'onnxruntime_providers_shared.dll',
                 'cv2*.dll', 'opencv*.dll', 'libopenblas*.dll'],
    name='ssook',
)
