"""
Visualizer Web Server — FastAPI backend serving the web UI
and exposing core/ functionality as REST API.
"""
import os
import sys
import platform
import asyncio
import base64
import threading
import time
import uuid
from pathlib import Path

import cv2
import numpy as np
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
from typing import Optional

# Ensure project root is on path
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))


def _generate_palette(n):
    """HSV 균등 분포로 n개의 BGR 색상 생성"""
    colors = []
    for i in range(n):
        hue = int(180 * i / max(n, 1))
        hsv = np.uint8([[[hue, 220, 220]]])
        bgr = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)[0][0]
        colors.append(tuple(int(x) for x in bgr))
    return colors


_palette_cache = []


def _get_color(style, cid, total):
    """Return BGR color for a class: style.color > palette > green fallback."""
    global _palette_cache
    if style.color:
        return tuple(style.color)
    if total > 0:
        if len(_palette_cache) < total:
            _palette_cache = _generate_palette(total)
        return _palette_cache[cid % len(_palette_cache)]
    return (0, 255, 0)

app = FastAPI(title="Visualizer", version="1.0.0")

# ── Static files ────────────────────────────────────────
WEB_DIR = ROOT / "web"
app.mount("/css", StaticFiles(directory=WEB_DIR / "css"), name="css")
app.mount("/js", StaticFiles(directory=WEB_DIR / "js"), name="js")
app.mount("/assets", StaticFiles(directory=ROOT / "assets"), name="assets")


@app.get("/")
async def index():
    return FileResponse(WEB_DIR / "index.html")


# ── Config API ──────────────────────────────────────────
@app.get("/api/config")
async def get_config():
    try:
        from core.app_config import AppConfig
        cfg = AppConfig()
        return {
            "model_type": cfg.model_type,
            "conf_threshold": cfg.conf_threshold,
            "batch_size": cfg.batch_size,
            "box_thickness": cfg.box_thickness,
            "label_size": cfg.label_size,
            "show_labels": cfg.show_labels,
            "show_confidence": cfg.show_confidence,
        }
    except Exception as e:
        return {"error": str(e)}


class ConfigUpdate(BaseModel):
    conf_threshold: Optional[float] = None
    model_type: Optional[str] = None
    batch_size: Optional[int] = None
    box_thickness: Optional[int] = None
    label_size: Optional[float] = None
    show_labels: Optional[bool] = None
    show_confidence: Optional[bool] = None


@app.post("/api/config")
async def save_config(cfg: ConfigUpdate):
    try:
        from core.app_config import AppConfig
        app_cfg = AppConfig()
        for k, v in cfg.dict(exclude_none=True).items():
            setattr(app_cfg, k, v)
        app_cfg.save()
        return {"ok": True}
    except Exception as e:
        return {"error": str(e)}


# ── Model API ───────────────────────────────────────────
class ModelLoadRequest(BaseModel):
    path: str


@app.post("/api/model/load")
async def load_model(req: ModelLoadRequest):
    global _loaded_model, _loaded_model_meta
    try:
        from core.model_loader import load_model as _load
        from core.app_config import AppConfig
        cfg = AppConfig()
        info = _load(req.path, model_type=cfg.model_type)
        _loaded_model = info
        inp = info.session.get_inputs()[0]
        out = info.session.get_outputs()[0]
        meta = {
            "ok": True,
            "name": os.path.basename(req.path),
            "input_shape": str(inp.shape),
            "output_shape": str(out.shape),
            "input_size": list(info.input_size) if info.input_size else None,
            "num_classes": len(info.names) if info.names else 0,
            "names": info.names or {},
            "task": info.task_type or "",
            "layout": info.output_layout or "",
            "model_type": info.model_type or "",
            "batch_size": info.batch_size,
        }
        _loaded_model_meta = meta
        return meta
    except Exception as e:
        return {"error": str(e)}


@app.get("/api/model/info")
async def model_info():
    return {"loaded": _loaded_model is not None, "info": _loaded_model_meta}


# ── Shared model state ──────────────────────────────────
_loaded_model = None      # ModelInfo object
_loaded_model_meta = None  # dict for JSON response


# ── Inference API ───────────────────────────────────────
class InferRequest(BaseModel):
    model_path: str
    image_path: Optional[str] = None
    conf: float = 0.25


