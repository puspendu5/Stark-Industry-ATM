import sys
from pathlib import Path

from PySide6.QtCore import Qt, QUrl, QTimer
from PySide6.QtGui import QColor, QFont
from PySide6.QtMultimedia import QSoundEffect
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QGraphicsDropShadowEffect,
)


class SOSPopup(QDialog):
    def __init__(self, parent=None, language="en"):
        super().__init__(parent)

        self.language = language

        self.translations = {
            "en": {
                "window": "Emergency Assistance",
                "heading": "SOS SIGNAL SENT",
                "message": (
                    "Your emergency alert has been triggered.\n"
                    "Please remain calm and seek immediate assistance."
                ),
                "close": "CLOSE",
            },
            "hi": {
                "window": "आपातकालीन सहायता",
                "heading": "SOS संकेत भेज दिया गया",
                "message": (
                    "आपका आपातकालीन अलर्ट सक्रिय कर दिया गया है।\n"
                    "कृपया शांत रहें और तुरंत सहायता प्राप्त करें।"
                ),
                "close": "बंद करें",
            },
            "bn": {
                "window": "জরুরি সহায়তা",
                "heading": "SOS সংকেত পাঠানো হয়েছে",
                "message": (
                    "আপনার জরুরি সতর্কবার্তা সক্রিয় করা হয়েছে।\n"
                    "অনুগ্রহ করে শান্ত থাকুন এবং দ্রুত সাহায্য নিন।"
                ),
                "close": "বন্ধ করুন",
            },
        }

        t = self.translations.get(self.language, self.translations["en"])

        self.setWindowTitle(t["window"])
        self.setFixedSize(440, 340)
        self.setModal(True)

        self.setStyleSheet("""
            QDialog {
                background-color: #07111F;
                border: 1px solid #FF394F;
                border-radius: 18px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 24, 30, 24)
        layout.setSpacing(12)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # --------------------------------
        # SOS SYMBOL
        # --------------------------------
        self.sos_icon = QLabel("SOS")
        self.sos_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.sos_icon.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        self.sos_icon.setStyleSheet("""
            QLabel {
                color: #FF394F;
                background: transparent;
                border: 2px solid #FF394F;
                border-radius: 38px;
                padding: 12px;
            }
        """)
        self.sos_icon.setFixedSize(100, 100)
        layout.addWidget(self.sos_icon, 0, Qt.AlignmentFlag.AlignHCenter)

        # --------------------------------
        # HEADING
        # --------------------------------
        self.heading = QLabel(t["heading"])
        self.heading.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.heading.setWordWrap(True)
        self.heading.setFont(QFont("Segoe UI", 17, QFont.Weight.Bold))
        self.heading.setStyleSheet("""
            QLabel {
                color: #FF394F;
                background: transparent;
                border: none;
            }
        """)
        layout.addWidget(self.heading)

        # --------------------------------
        # MESSAGE
        # --------------------------------
        self.message = QLabel(t["message"])
        self.message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.message.setWordWrap(True)
        self.message.setFont(QFont("Segoe UI", 10))
        self.message.setStyleSheet("""
            QLabel {
                color: #B9CBE0;
                background: transparent;
                border: none;
            }
        """)
        layout.addWidget(self.message)

        layout.addSpacing(5)

        # --------------------------------
        # CLOSE BUTTON
        # --------------------------------
        self.close_button = QPushButton(t["close"])
        self.close_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.close_button.setFixedHeight(42)
        self.close_button.setStyleSheet("""
            QPushButton {
                background-color: #FF394F;
                color: white;
                border: none;
                border-radius: 9px;
                font-family: 'Segoe UI';
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #E92740;
            }
            QPushButton:pressed {
                background-color: #C91D33;
            }
        """)
        self.close_button.clicked.connect(self.close_popup)
        layout.addWidget(self.close_button)

        # --------------------------------
        # RED GLOW
        # --------------------------------
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(28)
        shadow.setOffset(0, 0)
        shadow.setColor(QColor(255, 40, 70, 75))
        self.setGraphicsEffect(shadow)

        # --------------------------------
        # SOS ALARM SOUND
        # --------------------------------
        self.alarm_sound = QSoundEffect(self)
        self.alarm_sound.setVolume(0.8)
        self.alarm_sound.setLoopCount(3)

        sound_path = Path(__file__).resolve().parent / "sos_alarm.wav"
        if sound_path.exists():
            self.alarm_sound.setSource(QUrl.fromLocalFile(str(sound_path.resolve())))
        else:
            print(f"SOS alarm sound not found: {sound_path}")

        QTimer.singleShot(500, self.play_alarm)

    def play_alarm(self):
        if self.alarm_sound.source().isValid():
            self.alarm_sound.play()

    def close_popup(self):
        self.alarm_sound.stop()
        self.accept()

    def reject(self):
        self.alarm_sound.stop()
        super().reject()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    popup = SOSPopup(language="en")
    popup.exec()
    sys.exit(0)