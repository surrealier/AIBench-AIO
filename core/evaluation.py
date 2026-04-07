"""Evaluation metrics — extracted from ui/evaluation_tab.py for headless use."""
import numpy as np


def _compute_iou(box1, box2):
    x1 = max(box1[0], box2[0])
    y1 = max(box1[1], box2[1])
    x2 = min(box1[2], box2[2])
    y2 = min(box1[3], box2[3])
    inter = max(0, x2 - x1) * max(0, y2 - y1)
    a1 = (box1[2] - box1[0]) * (box1[3] - box1[1])
    a2 = (box2[2] - box2[0]) * (box2[3] - box2[1])
    return inter / (a1 + a2 - inter + 1e-9)


def _yolo_to_xyxy(cx, cy, w, h):
    return (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)


def _compute_ap(recalls, precisions):
    mrec = np.concatenate(([0.0], recalls, [1.0]))
    mpre = np.concatenate(([1.0], precisions, [0.0]))
    for i in range(len(mpre) - 2, -1, -1):
        mpre[i] = max(mpre[i], mpre[i + 1])
    ap = 0.0
    for t in np.linspace(0, 1, 101):
        p = mpre[mrec >= t]
        ap += (p.max() if len(p) > 0 else 0.0)
    return ap / 101.0


def evaluate_dataset(gt_data, pred_data, iou_thres=0.5):
    all_classes = set()
    for boxes in list(gt_data.values()) + list(pred_data.values()):
        for b in boxes:
            all_classes.add(b[0])
    if not all_classes:
        return {}

    results = {}
    total_tp = total_fp = total_fn = 0

    for cid in sorted(all_classes):
        preds = []
        gt_per_img = {}
        for stem in set(list(gt_data.keys()) + list(pred_data.keys())):
            gt_boxes = [_yolo_to_xyxy(b[1], b[2], b[3], b[4]) for b in gt_data.get(stem, []) if b[0] == cid]
            gt_per_img[stem] = {"boxes": gt_boxes, "matched": [False] * len(gt_boxes)}
            for b in pred_data.get(stem, []):
                if b[0] == cid:
                    score = b[5] if len(b) > 5 else 0.0
                    preds.append((score, stem, _yolo_to_xyxy(b[1], b[2], b[3], b[4])))
        preds.sort(key=lambda x: -x[0])

        n_gt = sum(len(v["boxes"]) for v in gt_per_img.values())
        if n_gt == 0 and len(preds) == 0:
            continue

        tp_list = []
        for _score, stem, pbox in preds:
            best_iou = 0
            best_j = -1
            for j, gbox in enumerate(gt_per_img[stem]["boxes"]):
                iou = _compute_iou(pbox, gbox)
                if iou > best_iou:
                    best_iou = iou
                    best_j = j
            if best_iou >= iou_thres and best_j >= 0 and not gt_per_img[stem]["matched"][best_j]:
                gt_per_img[stem]["matched"][best_j] = True
                tp_list.append(1)
            else:
                tp_list.append(0)

        tp_arr = np.array(tp_list)
        tp_cum = np.cumsum(tp_arr)
        fp_cum = np.cumsum(1 - tp_arr)
        recalls = tp_cum / max(n_gt, 1)
        precisions = tp_cum / (tp_cum + fp_cum + 1e-9)

        ap = _compute_ap(recalls, precisions) if len(recalls) > 0 else 0.0
        tp_total = int(tp_arr.sum())
        fp_total = len(preds) - tp_total
        fn_total = n_gt - tp_total
        total_tp += tp_total
        total_fp += fp_total
        total_fn += fn_total

        prec = tp_total / (tp_total + fp_total + 1e-9)
        rec = tp_total / (n_gt + 1e-9)
        f1 = 2 * prec * rec / (prec + rec + 1e-9)
        results[cid] = {"ap": ap, "precision": prec, "recall": rec, "f1": f1}

    prec_all = total_tp / (total_tp + total_fp + 1e-9)
    rec_all = total_tp / (total_tp + total_fn + 1e-9)
    f1_all = 2 * prec_all * rec_all / (prec_all + rec_all + 1e-9)
    mean_ap = float(np.mean([v["ap"] for v in results.values()])) if results else 0.0
    results["__overall__"] = {"ap": mean_ap, "precision": prec_all, "recall": rec_all, "f1": f1_all}
    return results


def evaluate_map50_95(gt_data, pred_data):
    aps = []
    for iou_t in np.arange(0.5, 1.0, 0.05):
        res = evaluate_dataset(gt_data, pred_data, iou_t)
        if "__overall__" in res:
            aps.append(res["__overall__"]["ap"])
        else:
            aps.append(0.0)
    return float(np.mean(aps)) if aps else 0.0
