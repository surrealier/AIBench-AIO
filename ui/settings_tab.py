"""설정 탭: conf/두께/라벨크기/클래스별 색상·두께 + 모델 타입 추가"""
import os

import cv2
import numpy as np
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QImage, QPixmap
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QSlider, QSpinBox, QCheckBox, QLabel,
    QGroupBox, QTableWidget, QTableWidgetItem,
    QPushButton, QColorDialog, QHeaderView, QComboBox,
    QDialog, QFileDialog, QScrollArea, QLineEdit,
    QGraphicsScene, QGraphicsView, QGraphicsPixmapItem,
    QMessageBox, QSizePolicy,
)

from core.app_config import AppConfig, CustomModelType
from ui.video_widget import get_palette_color
from ui import theme


# ------------------------------------------------------------------ #
# 사용자 정의 모델 타입 다이얼로그 (#4)
# ------------------------------------------------------------------ #
_ATTR_CHOICES = [
    "x1", "y1", "x2", "y2",
    "x_center", "y_center", "width", "height",
    "objectness", "confidence", "class_id",
]
# conf_class0 ~ conf_class99 는 동적 생성


class CustomModelTypeDialog(QDialog):
    """모델 Output Shape을 시각적으로 매핑하는 다이얼로그"""

    def __init__(self, config: AppConfig, parent=None):
        super().__init__(parent)
        self.setWindowTitle("모델 타입 추가 — Output Shape 매핑")
        self.resize(900, 650)
        self._config = config
        self._session = None
        self._model_path = ""
        self._test_image_path = ""
        self._output_shapes = []
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)

        # 이름
        name_row = QHBoxLayout()
        name_row.addWidget(QLabel("타입 이름:"))
        self._le_name = QLineEdit()
        self._le_name.setPlaceholderText("예: my_custom_detr")
        name_row.addWidget(self._le_name, 1)
        root.addLayout(name_row)

        # 모델 로드
        model_row = QHBoxLayout()
        model_row.addWidget(QLabel("ONNX 모델:"))
        self._lbl_model = QLabel("선택 안 됨")
        self._lbl_model.setStyleSheet(theme.muted_text_style())
        model_row.addWidget(self._lbl_model, 1)
        btn_model = QPushButton("모델 선택…")
        btn_model.clicked.connect(self._browse_model)
        model_row.addWidget(btn_model)
        root.addLayout(model_row)

        # Output shape 정보
        self._lbl_shapes = QLabel("모델을 로드하면 Output Shape이 표시됩니다.")
        self._lbl_shapes.setWordWrap(True)
        root.addWidget(self._lbl_shapes)

        # 출력 텐서 인덱스 선택
        oi_row = QHBoxLayout()
        oi_row.addWidget(QLabel("사용할 출력 텐서:"))
        self._spin_oi = QSpinBox()
        self._spin_oi.setRange(0, 9)
        self._spin_oi.setValue(0)
        self._spin_oi.valueChanged.connect(self._on_output_index_changed)
        oi_row.addWidget(self._spin_oi)
        oi_row.addStretch()
        root.addLayout(oi_row)

        # 차원 역할 매핑 테이블
        grp_dim = QGroupBox("차원별 역할 (dim_roles)")
        dim_lay = QVBoxLayout(grp_dim)
        self._dim_info = QLabel("출력 텐서의 각 차원에 역할을 지정하세요.")
        dim_lay.addWidget(self._dim_info)
        self._dim_combos = []  # 동적 생성
        self._dim_row_layout = QHBoxLayout()
        dim_lay.addLayout(self._dim_row_layout)
        root.addWidget(grp_dim)

        # 속성 역할 매핑 (attrs 차원 내 각 슬롯)
        grp_attr = QGroupBox("속성 매핑 (attr_roles) — 마지막 차원의 각 슬롯")
        attr_lay = QVBoxLayout(grp_attr)
        self._attr_scroll = QScrollArea()
        self._attr_scroll.setWidgetResizable(True)
        self._attr_widget = QWidget()
        self._attr_layout = QVBoxLayout(self._attr_widget)
        self._attr_scroll.setWidget(self._attr_widget)
        self._attr_scroll.setMaximumHeight(200)
        attr_lay.addWidget(self._attr_scroll)
        self._attr_combos = []
        root.addWidget(grp_attr)

        # 옵션
        opt_row = QHBoxLayout()
        self._chk_obj = QCheckBox("Objectness 포함")
        self._chk_nms = QCheckBox("NMS 적용")
        self._chk_nms.setChecked(True)
        opt_row.addWidget(self._chk_obj)
        opt_row.addWidget(self._chk_nms)
        opt_row.addStretch()
        root.addLayout(opt_row)

        # 클래스 이름
        cn_row = QHBoxLayout()
        cn_row.addWidget(QLabel("클래스 이름:"))
        self._le_class_names = QLineEdit()
        self._le_class_names.setPlaceholderText("0:person, 1:car, 2:bike  (비우면 자동)")
        cn_row.addWidget(self._le_class_names, 1)
        root.addLayout(cn_row)

        # 테스트 추론
        test_grp = QGroupBox("테스트 추론")
        test_lay = QVBoxLayout(test_grp)
        test_row = QHBoxLayout()
        test_row.addWidget(QLabel("테스트 이미지:"))
        self._lbl_test_img = QLabel("선택 안 됨")
        test_row.addWidget(self._lbl_test_img, 1)
        btn_test_img = QPushButton("이미지 선택…")
        btn_test_img.clicked.connect(self._browse_test_image)
        test_row.addWidget(btn_test_img)
        btn_run = QPushButton("추론 실행")
        btn_run.clicked.connect(self._run_test)
        test_row.addWidget(btn_run)
        test_lay.addLayout(test_row)

        # 결과 이미지
        self._scene = QGraphicsScene()
        self._view = QGraphicsView(self._scene)
        self._view.setMinimumHeight(200)
        self._pix_item = QGraphicsPixmapItem()
        self._scene.addItem(self._pix_item)
        test_lay.addWidget(self._view)
        self._lbl_test_result = QLabel("")
        test_lay.addWidget(self._lbl_test_result)
        root.addWidget(test_grp)

        # 버튼
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_save = QPushButton("저장")
        btn_save.clicked.connect(self._save)
        btn_cancel = QPushButton("취소")
        btn_cancel.clicked.connect(self.reject)
        btn_row.addWidget(btn_save)
        btn_row.addWidget(btn_cancel)
        root.addLayout(btn_row)

    def _browse_model(self):
        path, _ = QFileDialog.getOpenFileName(self, "ONNX 모델 선택", "", "ONNX (*.onnx)")
        if not path:
            return
        self._model_path = path
        self._lbl_model.setText(os.path.basename(path))
        self._lbl_model.setStyleSheet("")
        try:
            import onnxruntime as ort
            self._session = ort.InferenceSession(path)
            shapes = []
            info_lines = []
            for i, out in enumerate(self._session.get_outputs()):
                shapes.append(out.shape)
                info_lines.append(f"  출력[{i}]: {out.name}  shape={out.shape}  dtype={out.type}")
            self._output_shapes = shapes
            inp = self._session.get_inputs()[0]
            info_lines.insert(0, f"  입력: {inp.name}  shape={inp.shape}  dtype={inp.type}")
            self._lbl_shapes.setText("\n".join(info_lines))
            self._spin_oi.setMaximum(len(shapes) - 1)
            self._on_output_index_changed(0)
        except Exception as e:
            QMessageBox.critical(self, "오류", f"모델 로드 실패: {e}")

    def _on_output_index_changed(self, idx):
        if idx >= len(self._output_shapes):
            return
        shape = self._output_shapes[idx]
        # 차원 역할 콤보 생성
        while self._dim_row_layout.count():
            w = self._dim_row_layout.takeAt(0).widget()
            if w:
                w.deleteLater()
        self._dim_combos = []
        dim_choices = ["batch", "detections", "attrs", "기타"]
        for i, d in enumerate(shape):
            lbl = QLabel(f"dim[{i}]={d}")
            combo = QComboBox()
            combo.addItems(dim_choices)
            if i == 0:
                combo.setCurrentText("batch")
            elif i == len(shape) - 1:
                combo.setCurrentText("attrs")
            else:
                combo.setCurrentText("detections")
            self._dim_row_layout.addWidget(lbl)
            self._dim_row_layout.addWidget(combo)
            self._dim_combos.append(combo)

        # attrs 차원 매핑
        attrs_dim = shape[-1] if isinstance(shape[-1], int) else 0
        self._rebuild_attr_combos(attrs_dim)

    def _rebuild_attr_combos(self, n_attrs):
        # 기존 제거
        while self._attr_layout.count():
            w = self._attr_layout.takeAt(0).widget()
            if w:
                w.deleteLater()
        self._attr_combos = []

        choices = list(_ATTR_CHOICES)
        for i in range(min(n_attrs, 200)):
            choices.append(f"conf_class{i}")

        for i in range(min(n_attrs, 200)):
            row = QHBoxLayout()
            lbl = QLabel(f"[{i}]:")
            combo = QComboBox()
            combo.setEditable(True)
            combo.addItems(choices)
            # 기본 추정
            if i < 4:
                defaults = ["x_center", "y_center", "width", "height"]
                combo.setCurrentText(defaults[i])
            elif i >= 4:
                combo.setCurrentText(f"conf_class{i - 4}")
            w = QWidget()
            rl = QHBoxLayout(w)
            rl.setContentsMargins(0, 0, 0, 0)
            rl.addWidget(lbl)
            rl.addWidget(combo, 1)
            self._attr_layout.addWidget(w)
            self._attr_combos.append(combo)

    def _browse_test_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "테스트 이미지 선택", "",
            "이미지 (*.jpg *.jpeg *.png *.bmp)"
        )
        if path:
            self._test_image_path = path
            self._lbl_test_img.setText(os.path.basename(path))

    def _run_test(self):
        if not self._session or not self._test_image_path:
            QMessageBox.warning(self, "알림", "모델과 테스트 이미지를 먼저 선택하세요.")
            return

        frame = cv2.imread(self._test_image_path)
        if frame is None:
            QMessageBox.warning(self, "알림", "이미지를 읽을 수 없습니다.")
            return

        cmt = self._build_custom_type()
        if not cmt:
            return

        try:
            from core.inference import letterbox, preprocess, postprocess_custom
            inp = self._session.get_inputs()[0]
            h = int(inp.shape[2]) if isinstance(inp.shape[2], int) else 640
            w = int(inp.shape[3]) if isinstance(inp.shape[3], int) else 640
            _, ratio, pad = letterbox(frame, (h, w))
            tensor = preprocess(frame, (h, w))
            outputs = self._session.run(None, {inp.name: tensor})
            result = postprocess_custom(outputs, cmt, cmt.conf_threshold, ratio, pad, frame.shape)

            # 결과 시각화
            vis = frame.copy()
            cn = cmt.class_names or {}
            for box, score, cid in zip(result.boxes, result.scores, result.class_ids):
                x1, y1, x2, y2 = int(box[0]), int(box[1]), int(box[2]), int(box[3])
                cv2.rectangle(vis, (x1, y1), (x2, y2), (0, 255, 0), 2)
                lbl = cn.get(int(cid), f"cls{int(cid)}")
                cv2.putText(vis, f"{lbl} {score:.2f}", (x1, max(y1 - 5, 15)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

            rgb = cv2.cvtColor(vis, cv2.COLOR_BGR2RGB)
            qimg = QImage(rgb.data, rgb.shape[1], rgb.shape[0],
                          rgb.shape[1] * 3, QImage.Format.Format_RGB888).copy()
            pxm = QPixmap.fromImage(qimg)
            self._pix_item.setPixmap(pxm)
            self._scene.setSceneRect(0, 0, pxm.width(), pxm.height())
            self._view.fitInView(self._pix_item, Qt.KeepAspectRatio)
            self._lbl_test_result.setText(f"탐지: {len(result.boxes)}개")
        except Exception as e:
            QMessageBox.critical(self, "추론 오류", str(e))

    def _build_custom_type(self):
        name = self._le_name.text().strip()
        if not name:
            QMessageBox.warning(self, "알림", "타입 이름을 입력하세요.")
            return None
        dim_roles = [c.currentText() for c in self._dim_combos]
        attr_roles = [c.currentText() for c in self._attr_combos]
        # 클래스 이름 파싱
        class_names = None
        cn_text = self._le_class_names.text().strip()
        if cn_text:
            class_names = {}
            for part in cn_text.split(","):
                part = part.strip()
                if ":" in part:
                    k, v = part.split(":", 1)
                    class_names[int(k.strip())] = v.strip()
        return CustomModelType(
            name=name,
            output_index=self._spin_oi.value(),
            dim_roles=dim_roles,
            attr_roles=attr_roles,
            has_objectness=self._chk_obj.isChecked(),
            nms=self._chk_nms.isChecked(),
            class_names=class_names,
        )

    def _save(self):
        cmt = self._build_custom_type()
        if not cmt:
            return
        self._config.custom_model_types[cmt.name] = cmt
        self._config.save()
        QMessageBox.information(self, "저장 완료", f"'{cmt.name}' 모델 타입이 저장되었습니다.")
        self.accept()


# ------------------------------------------------------------------ #
# 설정 탭
# ------------------------------------------------------------------ #
class SettingsTab(QWidget):
    settings_changed = Signal()
    custom_type_added = Signal()

    def __init__(self, config: AppConfig, parent=None):
        super().__init__(parent)
        self._config = config
        self._names: dict = {}

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # --- 모델 타입 추가 ---
        type_group = QGroupBox("모델 타입 관리")
        type_layout = QHBoxLayout(type_group)
        btn_add_type = QPushButton("모델 타입 추가…")
        btn_add_type.setFixedWidth(130)
        btn_add_type.clicked.connect(self._on_add_custom_type)
        type_layout.addWidget(btn_add_type)
        type_layout.addStretch()
        layout.addWidget(type_group)

        # --- 테스트 모델 다운로드 ---
        dl_group = QGroupBox("테스트 모델 다운로드")
        dl_layout = QVBoxLayout(dl_group)
        dl_layout.setSpacing(4)
        dl_desc = QLabel("각 기능을 빠르게 테스트할 수 있는 공식 모델을 다운로드합니다.")
        dl_desc.setWordWrap(True)
        dl_desc.setStyleSheet(theme.muted_text_style())
        dl_layout.addWidget(dl_desc)
        _DL_LINKS = [
            ("Detection (YOLOv8n)", "https://github.com/ultralytics/assets/releases/download/v8.2.0/yolov8n.onnx"),
            ("Classification (YOLOv8n-cls)", "https://github.com/ultralytics/assets/releases/download/v8.2.0/yolov8n-cls.onnx"),
            ("Segmentation (YOLOv8n-seg)", "https://github.com/ultralytics/assets/releases/download/v8.2.0/yolov8n-seg.onnx"),
            ("CLIP Image Encoder", "https://huggingface.co/openai/clip-vit-base-patch32/resolve/main/onnx/model.onnx"),
            ("Embedder (ResNet50)", "https://github.com/onnx/models/raw/main/validated/vision/classification/resnet/model/resnet50-v2-7.onnx"),
        ]
        dl_row = QHBoxLayout()
        for label, url in _DL_LINKS:
            btn = QPushButton(label)
            btn.setToolTip(url)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda _, u=url: __import__('webbrowser').open(u))
            dl_row.addWidget(btn)
        dl_layout.addLayout(dl_row)
        layout.addWidget(dl_group)

        # --- 표시 설정 ---
        global_group = QGroupBox("표시 설정")
        form = QFormLayout(global_group)
        form.setSpacing(6)

        # 박스 두께
        self._thickness_spin = QSpinBox()
        self._thickness_spin.setRange(1, 10)
        self._thickness_spin.setValue(config.box_thickness)
        self._thickness_spin.valueChanged.connect(self._on_thickness_changed)
        form.addRow("박스 두께:", self._thickness_spin)

        # 라벨 크기
        self._label_size_slider = QSlider(Qt.Horizontal)
        self._label_size_slider.setRange(3, 15)
        self._label_size_slider.setValue(int(config.label_size * 10))
        self._label_size_label = QLabel(f"{config.label_size:.1f}")
        self._label_size_slider.valueChanged.connect(self._on_label_size_changed)
        label_size_row = QHBoxLayout()
        label_size_row.addWidget(self._label_size_slider)
        label_size_row.addWidget(self._label_size_label)
        form.addRow("라벨 크기:", label_size_row)

        # 라벨 / Confidence 표시
        self._show_labels_cb = QCheckBox("라벨 표시")
        self._show_labels_cb.setChecked(config.show_labels)
        self._show_labels_cb.stateChanged.connect(self._on_show_labels_changed)

        self._show_conf_cb = QCheckBox("Confidence 표시")
        self._show_conf_cb.setChecked(config.show_confidence)
        self._show_conf_cb.stateChanged.connect(self._on_show_conf_changed)

        self._show_label_bg_cb = QCheckBox("라벨 배경")
        self._show_label_bg_cb.setChecked(config.show_label_bg)
        self._show_label_bg_cb.stateChanged.connect(self._on_show_label_bg_changed)

        toggle_row = QHBoxLayout()
        toggle_row.addWidget(self._show_labels_cb)
        toggle_row.addWidget(self._show_conf_cb)
        toggle_row.addWidget(self._show_label_bg_cb)
        form.addRow("표시 옵션:", toggle_row)

        layout.addWidget(global_group)

        # 저장 버튼 (우측 상단)
        save_row = QHBoxLayout()
        save_row.addStretch()
        btn_save = QPushButton("설정 저장")
        btn_save.setFixedHeight(30)
        btn_save.setMinimumWidth(110)
        btn_save.clicked.connect(self._save)
        save_row.addWidget(btn_save)
        layout.addLayout(save_row)

        # --- 클래스별 설정 테이블 ---
        class_group = QGroupBox("클래스별 설정")
        class_layout = QVBoxLayout(class_group)

        self._table = QTableWidget(0, 4)
        self._table.setHorizontalHeaderLabels(["클래스", "활성화", "색상", "두께"])
        self._table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self._table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self._table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self._table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self._table.setSelectionMode(QTableWidget.NoSelection)
        self._table.verticalHeader().setVisible(False)
        class_layout.addWidget(self._table)

        layout.addWidget(class_group)

    def populate_classes(self, names: dict):
        """모델 로드 시 클래스 테이블 채우기 — 기존 설정값 반영 (#5)"""
        self._names = names
        self._table.setRowCount(0)
        total = len(names)

        for cls_id in sorted(names.keys()):
            name = names[cls_id]
            style = self._config.get_class_style(cls_id)
            row = self._table.rowCount()
            self._table.insertRow(row)

            # 클래스 이름
            name_item = QTableWidgetItem(f"{cls_id}: {name}")
            name_item.setFlags(Qt.ItemIsEnabled)
            self._table.setItem(row, 0, name_item)

            # 활성화 체크박스
            cb = QCheckBox()
            cb.setChecked(style.enabled)
            cb.setStyleSheet("margin-left: 8px;")
            cb.stateChanged.connect(lambda state, cid=cls_id: self._on_class_enabled(cid, bool(state)))
            cb_widget = QWidget()
            cb_layout = QHBoxLayout(cb_widget)
            cb_layout.addWidget(cb)
            cb_layout.setAlignment(Qt.AlignCenter)
            cb_layout.setContentsMargins(0, 0, 0, 0)
            self._table.setCellWidget(row, 1, cb_widget)

            # 색상 버튼 — 저장된 색상이 있으면 그것을 사용 (#5)
            if style.color:
                color = style.color
            else:
                color = get_palette_color(cls_id, total)
            btn_color = QPushButton()
            btn_color.setFixedSize(40, 22)
            r, g, b = color[2], color[1], color[0]  # BGR→RGB
            btn_color.setStyleSheet(f"background-color: rgb({r},{g},{b}); border: 1px solid {theme.color('border_default')}; border-radius: 4px;")
            btn_color.clicked.connect(lambda _, cid=cls_id, btn=btn_color: self._on_color_click(cid, btn))
            self._table.setCellWidget(row, 2, btn_color)

            # 두께 스핀박스
            spin = QSpinBox()
            spin.setRange(0, 10)
            spin.setSpecialValueText("기본")
            spin.setValue(style.thickness or 0)
            spin.valueChanged.connect(lambda val, cid=cls_id: self._on_class_thickness(cid, val))
            self._table.setCellWidget(row, 3, spin)

    # --- 핸들러 ---
    def _on_add_custom_type(self):
        dlg = CustomModelTypeDialog(self._config, self)
        if dlg.exec() == QDialog.Accepted:
            self.custom_type_added.emit()

    def _on_thickness_changed(self, val: int):
        self._config.box_thickness = val
        self.settings_changed.emit()

    def _on_label_size_changed(self, val: int):
        self._config.label_size = val / 10.0
        self._label_size_label.setText(f"{self._config.label_size:.1f}")
        self.settings_changed.emit()

    def _on_show_labels_changed(self, state: int):
        self._config.show_labels = bool(state)
        self.settings_changed.emit()

    def _on_show_conf_changed(self, state: int):
        self._config.show_confidence = bool(state)
        self.settings_changed.emit()

    def _on_show_label_bg_changed(self, state: int):
        self._config.show_label_bg = bool(state)
        self.settings_changed.emit()

    def _on_class_enabled(self, cls_id: int, enabled: bool):
        style = self._config.get_class_style(cls_id)
        style.enabled = enabled
        self._config.set_class_style(cls_id, style)
        self.settings_changed.emit()

    def _on_color_click(self, cls_id: int, btn: QPushButton):
        style = self._config.get_class_style(cls_id)
        init_color = QColor(*reversed(style.color)) if style.color else QColor(0, 255, 0)
        color = QColorDialog.getColor(init_color, self, f"클래스 {cls_id} 색상 선택")
        if color.isValid():
            bgr = (color.blue(), color.green(), color.red())
            style.color = bgr
            self._config.set_class_style(cls_id, style)
            r, g, b = color.red(), color.green(), color.blue()
            btn.setStyleSheet(f"background-color: rgb({r},{g},{b}); border: 1px solid {theme.color('border_default')}; border-radius: 4px;")
            self.settings_changed.emit()

    def _on_class_thickness(self, cls_id: int, val: int):
        style = self._config.get_class_style(cls_id)
        style.thickness = val if val > 0 else None
        self._config.set_class_style(cls_id, style)
        self.settings_changed.emit()

    def _save(self):
        self._config.save()
        self.settings_changed.emit()
