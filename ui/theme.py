"""
Onyx-inspired design token system for PySide6.

Color palette and semantic tokens adapted from Onyx (MIT License).
https://github.com/onyx-dot-app/onyx
"""

# ── Base Grey Scale ──────────────────────────────────────────────────
_GREY = {
    100: "#000000", 98: "#050505", 96: "#0a0a0a", 94: "#0f0f0f",
    92: "#141414", 90: "#1a1a1a", 85: "#262626", 80: "#333333",
    75: "#404040", 70: "#4d4d4d", 60: "#555555", 50: "#808080",
    40: "#a4a4a4", 30: "#b2b2b2", 20: "#cccccc", 10: "#e6e6e6",
    8: "#ebebeb", 6: "#f0f0f0", 4: "#f5f5f5", 2: "#fafafa", 0: "#ffffff",
}

# ── Stone Tint Scale ─────────────────────────────────────────────────
_STONE = {
    98: "#0b0b0f", 95: "#19191e", 90: "#26262b", 85: "#323239",
    80: "#3f3f46", 60: "#54545d", 50: "#7c7c83", 40: "#a4a4ab",
    20: "#cccccf", 10: "#e6e6e9", 5: "#f0f0f1", 2: "#fafafa",
}

# ── Accent Scales ────────────────────────────────────────────────────
_BLUE = {
    95: "#040e25", 90: "#091938", 85: "#11254e", 80: "#173268",
    60: "#3363c3", 50: "#286df8", 45: "#397bff", 40: "#508afb",
    20: "#9bbeff", 10: "#cddfff", 5: "#e7effc", 1: "#f8fafe",
}
_GREEN = {
    95: "#001503", 90: "#002207", 85: "#00320d", 80: "#004214",
    60: "#008933", 50: "#00a43f", 40: "#2eaa4d", 20: "#91d099",
    10: "#c9e8cc", 5: "#e6f2e7", 1: "#f8fbf8",
}
_RED = {
    95: "#210504", 90: "#330b09", 85: "#481310", 80: "#5f1a16",
    60: "#b02b27", 50: "#dc2626", 45: "#f23a36", 40: "#e8594e",
    20: "#f8a59b", 10: "#fed2cc", 5: "#fceae7", 1: "#fef7f6",
}
_ORANGE = {
    95: "#200600", 90: "#320d01", 85: "#471602", 80: "#5d1e01",
    60: "#b44105", 55: "#ce4b05", 50: "#ec5b13", 40: "#e1642f",
    20: "#f5a88b", 10: "#fcd4c5", 5: "#fbeae4", 1: "#fef9f7",
}
_PURPLE = {
    95: "#140921", 90: "#211132", 85: "#301b47", 80: "#41255e",
    60: "#7e4bb2", 50: "#9948e3", 45: "#a361e6", 40: "#a96fe8",
    20: "#ccaef2", 10: "#e5d6fa", 5: "#f1ebfa", 1: "#f9f7fd",
}

# ── Semantic Tokens ──────────────────────────────────────────────────
_is_dark = False


def _light():
    return {
        # Text
        "text_primary": _GREY[90],       # near-black
        "text_secondary": _GREY[60],
        "text_muted": _GREY[50],
        "text_faint": _GREY[40],
        "text_disabled": _GREY[20],
        # Background
        "bg_base": _GREY[0],             # white
        "bg_surface": _STONE[2],         # very light warm
        "bg_raised": _STONE[5],
        "bg_overlay": _STONE[10],
        "bg_heavy": _STONE[20],
        "bg_inverted": _GREY[100],
        # Border
        "border_subtle": _GREY[10],
        "border_default": _GREY[20],
        "border_strong": _GREY[40],
        # Accent / Action
        "accent": _BLUE[50],
        "accent_hover": _BLUE[40],
        "accent_muted": _BLUE[10],
        "accent_bg": _BLUE[5],
        # Status
        "success": _GREEN[60],
        "success_bg": _GREEN[5],
        "info": _BLUE[50],
        "info_bg": _BLUE[5],
        "warning": _ORANGE[55],
        "warning_bg": _ORANGE[5],
        "error": _RED[50],
        "error_bg": _RED[5],
        # Progress
        "progress_chunk": _BLUE[50],
        "progress_bg": _GREY[6],
        # Scrollbar / Slider
        "slider_groove": _GREY[10],
        "slider_handle": _BLUE[50],
        # Shadow (used as border-like effect in QSS)
        "shadow": "rgba(0,0,0,0.08)",
        # Tab
        "tab_bg": _STONE[5],
        "tab_selected": _GREY[0],
        "tab_hover": _STONE[10],
        "tab_text": _GREY[60],
        "tab_text_selected": _GREY[90],
        # Menu
        "menu_bg": _GREY[0],
        "menu_hover": _STONE[5],
        "menubar_bg": _STONE[2],
        # Selection
        "selection_bg": _BLUE[5],
        "list_selected": _STONE[5],
    }


