
from PySide6.QtCore import Qt, QTimer, QRectF, Signal
from PySide6.QtGui import QColor, QFont, QPainter, QPen
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
)


# --------------------------------------------------
# COLORS
# --------------------------------------------------

BG_COLOR = "#020B1A"
CYAN = "#43C8FF"
WHITE = "#F4F8FF"
MUTED = "#B2D1ED"
GREEN = "#35D49A"


# --------------------------------------------------
# CIRCULAR PROGRESS INDICATOR
# --------------------------------------------------

class CircularProgress(QWidget):
    """Animated circular loading indicator."""

    def __init__(self, parent=None, size=76):
        super().__init__(parent)

        self.setFixedSize(size, size)
        self.angle = 0

        self.timer = QTimer(self)
        self.timer.setInterval(30)
        self.timer.timeout.connect(self._rotate)
        self.timer.start()

    def _rotate(self):
        self.angle = (self.angle + 8) % 360
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = QRectF(7, 7, self.width() - 14, self.height() - 14)

        painter.setPen(
            QPen(QColor("#18354F"), 6, Qt.PenStyle.SolidLine)
        )
        painter.drawArc(rect, 0, 360 * 16)

        painter.setPen(
            QPen(
                QColor(CYAN),
                6,
                Qt.PenStyle.SolidLine,
                Qt.PenCapStyle.RoundCap,
            )
        )
        painter.drawArc(rect, self.angle * 16, 95 * 16)

        painter.end()

    def stop(self):
        if self.timer.isActive():
            self.timer.stop()


# --------------------------------------------------
# BASE TRANSACTION SCREEN
# --------------------------------------------------