@app.post("/api/infer/image")
async def infer_image(req: InferRequest):
    """Run inference on a single image, return annotated JPEG + detections."""
    global _loaded_model, _loaded_model_meta
    try:
        from core.model_loader import load_model as _load
        from core.inference import run_inference, run_classification
        from core.app_config import AppConfig

        cfg = AppConfig()
        if _loaded_model is None or _loaded_model.path != req.model_path or _loaded_model.model_type != cfg.model_type:
            _loaded_model = _load(req.model_path, model_type=cfg.model_type)
            _loaded_model_meta = {"name": os.path.basename(req.model_path)}

        frame = cv2.imread(req.image_path)
        if frame is None:
            return {"error": "Cannot read image"}

        names = _loaded_model.names or {}

        if _loaded_model.task_type == "classification":
            result = run_classification(_loaded_model, frame)
            top_k = result.top_k[:5]
            y = 30
            vis = frame.copy()
            for cid, conf in top_k:
                label = f"{names.get(cid, str(cid))}: {conf:.3f}"
                cv2.putText(vis, label, (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                y += 30
            _, buf = cv2.imencode('.jpg', vis, [cv2.IMWRITE_JPEG_QUALITY, 85])
            best = names.get(result.class_id, str(result.class_id))
            return {
                "image": base64.b64encode(buf).decode(),
                "detections": 0,
                "classification": f"{best} ({result.confidence:.3f})",
                "top_k": [{"class": names.get(c, str(c)), "score": round(s, 4)} for c, s in top_k],
                "infer_ms": round(result.infer_ms, 2),
                "classes": {},
            }

        # Detection
        result = run_inference(_loaded_model, frame, cfg.conf_threshold)
        thickness = cfg.box_thickness
        label_size = cfg.label_size
        total_cls = len(names)
        for box, score, cid in zip(result.boxes, result.scores, result.class_ids):
            cid_int = int(cid)
            style = cfg.get_class_style(cid_int)
            if not style.enabled:
                continue
            x1, y1, x2, y2 = map(int, box)
            t_val = style.thickness or thickness
            color = _get_color(style, cid_int, total_cls)
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, t_val)
            parts = []
            if cfg.show_labels:
                parts.append(names.get(cid_int, str(cid_int)))
            if cfg.show_confidence:
                parts.append(f"{score:.2f}")
            if parts:
                cv2.putText(frame, " ".join(parts), (x1, max(y1 - 6, 14)),
                            cv2.FONT_HERSHEY_SIMPLEX, label_size, color, max(1, t_val - 1))

        _, buf = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
        return {
            "image": base64.b64encode(buf).decode(),
            "detections": len(result.boxes),
            "infer_ms": round(result.infer_ms, 2),
            "classes": {int(cid): names.get(int(cid), str(int(cid)))
                        for cid in np.unique(result.class_ids)} if len(result.class_ids) else {},
        }
    except Exception as e:
        return {"error": str(e)}


# ── Video streaming (MJPEG) ─────────────────────────────
_video_sessions = {}  # session_id -> dict with state


class VideoStartRequest(BaseModel):
    model_path: str
    video_path: str
    conf: float = 0.25


@app.post("/api/viewer/start")
async def viewer_start(req: VideoStartRequest):
    """Start a video inference session, returns session_id."""
    global _loaded_model, _loaded_model_meta
    try:
        from core.model_loader import load_model as _load
        from core.app_config import AppConfig
        cfg = AppConfig()
        if _loaded_model is None or _loaded_model.path != req.model_path or _loaded_model.model_type != cfg.model_type:
            _loaded_model = _load(req.model_path, model_type=cfg.model_type)
            _loaded_model_meta = {"name": os.path.basename(req.model_path)}

        cap = cv2.VideoCapture(req.video_path)
        if not cap.isOpened():
            return {"error": "Cannot open video"}

        fps = cap.get(cv2.CAP_PROP_FPS) or 30
        sid = str(uuid.uuid4())[:8]
        _video_sessions[sid] = {
            "cap": cap, "model": _loaded_model, "conf": req.conf,
            "playing": True, "paused": False,
            "fps": fps, "speed": 1.0,
            "total": int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
            "width": int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            "height": int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            "frame_idx": 0, "last_detections": 0, "last_infer_ms": 0,
            "last_frame": None, "last_result": None,
            "seek_to": None, "step_request": None,
            "video_path": req.video_path,
        }
        return {"session_id": sid, "fps": fps,
                "total_frames": _video_sessions[sid]["total"]}
    except Exception as e:
        return {"error": str(e)}


@app.get("/api/viewer/stream/{session_id}")
async def viewer_stream(session_id: str):
    """MJPEG stream of inference results."""
    sess = _video_sessions.get(session_id)
    if not sess:
        return {"error": "Invalid session"}

    def generate():
        from core.inference import run_inference, run_classification
        from core.app_config import AppConfig
        cap = sess["cap"]
        model = sess["model"]
        names = model.names or {}

        try:
            while sess.get("playing", False):
                # Handle seek
                seek_to = sess.get("seek_to")
                if seek_to is not None:
                    cap.set(cv2.CAP_PROP_POS_FRAMES, seek_to)
                    sess["seek_to"] = None

                # Handle step
                step = sess.get("step_request")
                if step is not None:
                    cur = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
                    cap.set(cv2.CAP_PROP_POS_FRAMES, max(0, cur + step))
                    sess["step_request"] = None

                # Handle pause
                if sess.get("paused", False):
                    time.sleep(0.05)
                    continue

                target_delay = 1.0 / (sess["fps"] * sess.get("speed", 1.0))
                t0 = time.time()
                ret, frame = cap.read()
                if not ret:
                    sess["playing"] = False
                    break

                sess["frame_idx"] = int(cap.get(cv2.CAP_PROP_POS_FRAMES))

                cfg = AppConfig()

                if model.task_type == "classification":
                    result = run_classification(model, frame)
                    sess["last_detections"] = 0
                    sess["last_infer_ms"] = round(result.infer_ms, 2)
                    sess["last_frame"] = frame.copy()
                    sess["last_result"] = None
                    vis = frame.copy()
                    y = 30
                    for cid, conf in result.top_k[:5]:
                        label = f"{names.get(cid, str(cid))}: {conf:.3f}"
                        cv2.putText(vis, label, (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                        y += 30
                    _, buf = cv2.imencode('.jpg', vis, [cv2.IMWRITE_JPEG_QUALITY, 80])
                else:
                    result = run_inference(model, frame, cfg.conf_threshold)
                    sess["last_detections"] = len(result.boxes)
                    sess["last_infer_ms"] = round(result.infer_ms, 2)
                    sess["last_frame"] = frame.copy()
                    sess["last_result"] = result

                    thickness = cfg.box_thickness
                    label_size = cfg.label_size
                    total_cls = len(names)
                    for box, score, cid in zip(result.boxes, result.scores, result.class_ids):
                        cid_int = int(cid)
                        style = cfg.get_class_style(cid_int)
                        if not style.enabled:
                            continue
                        x1, y1, x2, y2 = map(int, box)
                        t_val = style.thickness or thickness
                        color = _get_color(style, cid_int, total_cls)
                        cv2.rectangle(frame, (x1, y1), (x2, y2), color, t_val)
                        parts = []
                        if cfg.show_labels:
                            parts.append(names.get(cid_int, str(cid_int)))
                        if cfg.show_confidence:
                            parts.append(f"{score:.2f}")
                        if parts:
                            cv2.putText(frame, " ".join(parts), (x1, max(y1 - 6, 14)),
                                        cv2.FONT_HERSHEY_SIMPLEX, label_size, color, max(1, t_val - 1))
                    _, buf = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
                yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' +
                       buf.tobytes() + b'\r\n')

                elapsed = time.time() - t0
                if elapsed < target_delay:
                    time.sleep(target_delay - elapsed)
        except Exception as exc:
            import traceback
            print(f"[MJPEG ERROR] {exc}")
            traceback.print_exc()
            sess["playing"] = False

    return StreamingResponse(generate(),
                             media_type='multipart/x-mixed-replace; boundary=frame')


@app.get("/api/viewer/status/{session_id}")
async def viewer_status(session_id: str):
    sess = _video_sessions.get(session_id)
    if not sess:
        return {"error": "Invalid session"}
    return {
        "playing": sess["playing"],
        "paused": sess.get("paused", False),
        "frame_idx": sess["frame_idx"],
        "total": sess["total"],
        "detections": sess["last_detections"],
        "infer_ms": sess["last_infer_ms"],
        "speed": sess.get("speed", 1.0),
    }


@app.post("/api/viewer/stop/{session_id}")
async def viewer_stop(session_id: str):
    sess = _video_sessions.pop(session_id, None)
    if sess:
        sess["playing"] = False
        sess["cap"].release()
    return {"ok": True}


@app.post("/api/viewer/pause/{session_id}")
async def viewer_pause(session_id: str):
    sess = _video_sessions.get(session_id)
    if sess:
        sess["paused"] = not sess.get("paused", False)
    return {"paused": sess.get("paused", False) if sess else False}


class SeekRequest(BaseModel):
    frame: int


@app.post("/api/viewer/seek/{session_id}")
async def viewer_seek(session_id: str, req: SeekRequest):
    sess = _video_sessions.get(session_id)
    if sess:
        sess["seek_to"] = req.frame
    return {"ok": True}


class SpeedRequest(BaseModel):
    speed: float


@app.post("/api/viewer/speed/{session_id}")
async def viewer_speed(session_id: str, req: SpeedRequest):
    sess = _video_sessions.get(session_id)
    if sess:
        sess["speed"] = req.speed
    return {"ok": True}


class StepRequest(BaseModel):
    delta: int = 1


@app.post("/api/viewer/step/{session_id}")
async def viewer_step(session_id: str, req: StepRequest):
    sess = _video_sessions.get(session_id)
    if sess:
        sess["step_request"] = req.delta
    return {"ok": True}


@app.post("/api/viewer/snapshot/{session_id}")
async def viewer_snapshot(session_id: str):
    sess = _video_sessions.get(session_id)
    if not sess or sess.get("last_frame") is None:
        return {"error": "No frame available"}
    os.makedirs("snapshots", exist_ok=True)
    from datetime import datetime
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join("snapshots", f"snapshot_{ts}.jpg")
    frame = sess["last_frame"].copy()
    # Draw detections on snapshot
    result = sess.get("last_result")
    if result is not None:
        from core.app_config import AppConfig
        cfg = AppConfig()
        names = sess["model"].names or {}
        total_cls = len(names)
        for box, score, cid in zip(result.boxes, result.scores, result.class_ids):
            cid_int = int(cid)
            style = cfg.get_class_style(cid_int)
            if not style.enabled:
                continue
            x1, y1, x2, y2 = map(int, box)
            t_val = style.thickness or cfg.box_thickness
            color = _get_color(style, cid_int, total_cls)
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, t_val)
            parts = []
            if cfg.show_labels:
                parts.append(names.get(cid_int, str(cid_int)))
            if cfg.show_confidence:
                parts.append(f"{score:.2f}")
            if parts:
                cv2.putText(frame, " ".join(parts), (x1, max(y1 - 6, 14)),
                            cv2.FONT_HERSHEY_SIMPLEX, cfg.label_size, color, max(1, t_val - 1))
    cv2.imwrite(path, frame)
    return {"ok": True, "path": path}


# ── Video Info ──────────────────────────────────────────
class VideoInfoRequest(BaseModel):
    path: str


@app.post("/api/video/info")
async def video_info(req: VideoInfoRequest):
    try:
        cap = cv2.VideoCapture(req.path)
        if not cap.isOpened():
            return {"error": "Cannot open video"}
        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS) or 0
        total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        cap.release()
        dur_s = total / fps if fps > 0 else 0
        mins, secs = divmod(int(dur_s), 60)
        return {
            "width": w, "height": h, "fps": round(fps, 2),
            "total_frames": total, "duration": f"{mins}:{secs:02d}",
        }
    except Exception as e:
        return {"error": str(e)}