def _dark():
    return {
        # Text
        "text_primary": _GREY[10],
        "text_secondary": _GREY[40],
        "text_muted": _GREY[50],
        "text_faint": _GREY[60],
        "text_disabled": _GREY[75],
        # Background
        "bg_base": _GREY[100],
        "bg_surface": _STONE[95],
        "bg_raised": _STONE[90],
        "bg_overlay": _STONE[85],
        "bg_heavy": _STONE[80],
        "bg_inverted": _GREY[0],
        # Border
        "border_subtle": _GREY[80],
        "border_default": _GREY[60],
        "border_strong": _GREY[50],
        # Accent / Action
        "accent": _BLUE[45],
        "accent_hover": _BLUE[50],
        "accent_muted": _BLUE[80],
        "accent_bg": _BLUE[90],
        # Status
        "success": _GREEN[50],
        "success_bg": _GREEN[90],
        "info": _BLUE[50],
        "info_bg": _BLUE[90],
        "warning": _ORANGE[50],
        "warning_bg": _ORANGE[90],
        "error": _RED[50],
        "error_bg": _RED[90],
        # Progress
        "progress_chunk": _BLUE[45],
        "progress_bg": _STONE[90],
        # Scrollbar / Slider
        "slider_groove": _STONE[85],
        "slider_handle": _BLUE[45],
        # Shadow
        "shadow": "rgba(255,255,255,0.05)",
        # Tab
        "tab_bg": _STONE[90],
        "tab_selected": _STONE[85],
        "tab_hover": _STONE[80],
        "tab_text": _GREY[40],
        "tab_text_selected": _GREY[10],
        # Menu
        "menu_bg": _STONE[90],
        "menu_hover": _STONE[85],
        "menubar_bg": _STONE[95],
        # Selection
        "selection_bg": _BLUE[90],
        "list_selected": _STONE[85],
    }


def current_tokens():
    """Return the active semantic token dict."""
    return _dark() if _is_dark else _light()


def set_dark(dark: bool):
    global _is_dark
    _is_dark = dark


def is_dark():
    return _is_dark


# ── Convenience color accessors ──────────────────────────────────────
def color(token: str) -> str:
    """Get a hex color for the given semantic token name."""
    return current_tokens()[token]


