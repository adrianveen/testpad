from __future__ import annotations

import contextlib
import os
from pathlib import Path

from PySide6.QtCore import QRect, QRectF, QSize, Qt, QTimer
from PySide6.QtGui import QColor, QFontMetrics, QGuiApplication, QPainter, QPen, QPixmap
from PySide6.QtWidgets import (
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

try:
    from PySide6.QtSvg import QSvgRenderer
except Exception:  # pragma: no cover - optional dependency at runtime
    QSvgRenderer = None  # type: ignore


def resolve_resource_path(relative: str) -> str:
    """Resolve a resource path for dev and PyInstaller builds.

    Looks in package (this file's directory), PyInstaller's _MEIPASS, then project root.
    """
    base_dir = os.path.dirname(Path(__file__).parent)  # src/testpad
    pkg_path = os.path.join(base_dir, "resources", relative)
    if Path(pkg_path).exists():
        return pkg_path
    meipass = getattr(__import__("sys"), "_MEIPASS", "")
    if meipass:
        alt = os.path.join(meipass, "resources", relative)
        if Path(alt).exists():
            return alt
    # fallback to repo-root layout during development
    return os.path.join(Path.cwd(), "src", "testpad", "resources", relative)


def _render_svg_to_pixmap(svg_path: str, size: QSize) -> QPixmap | None:
    if QSvgRenderer is None:
        return None
    if not Path(svg_path).exists():
        return None
    renderer = QSvgRenderer(svg_path)
    if not renderer.isValid():
        return None
    pm = QPixmap(size)
    pm.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pm)
    # Preserve aspect ratio within given size
    view_box = renderer.viewBoxF()
    if not view_box.isEmpty():
        scale = min(size.width() / view_box.width(), size.height() / view_box.height())
        w = view_box.width() * scale
        h = view_box.height() * scale
        x = (size.width() - w) / 2
        y = (size.height() - h) / 2
        renderer.render(painter, QRect(int(x), int(y), int(w), int(h)))
    else:
        renderer.render(painter)
    painter.end()
    return pm