# ── Hardware Stats ──────────────────────────────────────
@app.get("/api/system/hw")
async def system_hw():
    import psutil
    proc = psutil.Process(os.getpid())
    info = {
        "cpu": round(proc.cpu_percent(interval=0), 1),
        "ram_mb": round(proc.memory_info().rss / 1024 / 1024),
    }
    try:
        import subprocess, sys as _sys
        flags = 0x08000000 if _sys.platform == "win32" else 0
        out = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=name,utilization.gpu,memory.used,memory.total,temperature.gpu",
             "--format=csv,noheader,nounits"],
            text=True, timeout=2, creationflags=flags,
        )
        parts = [p.strip() for p in out.strip().split(",")]
        info.update(gpu_name=parts[0], gpu_util=int(parts[1]),
                    gpu_mem_used=int(parts[2]), gpu_mem_total=int(parts[3]),
                    gpu_temp=int(parts[4]))
    except Exception:
        info.update(gpu_name="N/A", gpu_util=0, gpu_mem_used=0, gpu_mem_total=0, gpu_temp=0)
    return info


# ── Benchmark API (async) ──────────────────────────────
class BenchmarkRequest(BaseModel):
    models: list[str]
    iterations: int = 100
    input_size: int = 640


_bench_state = {"running": False, "progress": 0, "total": 0, "msg": "", "results": []}


