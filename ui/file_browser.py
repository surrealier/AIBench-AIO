"""Videos / Models 폴더 파일 목록 패널"""
import os

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget,
    QListWidgetItem, QPushButton, QFileDialog, QSizePolicy,
    QScrollBar, QComboBox, QSpinBox, QSlider,
)

from core.app_config import AppConfig
from core.model_loader import MODEL_TYPES

VIDEO_EXTS = {".mp4", ".avi", ".mov", ".mkv", ".wmv", ".flv", ".ts", ".m4v",
              ".jpg", ".jpeg", ".png", ".bmp"}
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp"}
MODEL_EXTS = {".onnx", ".pt"}


class FileBrowserWidget(QWidget):
    video_selected = Signal(str)   # 절대 경로
    model_selected = Signal(str)
    model_type_changed = Signal()
    batch_changed = Signal(int)
    conf_changed = Signal(float)

    def __init__(self, config: AppConfig, videos_dir: str = "Videos",
                 models_dir: str = "Models", parent=None):
        super().__init__(parent)
        self._config = config
        self.videos_dir = videos_dir
        self.models_dir = models_dir

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        # --- 모델 설정 ---
        row1 = QHBoxLayout()
        row1.setSpacing(4)
        row1.addWidget(QLabel("모델:"))
        self._model_type_combo = QComboBox()
        self._model_type_combo.setSizeAdjustPolicy(QComboBox.AdjustToMinimumContentsLengthWithIcon)
        self._model_type_combo.setMinimumContentsLength(6)
        self._populate_model_types()
        self._model_type_combo.currentIndexChanged.connect(self._on_model_type_changed)
        row1.addWidget(self._model_type_combo, 1)
        row1.addWidget(QLabel("배치:"))
        self._batch_spin = QSpinBox()
        self._batch_spin.setRange(1, 16)
        self._batch_spin.setValue(config.batch_size)
        self._batch_spin.setFixedWidth(50)
        self._batch_spin.valueChanged.connect(self._on_batch_changed)
        row1.addWidget(self._batch_spin)
        layout.addLayout(row1)

        row2 = QHBoxLayout()
        row2.setSpacing(4)
        row2.addWidget(QLabel("신뢰도:"))
        self._conf_slider = QSlider(Qt.Horizontal)
        self._conf_slider.setRange(1, 99)
        self._conf_slider.setValue(int(config.conf_threshold * 100))
        self._conf_label = QLabel(f"{config.conf_threshold:.2f}")
        self._conf_slider.valueChanged.connect(self._on_conf_changed)
        row2.addWidget(self._conf_slider, 1)
        row2.addWidget(self._conf_label)
        layout.addLayout(row2)

        # --- 모델 패널 ---
        layout.addWidget(QLabel("모델 (ONNX / PT)"))
        self._model_list = QListWidget()
        self._model_list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._model_list.itemDoubleClicked.connect(self._on_model_double_clicked)
        self._model_list.setHorizontalScrollMode(QListWidget.ScrollPerPixel)
        self._model_list.setVerticalScrollMode(QListWidget.ScrollPerPixel)
        self._model_list.horizontalScrollBar().setSingleStep(15)
        self._model_list.verticalScrollBar().setSingleStep(15)
        layout.addWidget(self._model_list)

        model_btn_row = QHBoxLayout()
        btn_refresh_model = QPushButton("새로고침")
        btn_browse_model = QPushButton("탐색...")
        btn_refresh_model.clicked.connect(self._populate_models)
        btn_browse_model.clicked.connect(self._browse_model)
        model_btn_row.addWidget(btn_refresh_model)
        model_btn_row.addWidget(btn_browse_model)
        layout.addLayout(model_btn_row)

        # --- 비디오 패널 ---
        layout.addWidget(QLabel("비디오"))
        self._video_list = QListWidget()
        self._video_list.itemDoubleClicked.connect(self._on_video_double_clicked)
        self._video_list.setHorizontalScrollMode(QListWidget.ScrollPerPixel)
        self._video_list.setVerticalScrollMode(QListWidget.ScrollPerPixel)
        self._video_list.horizontalScrollBar().setSingleStep(15)
        self._video_list.verticalScrollBar().setSingleStep(15)
        layout.addWidget(self._video_list)

        video_btn_row = QHBoxLayout()
        btn_refresh_video = QPushButton("새로고침")
        btn_browse_video = QPushButton("탐색...")
        btn_refresh_video.clicked.connect(self._populate_videos)
        btn_browse_video.clicked.connect(self._browse_video)
        video_btn_row.addWidget(btn_refresh_video)
        video_btn_row.addWidget(btn_browse_video)
        layout.addLayout(video_btn_row)

        self._populate_models()
        self._populate_videos()

    def _populate_list(self, list_widget: QListWidget, directory: str, exts: set):
        list_widget.clear()
        if not os.path.isdir(directory):
            return
        for fname in sorted(os.listdir(directory)):
            if os.path.splitext(fname)[1].lower() in exts:
                item = QListWidgetItem(fname)
                item.setData(256, os.path.abspath(os.path.join(directory, fname)))
                list_widget.addItem(item)

    def _populate_models(self):
        self._populate_list(self._model_list, self.models_dir, MODEL_EXTS)

    def _populate_videos(self):
        self._populate_list(self._video_list, self.videos_dir, VIDEO_EXTS)

    def _on_model_double_clicked(self, item: QListWidgetItem):
        self.model_selected.emit(item.data(256))

    def _on_video_double_clicked(self, item: QListWidgetItem):
        self.video_selected.emit(item.data(256))

    def _browse_model(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "모델 파일 선택", self.models_dir,
            "모델 파일 (*.onnx *.pt)"
        )
        if path:
            self.model_selected.emit(path)

    def _browse_video(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "비디오/이미지 파일 선택", self.videos_dir,
            "미디어 파일 (*.mp4 *.avi *.mov *.mkv *.wmv *.flv *.ts *.m4v *.jpg *.jpeg *.png *.bmp)"
        )
        if path:
            self.video_selected.emit(path)

    def add_external_file(self, path: str):
        """드래그앤드롭 등 외부에서 파일이 들어왔을 때 목록에 추가"""
        ext = os.path.splitext(path)[1].lower()
        if ext in VIDEO_EXTS:
            self.video_selected.emit(path)
        elif ext in MODEL_EXTS:
            self.model_selected.emit(path)

    # --- 모델 설정 핸들러 ---
    def _populate_model_types(self):
        self._model_type_combo.blockSignals(True)
        self._model_type_combo.clear()
        for key, label in MODEL_TYPES.items():
            self._model_type_combo.addItem(label, key)
        for name in self._config.custom_model_types:
            self._model_type_combo.addItem(name, f"custom:{name}")
        # 현재 설정값 복원
        cur = self._config.model_type
        for i in range(self._model_type_combo.count()):
            if self._model_type_combo.itemData(i) == cur:
                self._model_type_combo.setCurrentIndex(i)
                break
        self._model_type_combo.blockSignals(False)

    def refresh_model_types(self):
        self._populate_model_types()

    def _on_model_type_changed(self, idx: int):
        key = self._model_type_combo.currentData()
        if key:
            self._config.model_type = key
        self.model_type_changed.emit()

    def _on_batch_changed(self, val: int):
        self._config.batch_size = val
        self.batch_changed.emit(val)

    def _on_conf_changed(self, val: int):
        self._config.conf_threshold = val / 100.0
        self._conf_label.setText(f"{self._config.conf_threshold:.2f}")
        self.conf_changed.emit(self._config.conf_threshold)
