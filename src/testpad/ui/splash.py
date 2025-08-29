from __future__ import annotations

import os
from typing import Optional

from PySide6.QtCore import Qt, QSize, QRect, QTimer
from PySide6.QtGui import QPixmap, QPainter, QGuiApplication, QFontMetrics, QColor, QPen
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QProgressBar,
    QFrame,
    QHBoxLayout,
    QGraphicsDropShadowEffect,
    QSizePolicy,
)

try:
    from PySide6.QtSvg import QSvgRenderer  # type: ignore
except Exception:  # pragma: no cover - optional dependency at runtime
    QSvgRenderer = None  # type: ignore


def resolve_resource_path(relative: str) -> str:
    """Resolve a resource path for dev and PyInstaller builds.

    Looks in package (this file's directory), PyInstaller's _MEIPASS, then project root.
    """
    base_dir = os.path.dirname(os.path.dirname(__file__))  # src/testpad
    pkg_path = os.path.join(base_dir, "resources", relative)
    if os.path.exists(pkg_path):
        return pkg_path
    meipass = getattr(__import__('sys'), '_MEIPASS', '')
    if meipass:
        alt = os.path.join(meipass, 'resources', relative)
        if os.path.exists(alt):
            return alt
    # fallback to repo-root layout during development
    cwd_alt = os.path.join(os.getcwd(), 'src', 'testpad', 'resources', relative)
    return cwd_alt


def _render_svg_to_pixmap(svg_path: str, size: QSize) -> Optional[QPixmap]:
    if QSvgRenderer is None:
        return None
    if not os.path.exists(svg_path):
        return None
    renderer = QSvgRenderer(svg_path)
    if not renderer.isValid():
        return None
    pm = QPixmap(size)
    pm.fill(Qt.transparent)
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