# ── QSS Generator ───────────────────────────────────────────────────
def generate_qss(dark: bool = False) -> str:
    """Generate a complete Qt stylesheet from Onyx-style tokens."""
    t = _dark() if dark else _light()
    return f"""
/* ── Global ─────────────────────────────────────────── */
QMainWindow, QWidget {{
    background-color: {t["bg_base"]};
    color: {t["text_primary"]};
    font-family: "Segoe UI", "Noto Sans", "Malgun Gothic", sans-serif;
    font-size: 13px;
}}

/* ── Tab Widget ─────────────────────────────────────── */
QTabWidget::pane {{
    border: 1px solid {t["border_subtle"]};
    background: {t["bg_base"]};
    border-radius: 4px;
}}
QTabBar::tab {{
    background: {t["tab_bg"]};
    color: {t["tab_text"]};
    padding: 7px 18px;
    margin-right: 2px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    border: 1px solid {t["border_subtle"]};
    border-bottom: none;
}}
QTabBar::tab:selected {{
    background: {t["tab_selected"]};
    color: {t["tab_text_selected"]};
    font-weight: 600;
}}
QTabBar::tab:hover:!selected {{
    background: {t["tab_hover"]};
}}

/* ── Group Box ──────────────────────────────────────── */
QGroupBox {{
    border: 1px solid {t["border_subtle"]};
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 18px;
    color: {t["text_secondary"]};
    font-weight: 600;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 8px;
    color: {t["text_primary"]};
}}

/* ── Buttons ────────────────────────────────────────── */
QPushButton {{
    background: {t["bg_raised"]};
    color: {t["text_primary"]};
    border: 1px solid {t["border_subtle"]};
    border-radius: 6px;
    padding: 6px 16px;
    min-height: 20px;
    font-weight: 500;
}}
QPushButton:hover {{
    background: {t["bg_overlay"]};
    border-color: {t["border_default"]};
}}
QPushButton:pressed {{
    background: {t["bg_heavy"]};
}}
QPushButton:disabled {{
    background: {t["bg_surface"]};
    color: {t["text_disabled"]};
    border-color: {t["border_subtle"]};
}}

/* ── Inputs ─────────────────────────────────────────── */
QLineEdit, QTextEdit, QPlainTextEdit, QSpinBox, QDoubleSpinBox, QComboBox {{
    background: {t["bg_surface"]};
    color: {t["text_primary"]};
    border: 1px solid {t["border_subtle"]};
    border-radius: 6px;
    padding: 5px 8px;
    min-height: 20px;
    selection-background-color: {t["accent_muted"]};
}}
QLineEdit:focus, QTextEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {{
    border-color: {t["accent"]};
}}
QComboBox::drop-down {{
    border: none;
    width: 24px;
}}
QComboBox QAbstractItemView {{
    background: {t["menu_bg"]};
    color: {t["text_primary"]};
    border: 1px solid {t["border_subtle"]};
    selection-background-color: {t["list_selected"]};
}}

/* ── Table ──────────────────────────────────────────── */
QTableWidget, QTableView {{
    background: {t["bg_base"]};
    color: {t["text_primary"]};
    gridline-color: {t["border_subtle"]};
    border: 1px solid {t["border_subtle"]};
    border-radius: 6px;
    selection-background-color: {t["selection_bg"]};
}}
QHeaderView::section {{
    background: {t["bg_raised"]};
    color: {t["text_secondary"]};
    border: none;
    border-bottom: 1px solid {t["border_subtle"]};
    border-right: 1px solid {t["border_subtle"]};
    padding: 6px 8px;
    font-weight: 600;
    font-size: 12px;
}}

/* ── Progress Bar ───────────────────────────────────── */
QProgressBar {{
    background: {t["progress_bg"]};
    border: 1px solid {t["border_subtle"]};
    border-radius: 6px;
    text-align: center;
    color: {t["text_secondary"]};
    min-height: 18px;
    padding: 1px;
    font-size: 11px;
}}
QProgressBar::chunk {{
    background: {t["progress_chunk"]};
    border-radius: 5px;
}}

/* ── Scroll Area / List ─────────────────────────────── */
QScrollArea {{
    border: none;
    background: transparent;
}}
QListWidget {{
    background: {t["bg_surface"]};
    color: {t["text_primary"]};
    border: 1px solid {t["border_subtle"]};
    border-radius: 6px;
    outline: none;
}}
QListWidget::item {{
    padding: 4px 8px;
    border-radius: 4px;
}}
QListWidget::item:selected {{
    background: {t["list_selected"]};
}}
QListWidget::item:hover:!selected {{
    background: {t["bg_raised"]};
}}

/* ── Labels & Checkbox ──────────────────────────────── */
QLabel {{
    color: {t["text_primary"]};
    background: transparent;
}}
QCheckBox {{
    color: {t["text_primary"]};
    spacing: 6px;
}}
QCheckBox::indicator {{
    width: 16px;
    height: 16px;
    border: 1px solid {t["border_default"]};
    border-radius: 4px;
    background: {t["bg_surface"]};
}}
QCheckBox::indicator:checked {{
    background: {t["accent"]};
    border-color: {t["accent"]};
}}

/* ── Status Bar ─────────────────────────────────────── */
QStatusBar {{
    background: {t["bg_surface"]};
    color: {t["text_muted"]};
    border-top: 1px solid {t["border_subtle"]};
    font-size: 12px;
}}

/* ── Menu Bar ───────────────────────────────────────── */
QMenuBar {{
    background: {t["menubar_bg"]};
    color: {t["text_primary"]};
    border-bottom: 1px solid {t["border_subtle"]};
    padding: 2px 0;
}}
QMenuBar::item {{
    padding: 5px 12px;
    border-radius: 4px;
}}
QMenuBar::item:selected {{
    background: {t["menu_hover"]};
}}
QMenu {{
    background: {t["menu_bg"]};
    color: {t["text_primary"]};
    border: 1px solid {t["border_subtle"]};
    border-radius: 8px;
    padding: 4px;
}}
QMenu::item {{
    padding: 6px 24px;
    border-radius: 4px;
}}
QMenu::item:selected {{
    background: {t["menu_hover"]};
}}
QMenu::separator {{
    height: 1px;
    background: {t["border_subtle"]};
    margin: 4px 8px;
}}

/* ── Slider ─────────────────────────────────────────── */
QSlider::groove:horizontal {{
    background: {t["slider_groove"]};
    height: 4px;
    border-radius: 2px;
}}
QSlider::handle:horizontal {{
    background: {t["slider_handle"]};
    width: 14px;
    height: 14px;
    margin: -5px 0;
    border-radius: 7px;
}}
QSlider::handle:horizontal:hover {{
    background: {t["accent_hover"]};
}}

/* ── Splitter ───────────────────────────────────────── */
QSplitter::handle {{
    background: {t["border_subtle"]};
    width: 1px;
}}

/* ── Scroll Bar ─────────────────────────────────────── */
QScrollBar:vertical {{
    background: transparent;
    width: 8px;
    margin: 0;
}}
QScrollBar::handle:vertical {{
    background: {t["text_disabled"]};
    border-radius: 4px;
    min-height: 24px;
}}
QScrollBar::handle:vertical:hover {{
    background: {t["text_muted"]};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}
QScrollBar:horizontal {{
    background: transparent;
    height: 8px;
    margin: 0;
}}
QScrollBar::handle:horizontal {{
    background: {t["text_disabled"]};
    border-radius: 4px;
    min-width: 24px;
}}
QScrollBar::handle:horizontal:hover {{
    background: {t["text_muted"]};
}}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0;
}}

/* ── Tool Tip ───────────────────────────────────────── */
QToolTip {{
    background: {t["bg_overlay"]};
    color: {t["text_primary"]};
    border: 1px solid {t["border_subtle"]};
    border-radius: 6px;
    padding: 4px 8px;
    font-size: 12px;
}}
"""


