import sys
from pathlib import Path
from datetime import datetime

from PySide6.QtCore import Qt, QTimer, QRectF, QPointF, Signal
from PySide6.QtGui import QColor, QFont, QPainter, QPen, QPixmap
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QGraphicsDropShadowEffect, QSizePolicy, QMenu, QGridLayout,
    QPushButton, QMessageBox, QLineEdit
)

from sos_popup import SOSPopup
from upi_popup import UPIPaymentPopup
from card_entry_popup import CardEntryPopup

BASE_DIR = Path(__file__).resolve().parent
BG_COLOR = "#020B1A"
CYAN = "#43C8FF"
WHITE = "#F4F8FF"
MUTED = "#B2D1ED"


class BackgroundWidget(QWidget):
    def __init__(self, image_path):
        super().__init__()
        self.background = QPixmap(str(image_path))
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        painter.fillRect(self.rect(), QColor(BG_COLOR))
        if not self.background.isNull():
            painter.drawPixmap(self.rect(), self.background)
        painter.fillRect(self.rect(), QColor(2, 11, 26, 55))
        painter.end()


class CircularProgress(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.angle = 0
        self.setFixedSize(120, 120)
        self.timer = QTimer(self)
        self.timer.setInterval(16)
        self.timer.timeout.connect(self.rotate)

    def start(self):
        self.angle = 0
        self.timer.start()
        self.update()

    def stop(self):
        self.timer.stop()

    def rotate(self):
        self.angle = (self.angle - 6) % 360
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        center = self.rect().center()
        circle = QRectF(center.x() - 45, center.y() - 45, 90, 90)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(QColor("#123047"), 5))
        painter.drawEllipse(circle)
        painter.setPen(QPen(QColor(CYAN), 5, Qt.PenStyle.SolidLine,
                            Qt.PenCapStyle.RoundCap))
        painter.drawArc(circle, self.angle * 16, 105 * 16)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(67, 200, 255, 35))
        painter.drawEllipse(QRectF(center.x() - 23, center.y() - 23, 46, 46))
        painter.setBrush(QColor(CYAN))
        painter.drawEllipse(QRectF(center.x() - 3, center.y() - 3, 6, 6))
        painter.end()


