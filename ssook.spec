# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for ssook (Web UI)
# Build: pyinstaller ssook.spec
#
# ep_venvs/에 설치된 최적 EP의 onnxruntime을 자동 번들합니다.
# 사전 준비: python scripts/setup_ep.py

import glob, os, sys, importlib

block_cipher = None

# ── ep_venvs에서 최적 EP의 site-packages를 pathex에 추가 ──
_ep_site = None
_spec_dir = os.path.dirname(os.path.abspath(SPECPATH)) if 'SPECPATH' in dir() else os.getcwd()
_ep_venvs = os.path.join(_spec_dir, 'ep_venvs')

# 플랫폼별 우선순위
_priority = {
    'win32':  ['cuda', 'directml', 'openvino', 'cpu'],
    'linux':  ['cuda', 'openvino', 'cpu'],
    'darwin': ['coreml', 'cpu'],
}.get(sys.platform, ['cpu'])

for _ep in _priority:
    _venv = os.path.join(_ep_venvs, _ep)
    if sys.platform == 'win32':
        _sp = os.path.join(_venv, 'Lib', 'site-packages')
    else:
        # linux/mac: lib/python3.X/site-packages
        _lib = os.path.join(_venv, 'lib')
        _sp = None
        if os.path.isdir(_lib):
            for d in sorted(os.listdir(_lib), reverse=True):
                if d.startswith('python'):
                    _sp = os.path.join(_lib, d, 'site-packages')
                    break
    if _sp and os.path.isdir(os.path.join(_sp, 'onnxruntime')):
        _ep_site = _sp
        print(f'[ssook.spec] EP venv 감지: {_ep} → {_sp}')
        break

if _ep_site is None:
    print('[ssook.spec] ⚠ ep_venvs에서 onnxruntime을 찾지 못함 → 메인 환경 사용')

_extra_pathex = [_ep_site] if _ep_site else []

# ── onnxruntime GPU 바이너리 자동 수집 ──
_ort_binaries = []
_ort_pkg = os.path.join(_ep_site, 'onnxruntime') if _ep_site else None
if _ort_pkg is None:
    try:
        _ort_pkg = os.path.dirname(importlib.import_module('onnxruntime').__file__)
    except Exception:
        _ort_pkg = None

if _ort_pkg and os.path.isdir(_ort_pkg):
    _capi = os.path.join(_ort_pkg, 'capi')
    for pattern in ['*.dll', '*.so', '*.so.*', '*.dylib', '*.pyd']:
        for f in glob.glob(os.path.join(_capi, pattern)):
            _ort_binaries.append((f, 'onnxruntime/capi'))
    for f in glob.glob(os.path.join(_ort_pkg, '*.dll')):
        _ort_binaries.append((f, 'onnxruntime'))

a = Analysis(
    ['run_web.py'],
    pathex=['.'] + _extra_pathex,
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