@app.post("/api/benchmark/run")
async def run_benchmark(req: BenchmarkRequest):
    if _bench_state["running"]:
        return {"error": "Benchmark already running"}

    def _run():
        from core.benchmark_runner import BenchmarkConfig, run_benchmark_core
        _bench_state.update(running=True, progress=0, total=0, msg="Starting...", results=[])
        configs = []
        for path in req.models:
            configs.append(BenchmarkConfig(
                model_path=path, iterations=req.iterations,
                warmup=min(50, req.iterations), src_hw=(1080, 1920),
            ))
        _bench_state["total"] = sum(c.warmup + c.iterations for c in configs)

        def on_progress(done, total, msg):
            _bench_state["progress"] = done
            _bench_state["msg"] = msg

        def on_result(r):
            _bench_state["results"].append({
                "name": r.model_name, "provider": r.provider,
                "fps": round(r.fps, 1),
                "avg": round(r.mean_total_ms, 2),
                "p50": round(r.mean_infer_ms, 2),
                "p95": round(r.max_ms, 2),
                "p99": round(r.max_ms, 2),
            })

        def on_error(msg):
            _bench_state["results"].append({"error": msg})

        try:
            run_benchmark_core(configs, on_progress, on_result, on_error, lambda: False)
        except Exception as e:
            _bench_state["msg"] = f"Error: {e}"
        _bench_state["running"] = False
        _bench_state["msg"] = "Complete"

    threading.Thread(target=_run, daemon=True).start()
    return {"ok": True, "msg": "Benchmark started"}