class TransactionProcessingOverlay(QWidget):
    finished = Signal()

    def __init__(self, parent=None, language="en", duration=4000):
        super().__init__(parent)
        self.duration = duration
        self.has_finished = False
        translations = {
            "en": ("STARK  /  EDITH SYSTEM", "TRANSACTION", "PROCESSING",
                   "Please wait while we process your request.",
                   "SECURE PROCESSING IN PROGRESS"),
            "hi": ("STARK  /  EDITH SYSTEM", "लेनदेन की", "प्रक्रिया जारी है",
                   "कृपया प्रतीक्षा करें।", "सुरक्षित प्रक्रिया जारी है"),
            "bn": ("STARK  /  EDITH SYSTEM", "লেনদেন", "প্রক্রিয়াকরণ চলছে",
                   "অনুগ্রহ করে অপেক্ষা করুন।", "নিরাপদ প্রক্রিয়াকরণ চলছে"),
        }
        brand_text, title_text, title2_text, subtitle_text, status_text = translations.get(language, translations["en"])
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet("background-color: #020B1A;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(0)
        layout.addStretch()
        brand = QLabel(brand_text)
        brand.setAlignment(Qt.AlignmentFlag.AlignCenter)
        brand.setStyleSheet("color:#67DDFF;background:transparent;font-size:12px;font-weight:700;letter-spacing:3px;")
        layout.addWidget(brand)
        layout.addSpacing(48)
        self.spinner = CircularProgress(self)
        glow = QGraphicsDropShadowEffect(self.spinner)
        glow.setBlurRadius(28)
        glow.setOffset(0, 0)
        glow.setColor(QColor(0, 170, 255, 120))
        self.spinner.setGraphicsEffect(glow)
        spinner_row = QHBoxLayout()
        spinner_row.addStretch()
        spinner_row.addWidget(self.spinner)
        spinner_row.addStretch()
        layout.addLayout(spinner_row)
        layout.addSpacing(30)
        title = QLabel(title_text)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color:#DCEBFA;background:transparent;font-size:23px;letter-spacing:3px;")
        layout.addWidget(title)
        title2 = QLabel(title2_text)
        title2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title2.setStyleSheet("color:white;background:transparent;font-size:32px;font-weight:700;letter-spacing:2px;")
        layout.addWidget(title2)
        layout.addSpacing(16)
        subtitle = QLabel(subtitle_text)
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet("color:#B2D1ED;background:transparent;font-size:14px;")
        layout.addWidget(subtitle)
        layout.addSpacing(30)
        separator = QFrame()
        separator.setFixedHeight(1)
        separator.setMaximumWidth(420)
        separator.setStyleSheet("background-color:#24445E;")
        separator_row = QHBoxLayout()
        separator_row.addStretch()
        separator_row.addWidget(separator)
        separator_row.addStretch()
        layout.addLayout(separator_row)
        layout.addSpacing(18)
        status = QLabel(status_text)
        status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status.setWordWrap(True)
        status.setStyleSheet("color:#67DDFF;background:transparent;font-size:11px;font-weight:600;letter-spacing:2px;")
        layout.addWidget(status)
        layout.addStretch()
        self.close_timer = QTimer(self)
        self.close_timer.setSingleShot(True)
        self.close_timer.timeout.connect(self.finish)

    def showEvent(self, event):
        super().showEvent(event)
        if self.parentWidget():
            self.setGeometry(self.parentWidget().rect())
        self.raise_()
        self.has_finished = False
        self.spinner.start()
        self.close_timer.start(self.duration)

    def finish(self):
        if self.has_finished:
            return
        self.has_finished = True
        self.close_timer.stop()
        self.spinner.stop()
        self.hide()
        self.finished.emit()
        self.deleteLater()

    def stop(self):
        if self.has_finished:
            return
        self.has_finished = True
        self.close_timer.stop()
        self.spinner.stop()
        self.hide()


class CashCollectionOverlay(QWidget):
    closed = Signal()

    def __init__(self, parent=None, language="en"):
        super().__init__(parent)
        self.has_closed = False
        translations = {
            "en": ("STARK  /  EDITH SYSTEM", "TRANSACTION COMPLETE", "PLEASE COLLECT YOUR CASH", "Your cash is ready.", "Please take your cash from the ATM dispenser before leaving.", "CASH DISPENSING COMPLETE", "CLOSE"),
            "hi": ("STARK  /  EDITH SYSTEM", "लेनदेन पूरा हुआ", "कृपया अपनी नकदी लें", "आपकी नकदी तैयार है।", "जाने से पहले कृपया ATM मशीन से अपनी नकदी निकाल लें।", "नकदी निकालने की प्रक्रिया पूरी हुई", "बंद करें"),
            "bn": ("STARK  /  EDITH SYSTEM", "লেনদেন সম্পন্ন", "অনুগ্রহ করে টাকা সংগ্রহ করুন", "আপনার টাকা প্রস্তুত।", "চলে যাওয়ার আগে ATM মেশিন থেকে আপনার টাকা সংগ্রহ করুন।", "টাকা বিতরণ সম্পন্ন", "বন্ধ করুন"),
        }
        brand_t, title_t, heading_t, subtitle_t, instruction_t, status_t, button_t = translations.get(language, translations["en"])
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet("background-color:#020B1A;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(0)
        layout.addStretch()
        brand = QLabel(brand_t)
        brand.setAlignment(Qt.AlignmentFlag.AlignCenter)
        brand.setStyleSheet("color:#67DDFF;background:transparent;font-size:12px;font-weight:700;letter-spacing:3px;")
        layout.addWidget(brand)
        layout.addSpacing(35)
        self.success_icon = QLabel("✓")
        self.success_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.success_icon.setFixedSize(100, 100)
        self.success_icon.setStyleSheet("color:#67FFB4;background:#092C32;border:2px solid #32E6A0;border-radius:50px;font-size:55px;")
        icon_row = QHBoxLayout()
        icon_row.addStretch()
        icon_row.addWidget(self.success_icon)
        icon_row.addStretch()
        layout.addLayout(icon_row)
        layout.addSpacing(30)
        title = QLabel(title_t)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color:#67DDFF;background:transparent;font-size:13px;font-weight:700;letter-spacing:3px;")
        layout.addWidget(title)
        layout.addSpacing(12)
        heading = QLabel(heading_t)
        heading.setAlignment(Qt.AlignmentFlag.AlignCenter)
        heading.setWordWrap(True)
        heading.setStyleSheet("color:white;background:transparent;font-size:27px;font-weight:700;letter-spacing:1px;")
        layout.addWidget(heading)
        layout.addSpacing(14)
        subtitle = QLabel(subtitle_t)
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color:#67FFB4;background:transparent;font-size:17px;font-weight:600;")
        layout.addWidget(subtitle)
        layout.addSpacing(12)
        instruction = QLabel(instruction_t)
        instruction.setAlignment(Qt.AlignmentFlag.AlignCenter)
        instruction.setWordWrap(True)
        instruction.setMaximumWidth(600)
        instruction.setStyleSheet("color:#B2D1ED;background:transparent;font-size:14px;")
        instruction_row = QHBoxLayout()
        instruction_row.addStretch()
        instruction_row.addWidget(instruction)
        instruction_row.addStretch()
        layout.addLayout(instruction_row)
        layout.addSpacing(25)
        separator = QFrame()
        separator.setFixedHeight(1)
        separator.setMaximumWidth(420)
        separator.setStyleSheet("background:#24445E;")
        sep_row = QHBoxLayout()
        sep_row.addStretch()
        sep_row.addWidget(separator)
        sep_row.addStretch()
        layout.addLayout(sep_row)
        layout.addSpacing(18)
        status = QLabel(status_t)
        status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status.setWordWrap(True)
        status.setStyleSheet("color:#67DDFF;background:transparent;font-size:11px;font-weight:600;letter-spacing:2px;")
        layout.addWidget(status)
        layout.addSpacing(30)
        self.close_button = QPushButton(button_t)
        self.close_button.setFixedSize(180, 48)
        self.close_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.close_button.setStyleSheet("QPushButton{color:#020B1A;background:#43C8FF;border:1px solid #67DDFF;border-radius:8px;font-size:13px;font-weight:700;letter-spacing:2px;} QPushButton:hover{background:#8BE0FF;}")
        self.close_button.clicked.connect(self.close_screen)
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_row.addWidget(self.close_button)
        btn_row.addStretch()
        layout.addLayout(btn_row)
        layout.addStretch()

    def showEvent(self, event):
        super().showEvent(event)
        if self.parentWidget():
            self.setGeometry(self.parentWidget().rect())
        self.raise_()

    def close_screen(self):
        if self.has_closed:
            return
        self.has_closed = True
        self.closed.emit()
        self.hide()
        self.deleteLater()


class LineIcon(QWidget):
    def __init__(self, icon_type, parent=None):
        super().__init__(parent)
        self.icon_type = icon_type
        self.icon_color = QColor(CYAN)
        self.setFixedSize(58, 54)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(QPen(self.icon_color, 2.2, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        if self.icon_type == "card":
            painter.drawRoundedRect(QRectF(3, 7, 52, 39), 5, 5)
            painter.drawLine(4, 18, 54, 18)
            painter.drawLine(10, 29, 23, 29)
            painter.drawLine(10, 36, 20, 36)
        elif self.icon_type == "upi":
            painter.drawRoundedRect(QRectF(5, 5, 48, 44), 8, 8)
            painter.drawEllipse(QRectF(13, 10, 32, 32))
            painter.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
            painter.drawText(QRectF(13, 10, 32, 32), Qt.AlignmentFlag.AlignCenter, "₹")
        elif self.icon_type == "sos":
            painter.drawRoundedRect(QRectF(4, 5, 50, 44), 8, 8)
            painter.setFont(QFont("Segoe UI", 15, QFont.Weight.Bold))
            painter.drawText(QRectF(5, 5, 48, 44), Qt.AlignmentFlag.AlignCenter, "SOS")
        elif self.icon_type == "globe":
            painter.drawEllipse(QRectF(7, 4, 44, 44))
            painter.drawLine(29, 5, 29, 47)
            painter.drawLine(8, 26, 50, 26)
            painter.drawEllipse(QRectF(18, 4, 22, 44))
            painter.drawEllipse(QRectF(8, 14, 42, 24))
        painter.end()


class GlassOption(QFrame):
    clicked = Signal()

    def __init__(self, icon_type, title, subtitle, parent=None):
        super().__init__(parent)
        self.hovered = False
        self.setMinimumHeight(158)
        self.setMinimumWidth(0)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setMouseTracking(True)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 14, 8, 12)
        layout.setSpacing(5)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon = LineIcon(icon_type, self)
        layout.addWidget(self.icon, 0, Qt.AlignmentFlag.AlignHCenter)
        self.title_label = QLabel(title)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setWordWrap(True)
        self.title_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.title_label.setStyleSheet("color:#F4F8FF;background:transparent;font-size:15px;font-weight:500;")
        layout.addWidget(self.title_label)
        self.subtitle_label = QLabel(subtitle)
        self.subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.subtitle_label.setWordWrap(True)
        self.subtitle_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.subtitle_label.setStyleSheet("color:#B2D1ED;background:transparent;font-size:11px;")
        layout.addWidget(self.subtitle_label)
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(14)
        self.shadow.setOffset(0, 3)
        self.shadow.setColor(QColor(0, 110, 220, 35))
        self.setGraphicsEffect(self.shadow)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(self.rect()).adjusted(1.5, 1.5, -1.5, -1.5)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(0, 5, 15, 95))
        painter.drawRoundedRect(rect.translated(1, 3), 11, 11)
        if self.hovered:
            fill, border, width = QColor(5, 39, 69, 175), QColor(0, 225, 255, 235), 1.8
        else:
            fill, border, width = QColor(3, 19, 37, 112), QColor(45, 133, 195, 195), 1.25
        painter.setBrush(fill)
        painter.setPen(QPen(border, width))
        painter.drawRoundedRect(rect, 11, 11)
        painter.setPen(QPen(QColor(80, 185, 255, 100 if self.hovered else 45), 1))
        painter.drawLine(QPointF(rect.left() + 11, rect.top() + 1), QPointF(rect.right() - 11, rect.top() + 1))
        painter.end()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.rect().contains(event.position().toPoint()):
            self.clicked.emit()
        super().mouseReleaseEvent(event)

    def enterEvent(self, event):
        self.hovered = True
        self.shadow.setBlurRadius(23)
        self.shadow.setOffset(0, 2)
        self.shadow.setColor(QColor(0, 170, 255, 90))
        self.icon.icon_color = QColor("#67DDFF")
        self.icon.update()
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.hovered = False
        self.shadow.setBlurRadius(14)
        self.shadow.setOffset(0, 3)
        self.shadow.setColor(QColor(0, 110, 220, 35))
        self.icon.icon_color = QColor(CYAN)
        self.icon.update()
        self.update()
        super().leaveEvent(event)


class StarkATM(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("STARK INDUSTRIES ATM")
        self.resize(1280, 720)
        self.setMinimumSize(1000, 600)
        self.processing_overlay = None
        self.cash_overlay = None
        self.transaction_active = False
        self.inserted_card = None
        self.processing_success_message = None
        self.demo_balance = 25000.0
        self.demo_transactions = [
            ("20-10-2026", "Cash withdrawal", -2000),
            ("19-10-2026", "UPI payment", -450),
            ("18-10-2026", "Deposit", 5000),
        ]
        self.demo_pin = "1234"
        self.pin_mode = None
        self.pin_attempts = 0
        self.pin_payload = None
        self.pending_new_pin = ""
        self.setup_translations()
        self.background_widget = BackgroundWidget(BASE_DIR / "stark_background.png")
        if self.background_widget.background.isNull():
            print("Warning: stark_background.png not found; using fallback background.")
        self.root_layout = QVBoxLayout(self)
        self.root_layout.setContentsMargins(0, 0, 0, 0)
        self.root_layout.setSpacing(0)
        self.root_layout.addWidget(self.background_widget)
        self.content = QWidget(self.background_widget)
        self.content.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.content_layout = QVBoxLayout(self.content)
        self.content_layout.setContentsMargins(34, 22, 34, 25)
        self.content_layout.setSpacing(0)
        self.build_header()
        self.build_welcome()
        self.build_options()
        self.build_transaction_screen()
        self.clock_timer = QTimer(self)
        self.clock_timer.timeout.connect(self.update_clock)
        self.clock_timer.start(1000)
        self.update_clock()

    def setup_translations(self):
        self.current_language = "en"
        self.translations = {
            "en": {"welcome": "Welcome to", "title": "Stark Industries ATM", "tagline": "Your Trust. Our Technology.", "instruction": "SELECT AN OPTION TO CONTINUE", "insert_card": "Insert Card", "begin": "to begin", "upi": "UPI Payment", "withdraw": "Withdraw with UPI", "sos": "SOS", "emergency": "Emergency Assistance", "language": "Language", "language_name": "English", "select_language": "Select Language"},
            "hi": {"welcome": "आपका स्वागत है", "title": "स्टार्क इंडस्ट्रीज़ ATM", "tagline": "आपका विश्वास। हमारी तकनीक।", "instruction": "जारी रखने के लिए एक विकल्प चुनें", "insert_card": "कार्ड डालें", "begin": "शुरू करने के लिए", "upi": "UPI भुगतान", "withdraw": "UPI से पैसे निकालें", "sos": "SOS", "emergency": "आपातकालीन सहायता", "language": "भाषा", "language_name": "हिंदी", "select_language": "भाषा चुनें"},
            "bn": {"welcome": "স্বাগতম", "title": "স্টার্ক ইন্ডাস্ট্রিজ ATM", "tagline": "আপনার বিশ্বাস। আমাদের প্রযুক্তি।", "instruction": "চালিয়ে যেতে একটি বিকল্প বেছে নিন", "insert_card": "কার্ড ঢোকান", "begin": "শুরু করতে", "upi": "UPI পেমেন্ট", "withdraw": "UPI দিয়ে টাকা তুলুন", "sos": "SOS", "emergency": "জরুরি সহায়তা", "language": "ভাষা", "language_name": "বাংলা", "select_language": "ভাষা নির্বাচন করুন"},
        }

    def show_language_menu(self):
        t = self.translations[self.current_language]
        menu = QMenu(self)
        menu.setStyleSheet("QMenu{background:#07182B;color:#F4F8FF;border:1px solid #43C8FF;border-radius:8px;padding:6px;font-size:13px;} QMenu::item{padding:10px 28px 10px 14px;border-radius:5px;} QMenu::item:selected{background:#103653;color:#67DDFF;}")
        menu.addSection(t["select_language"])
        for code, label in [("en", "English"), ("hi", "हिंदी"), ("bn", "বাংলা")]:
            action = menu.addAction(label)
            action.setCheckable(True)
            action.setChecked(code == self.current_language)
            action.triggered.connect(lambda checked=False, lang=code: self.change_language(lang))
        pos = self.language_option.mapToGlobal(QPointF(self.language_option.width() / 2, self.language_option.height()).toPoint())
        menu.exec(pos)

    def change_language(self, language_code):
        if language_code not in self.translations:
            return
        self.current_language = language_code
        t = self.translations[language_code]
        self.welcome_intro.setText(t["welcome"])
        self.welcome_label.setText(t["title"])
        self.tagline_label.setText(t["tagline"])
        self.instruction_label.setText(t["instruction"])
        self.insert_card_option.title_label.setText(t["insert_card"])
        self.insert_card_option.subtitle_label.setText(t["begin"])
        self.upi_payment_option.title_label.setText(t["upi"])
        self.upi_payment_option.subtitle_label.setText(t["withdraw"])
        self.sos_option.title_label.setText(t["sos"])
        self.sos_option.subtitle_label.setText(t["emergency"])
        self.language_option.title_label.setText(t["language"])
        self.language_option.subtitle_label.setText(t["language_name"])
        for option in self.option_widgets:
            option.updateGeometry()
            option.update()
        self.update_clock()
        self.content.update()

    def build_header(self):
        header = QHBoxLayout()
        header.setSpacing(15)
        self.logo_label = QLabel()
        self.logo_label.setStyleSheet("background:transparent;")
        self.original_logo = QPixmap(str(BASE_DIR / "logo.png"))
        if not self.original_logo.isNull():
            self.update_logo_size()
        else:
            self.logo_label.setText("STARK INDUSTRIES")
            self.logo_label.setStyleSheet("color:#67CFFF;background:transparent;font-size:18px;font-weight:bold;letter-spacing:2px;")
        header.addWidget(self.logo_label, 0, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        header.addStretch()
        self.clock_label = QLabel()
        self.clock_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.clock_label.setStyleSheet("color:#A9DFFF;background:transparent;font-size:12px;letter-spacing:1px;")
        header.addWidget(self.clock_label)
        self.content_layout.addLayout(header)

    def update_logo_size(self):
        if self.original_logo.isNull():
            return
        pixmap = self.original_logo.scaled(max(200, int(self.width() * .32)), max(30, int(self.height() * .065)), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.logo_label.setPixmap(pixmap)

    def build_welcome(self):
        self.content_layout.addSpacing(80)
        self.welcome_intro = QLabel("Welcome to")
        self.welcome_intro.setStyleSheet("color:#DCEBFA;background:transparent;font-size:20px;")
        self.content_layout.addWidget(self.welcome_intro, 0, Qt.AlignmentFlag.AlignLeft)
        self.content_layout.addSpacing(3)
        self.welcome_label = QLabel("Stark Industries ATM")
        self.welcome_label.setWordWrap(True)
        self.welcome_label.setStyleSheet("color:white;background:transparent;font-weight:700;")
        self.welcome_glow = QGraphicsDropShadowEffect(self.welcome_label)
        self.welcome_glow.setBlurRadius(18)
        self.welcome_glow.setOffset(0, 0)
        self.welcome_glow.setColor(QColor(0, 190, 255, 120))
        self.welcome_label.setGraphicsEffect(self.welcome_glow)
        self.content_layout.addWidget(self.welcome_label, 0, Qt.AlignmentFlag.AlignLeft)
        self.content_layout.addSpacing(8)
        self.tagline_label = QLabel("Your Trust. Our Technology.")
        self.tagline_label.setStyleSheet("color:#83CFFF;background:transparent;font-weight:500;")
        self.content_layout.addWidget(self.tagline_label, 0, Qt.AlignmentFlag.AlignLeft)
        self.content_layout.addStretch(1)
        self.instruction_label = QLabel("SELECT AN OPTION TO CONTINUE")
        self.instruction_label.setStyleSheet("color:#8BB8DF;background:transparent;font-size:10px;font-weight:600;letter-spacing:2px;")
        self.content_layout.addWidget(self.instruction_label)
        self.content_layout.addSpacing(13)

    def build_options(self):
        options = QHBoxLayout()
        options.setSpacing(20)
        self.insert_card_option = GlassOption("card", "Insert Card", "to begin")
        self.upi_payment_option = GlassOption("upi", "UPI Payment", "Withdraw with UPI")
        self.sos_option = GlassOption("sos", "SOS", "Emergency Assistance")
        self.language_option = GlassOption("globe", "Language", "English")
        self.insert_card_option.clicked.connect(self.show_insert_card_message)
        self.upi_payment_option.clicked.connect(self.show_upi_popup)
        self.sos_option.clicked.connect(self.show_sos_popup)
        self.language_option.clicked.connect(self.show_language_menu)
        self.option_widgets = [self.insert_card_option, self.upi_payment_option, self.sos_option, self.language_option]
        for option in self.option_widgets:
            options.addWidget(option, 1)
        self.content_layout.addLayout(options)

    def build_inserted_card_info(self):
        self.card_info_panel = QFrame()
        self.card_info_panel.setObjectName("cardInfoPanel")
        self.card_info_panel.setStyleSheet("QFrame#cardInfoPanel{background:rgba(4,25,43,220);border:1px solid #43C8FF;border-radius:10px;}")
        self.card_info_panel.setMaximumWidth(460)
        layout = QVBoxLayout(self.card_info_panel)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(6)
        self.card_status_label = QLabel("✓  CARD INSERTED SUCCESSFULLY")
        self.card_status_label.setStyleSheet("color:#67FFB4;background:transparent;border:none;font-size:11px;font-weight:bold;letter-spacing:1px;")
        self.card_holder_label = QLabel("Cardholder: --")
        self.card_holder_label.setStyleSheet("color:white;background:transparent;border:none;font-size:15px;font-weight:bold;")
        self.card_number_label = QLabel("Card Number: --")
        self.card_number_label.setStyleSheet("color:#83CFFF;background:transparent;border:none;font-size:13px;letter-spacing:1px;")
        layout.addWidget(self.card_status_label)
        layout.addWidget(self.card_holder_label)
        layout.addWidget(self.card_number_label)
        self.card_info_panel.hide()
        self.content_layout.addWidget(self.card_info_panel, 0, Qt.AlignmentFlag.AlignLeft)

    def build_transaction_screen(self):
        self.transaction_screen = QWidget(self.background_widget)
        self.transaction_screen.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        root = QVBoxLayout(self.transaction_screen)
        root.setContentsMargins(42, 25, 42, 28)
        root.setSpacing(0)
        header = QHBoxLayout()
        self.transaction_logo = QLabel()
        self.transaction_logo.setStyleSheet("background:transparent;border:none;")
        if not self.original_logo.isNull():
            self.transaction_logo.setPixmap(self.original_logo.scaled(390, 75, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            self.transaction_logo.setText("STARK INDUSTRIES")
            self.transaction_logo.setStyleSheet("color:white;background:transparent;font-size:28px;font-weight:bold;font-style:italic;")
        header.addWidget(self.transaction_logo, 0, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        header.addStretch()
        self.transaction_clock = QLabel()
        self.transaction_clock.setStyleSheet("color:#43C8FF;background:transparent;font-size:15px;font-weight:600;")
        header.addWidget(self.transaction_clock, 0, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        root.addLayout(header)
        root.addSpacing(60)
        main = QHBoxLayout()
        main.setSpacing(35)
        left = QVBoxLayout()
        left.setSpacing(10)
        welcome_row = QHBoxLayout()
        welcome_row.setSpacing(22)
        card_icon = QLabel("▤")
        card_icon.setFixedSize(92, 78)
        card_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_icon.setStyleSheet("color:#00CFFF;background:transparent;border:4px solid #00CFFF;border-radius:10px;font-size:48px;font-weight:bold;")
        welcome_row.addWidget(card_icon, 0, Qt.AlignmentFlag.AlignTop)
        welcome_text = QVBoxLayout()
        welcome_text.setSpacing(5)
        inserted = QLabel("Card Inserted")
        inserted.setStyleSheet("color:#00D5FF;background:transparent;font-size:18px;font-weight:bold;")
        self.transaction_welcome = QLabel("Welcome")
        self.transaction_welcome.setWordWrap(True)
        self.transaction_welcome.setStyleSheet("color:#FFFFFF;background:transparent;font-size:34px;font-weight:bold;")
        prompt = QLabel("Please select your transaction.")
        prompt.setWordWrap(True)
        prompt.setStyleSheet("color:#00CFFF;background:transparent;font-size:21px;font-weight:600;")
        welcome_text.addWidget(inserted)
        welcome_text.addWidget(self.transaction_welcome)
        welcome_text.addWidget(prompt)
        welcome_row.addLayout(welcome_text, 1)
        left.addLayout(welcome_row)
        left.addStretch()
        self.cancel_transaction_button = QPushButton("←     Cancel")
        self.cancel_transaction_button.setFixedSize(200, 64)
        self.cancel_transaction_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.cancel_transaction_button.setStyleSheet("QPushButton{color:#F4F8FF;background:rgba(0,19,43,185);border:2px solid #00CFFF;border-radius:10px;font-size:17px;font-weight:600;text-align:left;padding-left:24px;} QPushButton:hover{background:rgba(0,105,160,170);}")
        self.cancel_transaction_button.clicked.connect(self.cancel_transaction_screen)
        left.addWidget(self.cancel_transaction_button, 0, Qt.AlignmentFlag.AlignLeft)
        main.addLayout(left, 11)
        self.options_panel = QWidget()
        self.options_panel.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        right = QVBoxLayout(self.options_panel)
        right.setContentsMargins(0, 0, 0, 0)
        right.setSpacing(12)
        option_specs = [
            ("▣", "Cash Withdraw", self.start_cash_withdrawal),
            ("＋", "Cash Deposit", self.start_cash_deposit),
            ("▤", "Check Balance", self.show_balance),
            ("▧", "Mini Statement", self.show_mini_statement),
            ("♙", "Change Password", self.change_password),
        ]
        self.transaction_buttons = []
        for symbol, text, callback in option_specs:
            button = QPushButton(f"   {symbol}       {text}                         ❯")
            button.setMinimumHeight(78)
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            button.setStyleSheet("QPushButton{color:#F4F8FF;background:rgba(0,20,47,220);border:2px solid #00CFFF;border-radius:10px;font-size:21px;font-weight:600;text-align:left;padding:12px 22px;} QPushButton:hover{background:rgba(0,77,123,225);border:2px solid #73E5FF;} QPushButton:pressed{background:rgba(0,119,174,230);}")
            button.clicked.connect(callback)
            right.addWidget(button)
            self.transaction_buttons.append(button)
        main.addWidget(self.options_panel, 10)

        # Inline PIN keypad: it occupies the same right-side area as the options.
        self.pin_panel = QWidget()
        self.pin_panel.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        pin_layout = QVBoxLayout(self.pin_panel)
        pin_layout.setContentsMargins(8, 0, 8, 0)
        pin_layout.setSpacing(12)

        self.pin_heading = QLabel("SECURE PIN VERIFICATION")
        self.pin_heading.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pin_heading.setStyleSheet("color:#67DDFF;background:transparent;font-size:21px;font-weight:700;letter-spacing:2px;")
        pin_layout.addWidget(self.pin_heading)

        self.pin_subheading = QLabel("Enter your 4-digit PIN to continue")
        self.pin_subheading.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pin_subheading.setWordWrap(True)
        self.pin_subheading.setStyleSheet("color:#B2D1ED;background:transparent;font-size:14px;")
        pin_layout.addWidget(self.pin_subheading)

        self.pin_display = QLineEdit()
        self.pin_display.setEchoMode(QLineEdit.EchoMode.Password)
        self.pin_display.setMaxLength(4)
        self.pin_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pin_display.setPlaceholderText("•   •   •   •")
        self.pin_display.setFixedHeight(54)
        self.pin_display.setStyleSheet("QLineEdit{color:#FFFFFF;background:rgba(0,9,24,220);border:2px solid #00CFFF;border-radius:9px;font-size:25px;letter-spacing:12px;padding:5px;} QLineEdit:focus{border:2px solid #73E5FF;}")
        self.pin_display.returnPressed.connect(self.submit_pin)
        pin_layout.addWidget(self.pin_display)

        self.pin_status = QLabel("SECURE INPUT ENABLED")
        self.pin_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pin_status.setWordWrap(True)
        self.pin_status.setMinimumHeight(22)
        self.pin_status.setStyleSheet("color:#67DDFF;background:transparent;font-size:11px;font-weight:600;letter-spacing:1px;")
        pin_layout.addWidget(self.pin_status)

        keypad = QGridLayout()
        keypad.setSpacing(9)
        keypad_keys = [("1",0,0),("2",0,1),("3",0,2),("4",1,0),("5",1,1),("6",1,2),("7",2,0),("8",2,1),("9",2,2),("CLEAR",3,0),("0",3,1),("⌫",3,2)]
        for key_text, row, col in keypad_keys:
            key = QPushButton(key_text)
            key.setMinimumHeight(48)
            key.setCursor(Qt.CursorShape.PointingHandCursor)
            key.setStyleSheet("QPushButton{color:#F4F8FF;background:rgba(0,26,55,235);border:1px solid #168BC0;border-radius:8px;font-size:18px;font-weight:600;} QPushButton:hover{background:rgba(0,94,145,235);border:1px solid #73E5FF;} QPushButton:pressed{background:#006B9D;}")
            if key_text.isdigit():
                key.clicked.connect(lambda checked=False, digit=key_text: self.add_pin_digit(digit))
            elif key_text == "CLEAR":
                key.clicked.connect(self.clear_pin_input)
                key.setStyleSheet("QPushButton{color:#FFCC85;background:rgba(53,34,10,220);border:1px solid #B8792C;border-radius:8px;font-size:13px;font-weight:700;} QPushButton:hover{background:#65431C;}")
            else:
                key.clicked.connect(self.backspace_pin)
            keypad.addWidget(key, row, col)
        pin_layout.addLayout(keypad)

        pin_actions = QHBoxLayout()
        pin_actions.setSpacing(10)
        self.pin_cancel_button = QPushButton("CANCEL")
        self.pin_cancel_button.setMinimumHeight(48)
        self.pin_cancel_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.pin_cancel_button.setStyleSheet("QPushButton{color:#F4F8FF;background:rgba(34,22,30,220);border:1px solid #A94B68;border-radius:8px;font-size:13px;font-weight:700;} QPushButton:hover{background:#64283D;}")
        self.pin_cancel_button.clicked.connect(self.cancel_pin_entry)
        self.pin_enter_button = QPushButton("ENTER  ➜")
        self.pin_enter_button.setMinimumHeight(48)
        self.pin_enter_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.pin_enter_button.setStyleSheet("QPushButton{color:#001323;background:#43C8FF;border:1px solid #73E5FF;border-radius:8px;font-size:14px;font-weight:800;} QPushButton:hover{background:#8BE3FF;}")
        self.pin_enter_button.clicked.connect(self.submit_pin)
        pin_actions.addWidget(self.pin_cancel_button)
        pin_actions.addWidget(self.pin_enter_button, 1)
        pin_layout.addLayout(pin_actions)
        self.pin_panel.hide()
        main.addWidget(self.pin_panel, 10)
        root.addLayout(main, 1)
        self.transaction_screen.hide()

    def show_transaction_screen(self, holder):
        self.content.hide()
        self.transaction_welcome.setText(f"Welcome, {holder}")
        self.update_clock()
        self.transaction_screen.setGeometry(self.background_widget.rect())
        self.transaction_screen.show()
        self.transaction_screen.raise_()

    def cancel_transaction_screen(self):
        if self.transaction_active:
            return
        if hasattr(self, "pin_panel") and self.pin_panel.isVisible():
            self.cancel_pin_entry()
            return
        self.transaction_screen.hide()
        self.content.show()
        self.content.raise_()

    # --------------------------------------------------------
    # INLINE PIN ENTRY (INSIDE THE MAIN ATM SCREEN)
    # --------------------------------------------------------
    def show_pin_entry(self, mode, title, subtitle=None, payload=None):
        """Show amount or PIN input inside the transaction screen itself."""
        if not self.inserted_card or self.transaction_active:
            return
        self.pin_mode = mode
        self.pin_payload = payload
        if mode in (
            "withdraw_amount",
            "withdraw",
            "deposit_amount",
            "deposit",
            "balance",
            "statement",
            "change_current",
        ):
            self.pin_attempts = 0
        if mode in ("withdraw_amount", "withdraw", "balance", "statement", "change_current", "change_new"):
            self.pending_new_pin = ""

        is_amount = mode in ("withdraw_amount", "deposit_amount")
        self.pin_heading.setText(title.upper())
        self.pin_subheading.setText(subtitle or "Enter your 4-digit PIN to continue")
        self.pin_status.setText("AMOUNT ENTRY" if is_amount else "SECURE INPUT ENABLED")
        self.pin_status.setStyleSheet("color:#67DDFF;background:transparent;font-size:11px;font-weight:600;letter-spacing:1px;")
        self.pin_display.setEchoMode(QLineEdit.EchoMode.Normal if is_amount else QLineEdit.EchoMode.Password)
        self.pin_display.setMaxLength(
            (5 if mode == "withdraw_amount" else 10) if is_amount else 4
        )
        self.pin_display.setPlaceholderText("₹ 0" if is_amount else "•   •   •   •")
        self.pin_display.clear()
        self.options_panel.hide()
        self.pin_panel.show()
        self.pin_panel.raise_()
        self.pin_display.setFocus()

    def add_pin_digit(self, digit):
        current = self.pin_display.text()
        is_amount = self.pin_mode in ("withdraw_amount", "deposit_amount")
        limit = 5 if self.pin_mode == "withdraw_amount" else 10
        if len(current) < limit:
            self.pin_display.setText(current + digit)
            if is_amount:
                self.pin_status.setText(f"AMOUNT: ₹{int(current + digit):,}")
            else:
                self.pin_status.setText(f"PIN LENGTH: {len(current) + 1}/4")

    def clear_pin_input(self):
        self.pin_display.clear()
        self.pin_status.setText("PIN CLEARED")

    def backspace_pin(self):
        self.pin_display.setText(self.pin_display.text()[:-1])

    def cancel_pin_entry(self):
        self.pin_mode = None
        self.pin_payload = None
        self.pending_new_pin = ""
        self.pin_display.clear()
        self.pin_panel.hide()
        self.options_panel.show()

    def _pin_error(self, message):
        self.pin_status.setText(message)
        self.pin_status.setStyleSheet("color:#FF8D9D;background:transparent;font-size:11px;font-weight:700;")

    def submit_pin(self):
        entered = self.pin_display.text().strip()
        mode = self.pin_mode

        # Amount entry uses the same on-screen keypad and panel as PIN entry.
        if mode in ("withdraw_amount", "deposit_amount"):
            if not entered.isdigit():
                message = (
                    "PLEASE ENTER A VALID DEPOSIT AMOUNT"
                    if mode == "deposit_amount"
                    else "PLEASE ENTER A WITHDRAWAL AMOUNT"
                )
                self._pin_error(message)
                return
            amount = int(entered)
            if mode == "withdraw_amount" and (
                amount < 100 or amount > 10000 or amount % 100 != 0
            ):
                self._pin_error("ENTER ₹100–₹10,000 IN MULTIPLES OF ₹100")
                return
            if mode == "deposit_amount" and amount <= 0:
                self._pin_error("DEPOSIT AMOUNT MUST BE GREATER THAN ZERO")
                return
            if mode == "withdraw_amount" and amount > self.demo_balance:
                self._pin_error("INSUFFICIENT BALANCE — ENTER A LOWER AMOUNT")
                return
            next_mode = "withdraw" if mode == "withdraw_amount" else "deposit"
            action = "withdraw" if mode == "withdraw_amount" else "deposit"
            self.show_pin_entry(
                next_mode, f"Authorize {action.title()}",
                f"Enter your 4-digit PIN to {action} ₹{amount:,.0f}", amount
            )
            return

        if len(entered) != 4 or not entered.isdigit():
            self._pin_error("PLEASE ENTER EXACTLY 4 DIGITS")
            return

        if mode in ("withdraw", "deposit", "balance", "statement", "change_current"):
            if entered != self.demo_pin:
                self.pin_attempts += 1
                remaining = 3 - self.pin_attempts
                if remaining <= 0:
                    self._pin_error("TOO MANY INCORRECT ATTEMPTS")
                    QTimer.singleShot(900, self.cancel_pin_entry)
                else:
                    self.pin_display.clear()
                    self._pin_error(f"INCORRECT PIN — {remaining} ATTEMPT(S) LEFT")
                return

        if mode == "withdraw":
            amount = int(self.pin_payload)
            # Only debit the account after the PIN has been verified.
            self.demo_balance -= amount
            self.demo_transactions.insert(0, (datetime.now().strftime("%d-%m-%Y"), "Cash withdrawal", -amount))
            self.pin_panel.hide()
            self.options_panel.show()
            self.transaction_active = True
            self.start_processing_flow()
            return

        if mode == "deposit":
            amount = int(self.pin_payload)
            self.demo_balance += amount
            self.demo_transactions.insert(
                0,
                (datetime.now().strftime("%d-%m-%Y"), "Cash deposit", amount),
            )
            self.pin_panel.hide()
            self.options_panel.show()
            self.transaction_active = True
            self.start_processing_flow(
                success_message=(
                    f"₹{amount:,.0f} has been deposited successfully.\n\n"
                    f"Available balance: ₹{self.demo_balance:,.2f}"
                )
            )
            return

        if mode == "balance":
            self.cancel_pin_entry()
            QMessageBox.information(self, "Account Balance", f"Account Holder: {self.inserted_card['holder']}\n\nAvailable Balance: ₹{self.demo_balance:,.2f}")
            return

        if mode == "statement":
            self.cancel_pin_entry()
            lines = [f"{date} | {description}: {'+' if amount > 0 else ''}₹{amount:,.2f}" for date, description, amount in self.demo_transactions[:5]]
            QMessageBox.information(self, "Mini Statement", "RECENT TRANSACTIONS\n\n" + "\n".join(lines))
            return

        if mode == "change_current":
            self.show_pin_entry("change_new", "Set New PIN", "Enter a new 4-digit PIN")
            return

        if mode == "change_new":
            self.pending_new_pin = entered
            self.show_pin_entry("change_confirm", "Confirm New PIN", "Enter the new PIN again to confirm")
            return

        if mode == "change_confirm":
            if entered != self.pending_new_pin:
                self.pending_new_pin = ""
                self.show_pin_entry("change_new", "PIN Did Not Match", "Enter a new 4-digit PIN and confirm it")
                self._pin_error("PINS DID NOT MATCH — TRY AGAIN")
                return
            self.demo_pin = entered
            self.cancel_pin_entry()
            QMessageBox.information(self, "PIN Updated", "Your demo PIN has been updated for this session.")

    def show_insert_card_message(self):
        if self.transaction_active:
            return
        popup = CardEntryPopup(self, language=self.current_language)
        popup.card_submitted.connect(self.on_demo_card_submitted)
        popup.exec()
        popup.deleteLater()

    def on_demo_card_submitted(self, number, holder, expiry):
        # Keep the selected card details for transaction actions.
        # Cardholder/card-number details are no longer displayed on the home screen.
        self.inserted_card = {
            "number": number,
            "holder": holder,
            "expiry": expiry,
        }
        self.show_transaction_screen(holder)

    def show_upi_popup(self):
        if self.transaction_active:
            return
        self.transaction_active = True
        try:
            popup = UPIPaymentPopup(self, timeout=6, language=self.current_language)
            popup.exec()
            popup.deleteLater()
        except Exception as exc:
            self.transaction_active = False
            QMessageBox.critical(self, "UPI Error", f"The UPI payment window could not be opened.\n\n{exc}")
            return
        self.start_processing_flow()

    def start_cash_withdrawal(self):
        if self.transaction_active or not self.inserted_card:
            return
        self.show_pin_entry(
            "withdraw_amount",
            "Cash Withdrawal",
            "Enter amount using the keypad (₹100–₹10,000, in multiples of ₹100)."
        )

    def start_cash_deposit(self):
        if self.transaction_active or not self.inserted_card:
            return
        self.show_pin_entry(
            "deposit_amount",
            "Cash Deposit",
            "Enter the whole-number amount to deposit."
        )

    def start_processing_flow(self, success_message=None):
        self.processing_success_message = success_message
        if self.processing_overlay is not None:
            self.processing_overlay.stop()
            self.processing_overlay.deleteLater()
            self.processing_overlay = None
        if self.cash_overlay is not None:
            self.cash_overlay.hide()
            self.cash_overlay.deleteLater()
            self.cash_overlay = None
        self.processing_overlay = TransactionProcessingOverlay(self.background_widget, language=self.current_language, duration=4000)
        self.processing_overlay.finished.connect(self.on_processing_finished)
        self.processing_overlay.setGeometry(self.background_widget.rect())
        self.processing_overlay.show()
        self.processing_overlay.raise_()

    def on_processing_finished(self):
        self.processing_overlay = None
        if self.processing_success_message is not None:
            message = self.processing_success_message
            self.processing_success_message = None
            self.return_to_main_screen()
            QMessageBox.information(self, "Deposit Successful", message)
            return
        self._start_cash_stage()

    def _start_cash_stage(self):
        if not self.transaction_active:
            return
        self.cash_overlay = CashCollectionOverlay(self.background_widget, language=self.current_language)
        self.cash_overlay.closed.connect(self.return_to_main_screen)
        self.cash_overlay.setGeometry(self.background_widget.rect())
        self.cash_overlay.show()
        self.cash_overlay.raise_()

    def return_to_main_screen(self):
        self.cash_overlay = None
        self.transaction_active = False
        if self.inserted_card:
            self.show_transaction_screen(self.inserted_card["holder"])
        else:
            self.transaction_screen.hide()
            self.content.show()

    def show_balance(self):
        if not self.inserted_card:
            return
        self.show_pin_entry("balance", "Check Balance", "Verify your PIN to view your balance")

    def show_mini_statement(self):
        if not self.inserted_card:
            return
        self.show_pin_entry("statement", "Mini Statement", "Verify your PIN to view recent transactions")

    def change_password(self):
        if not self.inserted_card:
            return
        self.show_pin_entry("change_current", "Change PIN", "Enter your current 4-digit PIN")

    def show_sos_popup(self):
        popup = SOSPopup(self, language=self.current_language)
        popup.exec()

    def update_clock(self):
        now = datetime.now()
        date_text = now.strftime("%d-%m-%Y")
        time_text = now.strftime("%I:%M %p")
        if self.current_language == "hi":
            time_text = time_text.replace("AM", "पूर्वाह्न").replace("PM", "अपराह्न")
        elif self.current_language == "bn":
            time_text = time_text.replace("AM", "পূর্বাহ্ণ").replace("PM", "অপরাহ্ণ")
        self.clock_label.setText(f"{date_text}   {time_text}")
        if hasattr(self, "transaction_clock"):
            self.transaction_clock.setText(f"{date_text}    {time_text}")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "content"):
            self.content.setGeometry(self.background_widget.rect())
        if hasattr(self, "transaction_screen"):
            self.transaction_screen.setGeometry(self.background_widget.rect())
        if hasattr(self, "original_logo"):
            self.update_logo_size()
        if hasattr(self, "welcome_intro"):
            self.welcome_intro.setFont(QFont("Segoe UI", max(12, min(int(self.height() * .025), 20))))
        if hasattr(self, "welcome_label"):
            size = max(28, min(int(min(self.width() * .04, self.height() * .075)), 64))
            font = QFont("Segoe UI", size)
            font.setBold(True)
            self.welcome_label.setFont(font)
        if hasattr(self, "tagline_label"):
            size = max(16, min(int(min(self.width() * .02, self.height() * .032)), 32))
            font = QFont("Segoe UI", size)
            font.setWeight(QFont.Weight.Medium)
            self.tagline_label.setFont(font)
        if self.processing_overlay is not None and self.processing_overlay.isVisible():
            self.processing_overlay.setGeometry(self.background_widget.rect())
        if self.cash_overlay is not None and self.cash_overlay.isVisible():
            self.cash_overlay.setGeometry(self.background_widget.rect())

    def closeEvent(self, event):
        if self.processing_overlay is not None:
            self.processing_overlay.stop()
        if self.cash_overlay is not None:
            self.cash_overlay.hide()
        self.transaction_active = False
        super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = StarkATM()
    window.show()
    sys.exit(app.exec())