class SplashScreen(QWidget):
    """
    Simple, rounded, white splash window with a progress bar.
    Call update_progress(percent, message) during startup.
    """

    def __init__(self, version_text: str, logo_svg_relative: str = 'FUS_logo_text_icon_ms_v3.svg') -> None:
        super().__init__(
            None,
            Qt.WindowType.SplashScreen | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint,
        )
        # Make real rounded corners by painting our own background
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)

        self._frame = QFrame()
        self._frame.setObjectName("splashFrame")
        self._frame.setStyleSheet(
            """
            QFrame#splashFrame {
                background: white;
                border-radius: 16px;
            }
            QLabel#versionLabel { color: #555; }
            QLabel#messageLabel { color: #333; }
            QProgressBar {
                /* Rounded pill track */
                background: #f5f5f5;
                border: 1px solid #ddd;
                border-radius: 18px; /* half of height for fully rounded ends */
                height: 36px;
                padding: 0px;       /* no padding so the chunk can meet the curve */
                text-align: center;
                font: 14pt;
                color: black;
            }
            QProgressBar::chunk {
                /* Green fill with matching rounded caps */
                background-color: #69b19b;
                border-radius: 18px; /* match track radius for seamless ends */
                margin: 0px;         /* ensure fill touches the rounded edge */
            }
            """
        )
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(24)
        shadow.setOffset(0, 4)
        shadow.setColor(Qt.black)
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

        # Version
        self.version_label = QLabel(version_text)
        self.version_label.setObjectName("versionLabel")
        self.version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.version_label, alignment=Qt.AlignmentFlag.AlignHCenter)

        # Progress bar (custom rounded painter to ensure curved fill caps)
        self.progress = RoundedProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setTextVisible(True)
        self.progress.setFormat("%p%")
        self.progress.setFixedHeight(36)
        layout.addWidget(self.progress, alignment=Qt.AlignmentFlag.AlignHCenter)

        # Message (below progress, reduces gap under logo)
        self.message_label = QLabel("Starting…")
        self.message_label.setObjectName("messageLabel")
        self.message_label.setWordWrap(False)
        self.message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.message_label.setFixedHeight(22)
        self.message_label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        layout.addWidget(self.message_label, alignment=Qt.AlignmentFlag.AlignHCenter)

        outer_layout.addWidget(self._frame)

        # Load logo from SVG
        svg_path = resolve_resource_path(logo_svg_relative)
        # Render a larger logo for better visual weight
        pm = _render_svg_to_pixmap(svg_path, QSize(760, 220))
        if isinstance(pm, QPixmap):
            self.logo_label.setPixmap(pm)
            # Fix label to pixmap size so Qt does not stretch it
            self.logo_label.setFixedSize(pm.size())
            # Match progress bar width to ~90% of the logo width and center
            bar_width = int(pm.size().width() * 0.9)
            self.progress.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
            self.progress.setFixedWidth(bar_width)
            # Constrain labels to the same width for consistent centering
            self.version_label.setFixedWidth(bar_width)
            self.message_label.setFixedWidth(bar_width)
        else:
            # Fallback to text if rendering fails
            base_name = os.path.basename(svg_path)
            self.logo_label.setText(base_name)

        # Wider splash, slightly taller than the logo aspect ratio
        target_width = (pm.size().width() if isinstance(pm, QPixmap) else 760) + (m * 2)
        self.resize(target_width, 360)

    def paintEvent(self, ev):  # noqa: N802
        # Transparent window, so we only need to let the frame paint itself.
        return super().paintEvent(ev)

    def update_progress(self, percent: int, message: Optional[str] = None) -> None:
        self.progress.setValue(max(0, min(100, percent)))
        if message is not None:
            # Elide long messages to fit within the fixed width without wrapping
            self._full_message = message
            fm = QFontMetrics(self.message_label.font())
            available = max(0, self.message_label.width() - 4)
            elided = fm.elidedText(self._full_message, Qt.TextElideMode.ElideRight, available)
            self.message_label.setText(elided)
            self.message_label.setToolTip(self._full_message)
        # keep UI responsive during startup
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

    def __init__(self, parent: Optional[QWidget] = None) -> None:  # type: ignore[name-defined]
        super().__init__(parent)
        self._minimum = 0
        self._maximum = 100
        self._value = 0
        self._text_visible = True
        self._format = "%p%"
        # Colors to match prior stylesheet
        self._track_bg = QColor("#f5f5f5")
        self._track_border = QColor("#dddddd")
        self._fill = QColor("#69b19b")

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
        return int(round((self._value - self._minimum) * 100 / span))

    def _text(self) -> str:
        txt = self._format
        if "%p%" in txt:
            txt = txt.replace("%p%", f"{self._percent()}%")
        return txt

    def paintEvent(self, ev):  # noqa: N802
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        # Geometry and radius (half height for a pill)
        w = max(0, self.width())
        h = max(0, self.height())
        if w == 0 or h == 0:
            return
        rect = self.rect().adjusted(1, 1, -1, -1)  # account for 1px border
        radius = rect.height() / 2.0

        # Track: background + 1px border
        p.setPen(QPen(self._track_border, 1))
        p.setBrush(self._track_bg)
        p.drawRoundedRect(rect, radius, radius)

        # Fill amount (clamped)
        percent = self._percent() / 100.0
        if percent > 0.0:
            fill_w = int(rect.width() * percent)
            fill_rect = rect.adjusted(0, 0, -(rect.width() - fill_w), 0)
            # Draw fill with same radius so ends are always curved
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(self._fill)
            # Ensure a minimum width for visible rounded cap at very low values
            if fill_w <= 0:
                pass
            else:
                p.drawRoundedRect(fill_rect, radius, radius)

        # Text overlay (centered)
        if self._text_visible:
            p.setPen(QColor("black"))
            p.drawText(self.rect(), int(Qt.AlignmentFlag.AlignCenter), self._text())
        p.end()

if __name__ == "__main__":
    # Minimal harness to preview the splash screen directly
    from PySide6.QtWidgets import QApplication
    import sys

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

    def tick():
        i = state["i"]
        percent = min(100, int((i + 1) / len(steps) * 100))
        splash.update_progress(percent, steps[i])
        state["i"] += 1
        if state["i"] >= len(steps):
            # Keep the splash open for inspection; stop ticking.
            try:
                timer.stop()
            except Exception:
                pass

    timer = QTimer()
    timer.timeout.connect(tick)
    timer.setInterval(400)
    timer.start()

    sys.exit(app.exec())