@app.get("/api/benchmark/status")
async def benchmark_status():
    return {
        "running": _bench_state["running"],
        "progress": _bench_state["progress"],
        "total": _bench_state["total"],
        "msg": _bench_state["msg"],
        "results": _bench_state["results"],
    }


# ── System Info ─────────────────────────────────────────
@app.get("/api/system/info")
async def system_info():
    info = {
        "os": f"{platform.system()} {platform.release()}",
        "python": platform.python_version(),
    }
    try:
        import onnxruntime
        info["ort"] = onnxruntime.__version__
    except ImportError:
        info["ort"] = "N/A"
    try:
        import torch
        info["torch"] = torch.__version__
        info["cuda"] = torch.version.cuda or "N/A"
    except ImportError:
        info["torch"] = "N/A"
        info["cuda"] = "N/A"
    try:
        import subprocess, sys as _sys
        flags = 0x08000000 if _sys.platform == "win32" else 0
        out = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=name", "--format=csv,noheader,nounits"],
            text=True, timeout=2, creationflags=flags,
        )
        info["gpu_name"] = out.strip()
    except Exception:
        info["gpu_name"] = "N/A"
    return info


# ── File System API (for file/dir selection dialogs) ────
class FileSelectRequest(BaseModel):
    filters: Optional[str] = None


@app.post("/api/fs/select")
async def select_file(req: FileSelectRequest):
    """Return a file selection dialog via tkinter (fallback)."""
    try:
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        path = filedialog.askopenfilename(
            title="Select File",
            filetypes=[("All files", "*.*")] if not req.filters else _parse_filters(req.filters),
        )
        root.destroy()
        return {"path": path or ""}
    except Exception as e:
        return {"error": str(e), "path": ""}