def _load_logo_pixmap(
    preferred_png: str, fallback_png: str, fallback_svg: str, size: QSize
) -> QPixmap | None:
    # Try preferred PNG
    p_png = resolve_resource_path(preferred_png)
    if os.path.exists(p_png):
        pm = QPixmap(p_png)
        if not pm.isNull():
            return pm.scaled(
                size,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
    # Fallback PNG
    f_png = resolve_resource_path(fallback_png)
    if os.path.exists(f_png):
        pm = QPixmap(f_png)
        if not pm.isNull():
            return pm.scaled(
                size,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
    # Fallback SVG render if available
    f_svg = resolve_resource_path(fallback_svg)
    return _render_svg_to_pixmap(f_svg, size)


class SplashScreen(QWidget):
    """Simple, rounded, white splash window with a progress bar.

    Call update_progress(percent, message) during startup.
    """

    def __init__(
        self, version_text: str, logo_svg_relative: str = "FUS_logo_text_icon_ms_v3.svg"
    ) -> None:
        super().__init__(
            None,
            Qt.WindowType.SplashScreen
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint,
        )
        # Make real rounded corners by painting our own background
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)

        self._frame = QFrame()
        self._frame.setObjectName("splashFrame")
        # Keep default widget styles; only basic label colors.
        self._frame.setStyleSheet(
            """
            QFrame#splashFrame { background: white; border-radius: 16px; }
            QLabel#versionLabel { color: #555; }
            QLabel#messageLabel { color: black; }
            """
        )
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(24)
        shadow.setOffset(0, 4)
        shadow.setColor(Qt.GlobalColor.black)
        self._frame.setGraphicsEffect(shadow)

        layout = QVBoxLayout(self._frame)
        m = 28
        layout.setContentsMargins(m, m, m, m)
        layout.setSpacing(6)

        # Logo area
        logo_row = QHBoxLayout()
        logo_row.setSpacing(12)

        self.logo_label = QLabel()
        # Preserve aspect ratio by not scaling contents; we fix to the pixmap size below.
        self.logo_label.setScaledContents(False)
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_row.addWidget(self.logo_label, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addLayout(logo_row)

        # App name + Version row
        self.app_label = QLabel("Testpad")
        self.app_label.setObjectName("appLabel")
        self.version_label = QLabel(version_text)
        self.version_label.setObjectName("versionLabel")

        # Increase sizes
        app_font = self.app_label.font()
        app_font.setPointSize(20)
        app_font.setBold(True)
        self.app_label.setFont(app_font)

        ver_font = self.version_label.font()
        ver_font.setPointSize(18)
        self.version_label.setFont(ver_font)

        # Color the app name to match progress fill; version stays black
        self.app_label.setStyleSheet("color: #69b19b;")
        self.version_label.setStyleSheet("color: #69b19b;")

        # Place them side-by-side and center as a group
        self.name_row_wrap = QWidget()
        name_row = QHBoxLayout(self.name_row_wrap)
        name_row.setContentsMargins(0, 0, 0, 0)
        name_row.setSpacing(8)
        name_row.addWidget(self.app_label)
        name_row.addWidget(self.version_label)
        name_row.setAlignment(
            Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter
        )
        layout.addWidget(self.name_row_wrap, alignment=Qt.AlignmentFlag.AlignHCenter)

        # Progress bar — custom, with default-like background and green fill
        self.progress = RoundedProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setTextVisible(True)
        self.progress.setFormat("%p%")
        self.progress.setFixedHeight(24)
        layout.addWidget(self.progress, alignment=Qt.AlignmentFlag.AlignHCenter)

        # Message (below progress, reduces gap under logo)
        self.message_label = QLabel("Starting…")
        self.message_label.setObjectName("messageLabel")
        self.message_label.setWordWrap(False)
        self.message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.message_label.setFixedHeight(22)
        self.message_label.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed
        )
        layout.addWidget(self.message_label, alignment=Qt.AlignmentFlag.AlignHCenter)

        outer_layout.addWidget(self._frame)

        # Load logo from PNG first (preferred), fall back to SVG
        target_size = QSize(760, 220)
        pm = _load_logo_pixmap(
            preferred_png="FUS_logo_text_icon_ms_v3.png",
            fallback_png="fus_icon_transparent.png",
            fallback_svg=logo_svg_relative,
            size=target_size,
        )
        if isinstance(pm, QPixmap):
            self.logo_label.setPixmap(pm)
            # Fix label to pixmap size so Qt does not stretch it
            self.logo_label.setFixedSize(pm.size())
            # Match progress bar width to ~90% of the logo width and center
            bar_width = int(pm.size().width() * 0.9)
            self.progress.setSizePolicy(
                QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed
            )
            self.progress.setFixedWidth(bar_width)
            # Keep app/version row to the same width for alignment
            self.name_row_wrap.setFixedWidth(bar_width)
            # Constrain labels to the same width for consistent centering
            self.message_label.setFixedWidth(bar_width)
        else:
            # Fallback to text if rendering fails
            base_name = "splash_logo.png"
            self.logo_label.setText(base_name)

        # Wider splash, slightly taller than the logo aspect ratio
        target_width = (pm.size().width() if isinstance(pm, QPixmap) else 760) + (m * 2)
        self.resize(target_width, 360)

    def paintEvent(self, ev):
        # Transparent window, so we only need to let the frame paint itself.
        return super().paintEvent(ev)

    def update_progress(self, percent: int, message: str | None = None) -> None:
        self.progress.setValue(max(0, min(100, percent)))
        if message is not None:
            # Elide long messages to fit within the fixed width without wrapping
            self._full_message = message
            fm = QFontMetrics(self.message_label.font())
            available = max(0, self.message_label.width() - 4)
            elided = fm.elidedText(
                self._full_message, Qt.TextElideMode.ElideRight, available
            )
            self.message_label.setText(elided)
            self.message_label.setToolTip(self._full_message)
        # Keep UI responsive and visibly update the progress while loading
        app = QGuiApplication.instance()
        if app:
            app.processEvents()

    def show_centered(self) -> None:
        screen = QGuiApplication.primaryScreen()
        if screen:
            geo = screen.availableGeometry()
            x = geo.x() + (geo.width() - self.width()) // 2
            y = geo.y() + (geo.height() - self.height()) // 2
            self.move(x, y)
        self.show()


class RoundedProgressBar(QWidget):
    """Custom progress bar with fully rounded track and fill caps.

    Supports a subset of QProgressBar API used by the splash: setRange, setValue,
    setTextVisible, setFormat. Width/height and layout are handled by the parent.
    """

    def __init__(self, parent: QWidget | None = None) -> None:  # type: ignore[name-defined]
        super().__init__(parent)
        self._minimum = 0
        self._maximum = 100
        self._value = 0
        self._text_visible = True
        self._format = "%p%"
        # Default-like track and green fill
        self._track_bg = QColor("#f5f5f5")
        self._track_border = QColor("#dddddd")
        self._fill = QColor("#69b19b")  # keep original bar color
        # Transparent background so frame shows around it
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAutoFillBackground(False)

    def setRange(self, minimum: int, maximum: int) -> None:
        self._minimum = minimum
        self._maximum = maximum if maximum > minimum else minimum + 1
        self._value = max(self._minimum, min(self._value, self._maximum))
        self.update()

    def setValue(self, value: int) -> None:
        self._value = max(self._minimum, min(value, self._maximum))
        self.update()

    def setTextVisible(self, visible: bool) -> None:
        self._text_visible = bool(visible)
        self.update()

    def setFormat(self, fmt: str) -> None:
        self._format = fmt or "%p%"
        self.update()

    def _percent(self) -> int:
        span = max(1, self._maximum - self._minimum)
        return round((self._value - self._minimum) * 100 / span)

    def _text(self) -> str:
        txt = self._format
        if "%p%" in txt:
            txt = txt.replace("%p%", f"{self._percent()}%")
        return txt

    def paintEvent(self, ev) -> None:  # noqa: N802
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        w = self.width()
        h = self.height()
        if w <= 0 or h <= 0:
            return

        outer = QRectF(self.rect())
        radius = outer.height() / 2.0

        # Track (background)
        p.setPen(QPen(self._track_border, 1.0))
        p.setBrush(self._track_bg)
        p.drawRoundedRect(outer, radius, radius)

        # Fill amount
        percent = max(0.0, min(1.0, self._percent() / 100.0))
        if percent > 0.0:
            fill_w = outer.width() * percent
            # Clip to the fill width, then draw the same rounded rect as the track
            p.save()
            p.setClipRect(QRectF(outer.left(), outer.top(), fill_w, outer.height()))
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(self._fill)
            p.drawRoundedRect(outer, radius, radius)
            p.restore()

        # Text overlay (centered)
        if self._text_visible:
            p.setPen(QColor("black"))
            p.drawText(self.rect(), int(Qt.AlignmentFlag.AlignCenter), self._text())
        p.end()


if __name__ == "__main__":
    # Minimal harness to preview the splash screen directly
    import sys

    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    splash = SplashScreen(version_text="vTEST")
    splash.show_centered()

    steps = [
        "Importing modules…",
        "Loading resources…",
        "Initializing UI…",
        "Preparing tabs…",
        "Finalizing…",
    ]
    state = {"i": 0}

    def tick() -> None:
        i = state["i"]
        percent = min(100, int((i + 1) / len(steps) * 100))
        splash.update_progress(percent, steps[i])
        state["i"] += 1
        if state["i"] >= len(steps):
            # Keep the splash open for inspection; stop ticking.
            with contextlib.suppress(Exception):
                timer.stop()

    timer = QTimer()
    timer.timeout.connect(tick)
    timer.setInterval(400)
    timer.start()

    sys.exit(app.exec())