# ── Inline style helpers ─────────────────────────────────────────────
def muted_text_style() -> str:
    t = current_tokens()
    return f"color: {t['text_muted']}; font-size: 11px;"


def description_style() -> str:
    t = current_tokens()
    return f"color: {t['text_muted']}; font-size: 11px; margin-bottom: 4px;"


def heading_style() -> str:
    t = current_tokens()
    return f"font-weight: 600; font-size: 13px; color: {t['text_primary']};"


def card_style() -> str:
    t = current_tokens()
    return f"border: 1px solid {t['border_subtle']}; background: {t['bg_raised']}; border-radius: 6px;"


def placeholder_style() -> str:
    t = current_tokens()
    return f"color: {t['text_muted']}; font-size: 14px;"


def remove_btn_style() -> str:
    t = current_tokens()
    return f"color: {t['error']}; font-weight: bold; border: none; background: transparent;"


def image_card_style() -> str:
    t = current_tokens()
    return f"border: 2px solid {t['border_subtle']}; background: {t['bg_raised']}; border-radius: 4px;"


def best_cell_colors():
    """Return (bg_hex, fg_hex) for highlighting best metric cells."""
    t = current_tokens()
    return t["success_bg"], t["success"]


def normal_cell_colors():
    """Return (bg_hex, fg_hex) for normal metric cells."""
    t = current_tokens()
    return t["bg_raised"], t["text_primary"]