class TransactionScreen(QWidget):
    """Shared full-window background and centered content layout."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setAttribute(
            Qt.WidgetAttribute.WA_StyledBackground, True
        )
        self.setStyleSheet(f"background-color: {BG_COLOR};")

        self.content_layout = QVBoxLayout(self)
        self.content_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.content_layout.setContentsMargins(30, 30, 30, 30)
        self.content_layout.setSpacing(18)

    def add_label(
        self,
        text,
        size,
        color=WHITE,
        bold=False,
        alignment=Qt.AlignmentFlag.AlignCenter,
    ):
        label = QLabel(text, self)
        label.setAlignment(alignment)
        label.setWordWrap(True)

        font = QFont("Segoe UI", size)
        font.setBold(bold)
        label.setFont(font)
        label.setStyleSheet(f"color: {color}; background: transparent;")

        self.content_layout.addWidget(label)
        return label


# --------------------------------------------------
# TRANSACTION PROCESSING SCREEN
# --------------------------------------------------

class TransactionProcessingScreen(TransactionScreen):
    """
    Shows a processing animation for a set duration.

    Signal:
        finished: emitted once when processing completes.
    """

    finished = Signal()

    MESSAGES = {
        "en": {
            "title": "PROCESSING TRANSACTION",
            "message": "Please wait while we process your request.",
            "note": "Please do not remove your card.",
        },
        "hi": {
            "title": "लेन-देन प्रक्रिया जारी है",
            "message": "कृपया प्रतीक्षा करें।",
            "note": "कृपया अपना कार्ड न निकालें।",
        },
        "bn": {
            "title": "লেনদেন প্রক্রিয়াকরণ চলছে",
            "message": "অনুগ্রহ করে অপেক্ষা করুন।",
            "note": "অনুগ্রহ করে কার্ডটি বের করবেন না।",
        },
    }

    def __init__(
        self,
        parent=None,
        language="en",
        duration=4000,
    ):
        super().__init__(parent)

        self.duration = max(1, int(duration))
        self._finished_emitted = False

        messages = self.MESSAGES.get(language, self.MESSAGES["en"])

        self.add_label(
            "ATM TRANSACTION",
            12,
            CYAN,
            True,
        )

        self.add_label(
            messages["title"],
            24,
            WHITE,
            True,
        )

        self.spinner = CircularProgress(self, 82)
        self.content_layout.addWidget(
            self.spinner,
            alignment=Qt.AlignmentFlag.AlignCenter,
        )

        self.add_label(
            messages["message"],
            13,
            MUTED,
        )

        self.add_label(
            messages["note"],
            11,
            "#7899B9",
        )

        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.complete)

    def start(self):
        """Start or restart the processing timer."""
        self._finished_emitted = False
        self.timer.stop()
        self.timer.start(self.duration)
        self.show()
        self.raise_()

    def complete(self):
        """Finish processing exactly once."""
        if self._finished_emitted:
            return

        self._finished_emitted = True
        self.timer.stop()
        self.spinner.stop()
        self.hide()
        self.finished.emit()

    def stop(self):
        """Stop without emitting the finished signal."""
        self.timer.stop()
        self.spinner.stop()
        self.hide()

    def closeEvent(self, event):
        self.stop()
        super().closeEvent(event)


# --------------------------------------------------
# CASH COLLECTION SCREEN
# --------------------------------------------------

class CashCollectionScreen(TransactionScreen):
    """
    Shows a successful withdrawal and asks the user
    to collect their cash.

    Signal:
        closed: emitted when the user closes the screen.
    """

    closed = Signal()

    MESSAGES = {
        "en": {
            "title": "PLEASE COLLECT YOUR CASH",
            "message": "Your transaction was successful.",
            "button": "DONE",
        },
        "hi": {
            "title": "कृपया अपनी नकदी लें",
            "message": "आपका लेन-देन सफल रहा।",
            "button": "हो गया",
        },
        "bn": {
            "title": "অনুগ্রহ করে নগদ সংগ্রহ করুন",
            "message": "আপনার লেনদেন সফল হয়েছে।",
            "button": "সম্পন্ন",
        },
    }

    def __init__(
        self,
        parent=None,
        amount=0,
        language="en",
    ):
        super().__init__(parent)

        self.amount = amount
        self._closed_emitted = False

        messages = self.MESSAGES.get(language, self.MESSAGES["en"])

        self.add_label(
            "TRANSACTION SUCCESSFUL",
            12,
            GREEN,
            True,
        )

        self.add_label(
            messages["title"],
            23,
            WHITE,
            True,
        )

        amount_label = self.add_label(
            f"₹{self.amount:,.2f}",
            38,
            GREEN,
            True,
        )
        amount_label.setMinimumWidth(260)

        self.add_label(
            messages["message"],
            13,
            MUTED,
        )

        self.add_label(
            "Thank you for banking with us.",
            11,
            "#7899B9",
        )

        button_row = QHBoxLayout()
        button_row.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.done_button = QPushButton(messages["button"], self)
        self.done_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.done_button.setMinimumSize(180, 46)
        self.done_button.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        self.done_button.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {CYAN};
                color: #03101F;
                border: none;
                border-radius: 9px;
                padding: 10px 24px;
            }}
            QPushButton:hover {{
                background-color: #79D8FF;
            }}
            QPushButton:pressed {{
                background-color: #28A8E8;
            }}
            """
        )
        self.done_button.clicked.connect(self.finish)

        button_row.addWidget(self.done_button)
        self.content_layout.addSpacing(12)
        self.content_layout.addLayout(button_row)

    def finish(self):
        """Close the cash screen and emit its signal once."""
        if self._closed_emitted:
            return

        self._closed_emitted = True
        self.hide()
        self.closed.emit()

    def closeEvent(self, event):
        if not self._closed_emitted:
            self._closed_emitted = True
            self.closed.emit()

        event.accept()


# --------------------------------------------------
# BACKWARD-COMPATIBLE CLASS NAMES
# --------------------------------------------------

TransactionProcessingOverlay = TransactionProcessingScreen
CashCollectionOverlay = CashCollectionScreen
