
import sys
from io import BytesIO

import qrcode

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QStackedWidget,
    QFrame,
    QGraphicsDropShadowEffect,
)


# ============================================================
# COLORS
# ============================================================

BG_COLOR = "#020B1A"
CYAN = "#43C8FF"
WHITE = "#F4F8FF"
MUTED = "#B2D1ED"
GREEN = "#43E6A4"


# ============================================================
# UPI PAYMENT POPUP
# QR PAGE -> SUCCESS PAGE -> AUTOMATIC CLOSE
# ============================================================

class UPIPaymentPopup(QDialog):

    def __init__(self, parent=None, timeout=6, language="en"):
        super().__init__(parent)

        self.remaining_seconds = timeout
        self.total_seconds = timeout
        self.language = language
        self.completion_timer = None

        self.setWindowTitle("STARK INDUSTRIES - UPI PAYMENT")
        self.setFixedSize(440, 620)
        self.setModal(True)

        self.setStyleSheet("""
            QDialog {
                background-color: #020B1A;
                color: #F4F8FF;
            }

            QLabel {
                background: transparent;
                color: #F4F8FF;
                font-family: 'Segoe UI';
            }

            QProgressBar {
                background-color: #0A1B2D;
                border: 1px solid #24445E;
                border-radius: 5px;
                height: 9px;
                text-align: center;
            }

            QProgressBar::chunk {
                background-color: #43C8FF;
                border-radius: 4px;
            }
        """)

        # ----------------------------------------------------
        # TRANSLATIONS
        # ----------------------------------------------------

        self.texts = {
            "en": {
                "brand": "STARK  /  SECURE TRANSACTION",
                "title": "UPI PAYMENT",
                "subtitle": "Scan to continue",
                "instruction": "Scan the QR code using your UPI app.",
                "warning": "SECURE UPI TRANSACTION",
                "waiting": "AWAITING PAYMENT SESSION",
                "countdown": "Session ending in {seconds}s",

                "success_title": "TRANSACTION COMPLETE",
                "success_subtitle": (
                    "Thank you for using Stark Industries ATM"
                ),
                "success_message": (
                    "Your transaction session has ended."
                ),
                "success_status": "SESSION COMPLETE",
            },

            "hi": {
                "brand": "STARK  /  सुरक्षित लेनदेन",
                "title": "UPI भुगतान",
                "subtitle": "आगे बढ़ने के लिए स्कैन करें",
                "instruction": "अपने UPI ऐप से QR कोड स्कैन करें।",
                "warning": "सुरक्षित UPI लेनदेन",
                "waiting": "भुगतान सत्र की प्रतीक्षा",
                "countdown": "{seconds} सेकंड शेष",

                "success_title": "सत्र पूरा हुआ",
                "success_subtitle": (
                    "Stark Industries ATM का उपयोग करने के लिए धन्यवाद"
                ),
                "success_message": "आपका सत्र समाप्त हो गया है।",
                "success_status": "सत्र पूरा हुआ",
            },

            "bn": {
                "brand": "STARK  /  নিরাপদ লেনদেন",
                "title": "UPI পেমেন্ট",
                "subtitle": "এগিয়ে যেতে স্ক্যান করুন",
                "instruction": "আপনার UPI অ্যাপ দিয়ে QR কোডটি স্ক্যান করুন।",
                "warning": "নিরাপদ UPI লেনদেন",
                "waiting": "পেমেন্ট সেশনের অপেক্ষায়",
                "countdown": "{seconds} সেকেন্ড বাকি",

                "success_title": "সেশন সম্পূর্ণ",
                "success_subtitle": (
                    "Stark Industries ATM ব্যবহার করার জন্য ধন্যবাদ"
                ),
                "success_message": "আপনার সেশন শেষ হয়েছে।",
                "success_status": "সেশন সম্পূর্ণ",
            },
        }

        self.t = self.texts.get(language, self.texts["en"])

        self.build_ui()

        # Countdown for the QR page.
        self.countdown_timer = QTimer(self)
        self.countdown_timer.setInterval(1000)
        self.countdown_timer.timeout.connect(self.update_countdown)
        self.countdown_timer.start()

    # ========================================================
    # MAIN STACK
    # ========================================================

    def build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 24, 25, 22)
        main_layout.setSpacing(12)

        self.stack = QStackedWidget()
        main_layout.addWidget(self.stack)

        self.build_qr_page()
        self.build_success_page()

        # Start directly on the QR page.
        self.stack.setCurrentWidget(self.qr_page)

    # ========================================================
    # QR PAYMENT PAGE
    # ========================================================

    def build_qr_page(self):
        self.qr_page = QFrame()

        layout = QVBoxLayout(self.qr_page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        brand = QLabel(self.t["brand"])
        brand.setAlignment(Qt.AlignmentFlag.AlignCenter)
        brand.setStyleSheet("""
            color: #67DDFF;
            font-size: 10px;
            font-weight: 700;
            letter-spacing: 2px;
        """)
        layout.addWidget(brand)

        title = QLabel(self.t["title"])
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            color: #FFFFFF;
            font-size: 25px;
            font-weight: 700;
            letter-spacing: 1px;
        """)
        layout.addWidget(title)

        subtitle = QLabel(self.t["subtitle"])
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("""
            color: #9DDCFF;
            font-size: 14px;
        """)
        layout.addWidget(subtitle)

        self.qr_label = QLabel()
        self.qr_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.qr_label.setFixedSize(220, 220)
        self.qr_label.setStyleSheet("""
            QLabel {
                background-color: #FFFFFF;
                border: 3px solid #43C8FF;
                border-radius: 12px;
                padding: 8px;
            }
        """)

        self.generate_qr()

        qr_row = QHBoxLayout()
        qr_row.addStretch()
        qr_row.addWidget(self.qr_label)
        qr_row.addStretch()
        layout.addLayout(qr_row)

        instruction = QLabel(self.t["instruction"])
        instruction.setAlignment(Qt.AlignmentFlag.AlignCenter)
        instruction.setWordWrap(True)
        instruction.setStyleSheet("""
            color: #D4E8F8;
            font-size: 12px;
        """)
        layout.addWidget(instruction)

        warning = QLabel(self.t["warning"])
        warning.setAlignment(Qt.AlignmentFlag.AlignCenter)
        warning.setWordWrap(True)
        warning.setStyleSheet("""
            color: #67DDFF;
            font-size: 10px;
            font-weight: 700;
            letter-spacing: 1px;
            padding: 5px;
        """)
        layout.addWidget(warning)

        separator = QFrame()
        separator.setFixedHeight(1)
        separator.setStyleSheet(
            "background-color: #24445E;"
        )
        layout.addWidget(separator)

        self.status_label = QLabel(self.t["waiting"])
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setWordWrap(True)
        self.status_label.setStyleSheet("""
            color: #67DDFF;
            font-size: 11px;
            font-weight: 600;
            letter-spacing: 1px;
        """)
        layout.addWidget(self.status_label)

        self.countdown_label = QLabel()
        self.countdown_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.countdown_label.setStyleSheet("""
            color: #FFFFFF;
            font-size: 14px;
            font-weight: 600;
        """)
        layout.addWidget(self.countdown_label)

        self.progress = QProgressBar()
        self.progress.setRange(0, self.total_seconds)
        self.progress.setValue(self.total_seconds)
        self.progress.setTextVisible(False)
        layout.addWidget(self.progress)

        self.update_countdown_label()

        self.stack.addWidget(self.qr_page)

    # ========================================================
    # QR CODE GENERATION
    # ========================================================

    def generate_qr(self):
        # Placeholder QR payload; this is not a real UPI payment QR.
        qr_payload = "STARK ATM PAYMENT SESSION"

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=8,
            border=3,
        )

        qr.add_data(qr_payload)
        qr.make(fit=True)

        image = qr.make_image(
            fill_color="black",
            back_color="white",
        )

        buffer = BytesIO()
        image.save(buffer, format="PNG")

        pixmap = QPixmap()
        pixmap.loadFromData(buffer.getvalue(), "PNG")

        self.qr_label.setPixmap(
            pixmap.scaled(
                200,
                200,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )

    # ========================================================
    # COUNTDOWN
    # ========================================================

    def update_countdown_label(self):
        self.countdown_label.setText(
            self.t["countdown"].format(
                seconds=self.remaining_seconds
            )
        )

    def update_countdown(self):
        self.remaining_seconds -= 1

        self.progress.setValue(
            max(0, self.remaining_seconds)
        )
        self.update_countdown_label()

        if self.remaining_seconds <= 0:
            self.countdown_timer.stop()
            self.show_success_page()

    # ========================================================
    # SUCCESS PAGE
    # ========================================================

    def build_success_page(self):
        self.success_page = QFrame()

        layout = QVBoxLayout(self.success_page)
        layout.setContentsMargins(5, 35, 5, 25)
        layout.setSpacing(18)

        brand = QLabel("STARK  /  EDITH SYSTEM")
        brand.setAlignment(Qt.AlignmentFlag.AlignCenter)
        brand.setStyleSheet("""
            color: #67DDFF;
            font-size: 10px;
            font-weight: 700;
            letter-spacing: 2px;
        """)
        layout.addWidget(brand)

        check = QLabel("✓")
        check.setAlignment(Qt.AlignmentFlag.AlignCenter)
        check.setStyleSheet("""
            color: #43E6A4;
            font-family: 'Segoe UI';
            font-size: 76px;
            font-weight: 400;
        """)

        glow = QGraphicsDropShadowEffect(check)
        glow.setBlurRadius(25)
        glow.setOffset(0, 0)
        glow.setColor(QColor(40, 255, 160, 130))
        check.setGraphicsEffect(glow)

        layout.addWidget(check)

        title = QLabel(self.t["success_title"])
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setWordWrap(True)
        title.setStyleSheet("""
            color: #43E6A4;
            font-size: 25px;
            font-weight: 700;
            letter-spacing: 1px;
        """)
        layout.addWidget(title)

        subtitle = QLabel(self.t["success_subtitle"])
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet("""
            color: #D8E8F7;
            font-size: 14px;
        """)
        layout.addWidget(subtitle)

        message = QLabel(self.t["success_message"])
        message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message.setWordWrap(True)
        message.setStyleSheet("""
            color: #AFCBE0;
            font-size: 12px;
            padding: 5px;
        """)
        layout.addWidget(message)

        status = QLabel(self.t["success_status"])
        status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status.setWordWrap(True)
        status.setStyleSheet("""
            color: #43E6A4;
            font-size: 10px;
            font-weight: 700;
            letter-spacing: 2px;
            padding: 8px;
            border: 1px solid #216D59;
            border-radius: 7px;
            background-color: #08251F;
        """)
        layout.addWidget(status)

        layout.addStretch()

        self.stack.addWidget(self.success_page)

    # ========================================================
    # SHOW SUCCESS AND CLOSE AUTOMATICALLY
    # ========================================================

    def show_success_page(self):
        self.stack.setCurrentWidget(self.success_page)

        # Automatically close two seconds after the success page.
        self.completion_timer = QTimer(self)
        self.completion_timer.setSingleShot(True)
        self.completion_timer.timeout.connect(self.accept)
        self.completion_timer.start(2000)

    # ========================================================
    # CLEANUP
    # ========================================================

    def stop_timers(self):
        if hasattr(self, "countdown_timer"):
            self.countdown_timer.stop()

        if self.completion_timer is not None:
            self.completion_timer.stop()

    def reject(self):
        self.stop_timers()
        super().reject()

    def closeEvent(self, event):
        self.stop_timers()
        super().closeEvent(event)


# ============================================================
# STANDALONE TEST
# ============================================================

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    popup = UPIPaymentPopup(timeout=6, language="en")
    popup.exec()

    sys.exit(0)