@app.post("/api/fs/select-dir")
async def select_dir():
    try:
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        path = filedialog.askdirectory(title="Select Directory")
        root.destroy()
        return {"path": path or ""}
    except Exception as e:
        return {"error": str(e), "path": ""}


class ListDirRequest(BaseModel):
    path: str
    exts: Optional[list[str]] = None


@app.post("/api/fs/list")
async def list_dir(req: ListDirRequest):
    p = ROOT / req.path if not os.path.isabs(req.path) else Path(req.path)
    if not p.is_dir():
        return {"error": "Not a directory", "files": [], "entries": []}
    files = []
    for item in sorted(p.iterdir()):
        if item.is_file():
            if req.exts and item.suffix.lower() not in req.exts:
                continue
            files.append({"name": item.name, "path": str(item.resolve())})
    return {"files": files}


# ── Evaluation API ──────────────────────────────────────
class EvalRequest(BaseModel):
    models: list[str]
    img_dir: str
    label_dir: str
    conf: float = 0.25


@app.post("/api/evaluation/run")
async def run_evaluation(req: EvalRequest):
    """Run multi-model evaluation against GT labels."""
    try:
        from core.model_loader import load_model as _load_model
        from core.inference import run_inference
        from core.evaluation import evaluate_dataset, evaluate_map50_95
        import glob, cv2

        exts = ("*.jpg", "*.jpeg", "*.png", "*.bmp")
        img_files = []
        for e in exts:
            img_files.extend(glob.glob(os.path.join(req.img_dir, e)))
        img_files.sort()

        # Load GT
        gt_data = {}
        for fp in img_files:
            stem = os.path.splitext(os.path.basename(fp))[0]
            txt = os.path.join(req.label_dir, stem + ".txt")
            boxes = []
            if os.path.isfile(txt):
                with open(txt) as f:
                    for line in f:
                        parts = line.strip().split()
                        if len(parts) >= 5:
                            boxes.append((int(parts[0]), *map(float, parts[1:5])))
            gt_data[stem] = boxes

        results = []
        for model_path in req.models:
            name = os.path.basename(model_path)
            try:
                mi = _load_model(model_path)
                pred_data = {}
                for fp in img_files:
                    frame = cv2.imread(fp)
                    if frame is None:
                        continue
                    h, w = frame.shape[:2]
                    res = run_inference(mi, frame, req.conf)
                    stem = os.path.splitext(os.path.basename(fp))[0]
                    boxes = []
                    for box, score, cid in zip(res.boxes, res.scores, res.class_ids):
                        x1, y1, x2, y2 = box
                        cx = ((x1+x2)/2)/w; cy = ((y1+y2)/2)/h
                        bw = (x2-x1)/w; bh = (y2-y1)/h
                        boxes.append((int(cid), cx, cy, bw, bh, float(score)))
                    pred_data[stem] = boxes

                res50 = evaluate_dataset(gt_data, pred_data, 0.5)
                map5095 = evaluate_map50_95(gt_data, pred_data)
                ov = res50.get("__overall__", {})
                results.append({
                    "name": name,
                    "map50": ov.get("ap", 0),
                    "map5095": map5095,
                    "precision": ov.get("precision", 0),
                    "recall": ov.get("recall", 0),
                    "f1": ov.get("f1", 0),
                })
            except Exception as e:
                results.append({"name": name, "error": str(e),
                                "map50": 0, "map5095": 0, "precision": 0, "recall": 0, "f1": 0})
        return results
    except Exception as e:
        return {"error": str(e)}


def _parse_filters(s: str):
    """Parse Qt-style filter string to tkinter format."""
    pairs = []
    for part in s.split(";;"):
        part = part.strip()
        if "(" in part and ")" in part:
            label = part[:part.index("(")].strip()
            exts = part[part.index("(") + 1:part.index(")")].strip()
            pairs.append((label, exts))
        else:
            pairs.append(("Files", part))
    return pairs or [("All files", "*.*")]


# ── Launch ──────────────────────────────────────────────
def main():
    import uvicorn
    port = int(os.environ.get("PORT", 8765))
    print(f"\n  Visualizer running at http://localhost:{port}\n")
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="warning")


if __name__ == "__main__":
    main()
