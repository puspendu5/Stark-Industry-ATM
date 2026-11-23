
from PySide6.QtCore import (
    Qt, Signal, QPoint, QRect, QPropertyAnimation, QEasingCurve
)
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QDialog, QWidget, QLabel, QPushButton, QFrame, QScrollArea,
    QVBoxLayout, QHBoxLayout, QGraphicsDropShadowEffect
)


class CardEntryPopup(QDialog):
    """
    Demo ATM card insertion popup.

    Emits:
        card_submitted(number, holder, expiry)
    after the insertion animation finishes.
    """

    card_submitted = Signal(str, str, str)

    CARDS = [
        {
            "name": "ERSHA DAS",
            "holder": "ERSHA DAS",
            "number": "4532 1000 2000 0101",
            "expiry": "11/27",
            "color": "#252C3A",
            "accent": "#B3C7DF",
        },
        {
            "name": "PUSPENDU PURKAIT",
            "holder": "PUSPENDU PURKAIT",
            "number": "4532 1000 2000 0102",
            "expiry": "10/28",
            "color": "#78501D",
            "accent": "#FFD88A",
        },
        {
            "name": "PRABIN MANDAL",
            "holder": "PRABIN MANDAL",
            "number": "4532 1000 2000 0103",
            "expiry": "12/28",
            "color": "#075A79",
            "accent": "#42D7FF",
        },
        {
            "name": "SAGAR SAMANTA",
            "holder": "SAGAR SAMANTA",
            "number": "4532 1000 2000 0104",
            "expiry": "09/27",
            "color": "#264D35",
            "accent": "#83F0A5",
        },
    ]

    def __init__(self, parent=None, language="en"):
        super().__init__(parent)

        self.language = language
        self.selected_index = None
        self.animating = False
        self.inserted = False
        self._animation = None

        self.setWindowTitle("ATM Card Insertion")
        self.setModal(True)
        self.setMinimumSize(650, 440)
        self.resize(820, 510)

        self.setStyleSheet("""
            QDialog {
                background: #080E18;
                color: #E8F3FF;
            }

            QLabel {
                background: transparent;
            }

            QPushButton {
                color: #DBEFFF;
                background: #13243A;
                border: 1px solid #34516D;
                border-radius: 7px;
                padding: 10px 16px;
                font-weight: bold;
            }

            QPushButton:hover {
                background: #1A3B55;
                border-color: #4DD7FF;
            }

            QPushButton:disabled {
                color: #63778B;
                background: #101A27;
                border-color: #243346;
            }

            QPushButton#insertButton {
                color: #03121D;
                background: #48D5FF;
                border: 1px solid #8AE9FF;
            }

            QPushButton#insertButton:hover {
                background: #91EAFF;
            }
        """)

        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(18, 18, 18, 16)
        root.setSpacing(12)

        # ATM machine body
        self.machine = QFrame()
        self.machine.setObjectName("machine")
        self.machine.setStyleSheet("""
            QFrame#machine {
                background: #172334;
                border: 2px solid #43566C;
                border-radius: 16px;
            }
        """)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(24)
        shadow.setOffset(0, 5)
        shadow.setColor(QColor(0, 0, 0, 170))
        self.machine.setGraphicsEffect(shadow)

        machine_layout = QVBoxLayout(self.machine)
        machine_layout.setContentsMargins(16, 14, 16, 14)
        machine_layout.setSpacing(12)

        # Header
        header = QHBoxLayout()

        logo = QLabel("S")
        logo.setFixedSize(34, 34)
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo.setStyleSheet("""
            background: #42D1FF;
            color: #07111D;
            border-radius: 7px;
            font-size: 23px;
            font-weight: 900;
        """)

        heading = QVBoxLayout()

        title = QLabel("STARK")
        title.setStyleSheet(
            "font-size:18px;font-weight:900;letter-spacing:3px;"
        )

        subtitle = QLabel("ATM CARD SYSTEM")
        subtitle.setStyleSheet(
            "color:#8CA9C6;font-size:9px;letter-spacing:2px;"
        )

        heading.addWidget(title)
        heading.addWidget(subtitle)

        header.addWidget(logo)
        header.addLayout(heading)
        header.addStretch()

        self.status_light = QLabel("●")
        self.status_light.setStyleSheet(
            "color:#43E8AE;font-size:15px;"
        )

        self.status_text = QLabel("READY")
        self.status_text.setStyleSheet(
            "color:#8EDFC5;font-size:10px;font-weight:bold;"
            "letter-spacing:2px;"
        )

        header.addWidget(self.status_light)
        header.addWidget(self.status_text)

        machine_layout.addLayout(header)

        separator = QFrame()
        separator.setFixedHeight(2)
        separator.setStyleSheet("background:#30445A;border:none;")
        machine_layout.addWidget(separator)

        # Instruction panel and card reader
        upper = QHBoxLayout()
        upper.setSpacing(14)

        instruction_panel = QFrame()
        instruction_panel.setStyleSheet("""
            QFrame {
                background: #0A1422;
                border: 1px solid #293E55;
                border-radius: 10px;
            }
        """)

        instruction_layout = QVBoxLayout(instruction_panel)
        instruction_layout.setContentsMargins(15, 12, 15, 12)

        small_line = QFrame()
        small_line.setFixedSize(48, 3)
        small_line.setStyleSheet(
            "background:#42D1FF;border:none;border-radius:1px;"
        )

        instruction_title = QLabel("SELECT A CARD")
        instruction_title.setStyleSheet(
            "font-size:15px;font-weight:bold;letter-spacing:2px;"
        )

        instruction_subtitle = QLabel("FROM THE HOLDER BELOW")
        instruction_subtitle.setStyleSheet(
            "font-size:10px;color:#80B6E0;letter-spacing:1px;"
        )

        self.instruction = QLabel(
            "Choose a demo card, then insert it into the slot."
        )
        self.instruction.setWordWrap(True)
        self.instruction.setStyleSheet(
            "color:#8FA8C2;font-size:11px;"
        )

        instruction_layout.addWidget(small_line)
        instruction_layout.addSpacing(5)
        instruction_layout.addWidget(instruction_title)
        instruction_layout.addWidget(instruction_subtitle)
        instruction_layout.addSpacing(8)
        instruction_layout.addWidget(self.instruction)
        instruction_layout.addStretch()

        upper.addWidget(instruction_panel, 3)

        # Card reader
        reader = QFrame()
        reader.setFixedWidth(190)
        reader.setStyleSheet("""
            QFrame {
                background: #0A111D;
                border: 2px solid #4A5C70;
                border-radius: 11px;
            }
        """)

        reader_layout = QVBoxLayout(reader)
        reader_layout.setContentsMargins(12, 12, 12, 12)
        reader_layout.setSpacing(9)

        reader_title = QLabel("CARD READER")
        reader_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        reader_title.setStyleSheet(
            "font-size:9px;color:#86A8C8;font-weight:bold;"
            "letter-spacing:2px;border:none;"
        )

        self.slot = QFrame()
        self.slot.setFixedHeight(39)
        self.slot.setStyleSheet("""
            QFrame {
                background: #01050B;
                border: 2px solid #43546A;
                border-radius: 5px;
            }
        """)

        slot_layout = QVBoxLayout(self.slot)
        slot_layout.setContentsMargins(5, 7, 5, 7)

        self.slot_light = QFrame()
        self.slot_light.setFixedHeight(3)
        self.slot_light.setStyleSheet("""
            background: #35CFFF;
            border: none;
            border-radius: 1px;
        """)

        slot_shadow = QGraphicsDropShadowEffect(self)
        slot_shadow.setBlurRadius(12)
        slot_shadow.setColor(QColor(40, 190, 255, 200))
        slot_shadow.setOffset(0, 0)
        self.slot_light.setGraphicsEffect(slot_shadow)

        slot_layout.addWidget(self.slot_light)

        arrow = QLabel("⌃")
        arrow.setAlignment(Qt.AlignmentFlag.AlignCenter)
        arrow.setStyleSheet(
            "color:#A6CBEA;font-size:27px;border:none;"
        )

        reader_layout.addWidget(reader_title)
        reader_layout.addSpacing(5)
        reader_layout.addWidget(self.slot)
        reader_layout.addWidget(arrow)
        reader_layout.addStretch()

        upper.addWidget(reader, 2)
        machine_layout.addLayout(upper)

        # Scrollable card holder
        holder_label = QLabel("CARD HOLDER")
        holder_label.setStyleSheet(
            "color:#87A8C6;font-size:10px;font-weight:bold;"
            "letter-spacing:2px;"
        )
        machine_layout.addWidget(holder_label)

        self.holder = QFrame()
        self.holder.setStyleSheet("""
            QFrame {
                background: #09111D;
                border: 1px solid #34485E;
                border-radius: 9px;
            }
        """)

        holder_layout = QVBoxLayout(self.holder)
        holder_layout.setContentsMargins(6, 6, 6, 6)
        holder_layout.setSpacing(0)

        self.card_scroll = QScrollArea()
        self.card_scroll.setWidgetResizable(True)
        self.card_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.card_scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        self.card_scroll.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.card_scroll.setFixedHeight(142)
        self.card_scroll.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }

            QScrollBar:horizontal {
                height: 8px;
                background: #101D2C;
                margin: 3px 4px 0 4px;
                border-radius: 4px;
            }

            QScrollBar::handle:horizontal {
                background: #426681;
                min-width: 35px;
                border-radius: 4px;
            }

            QScrollBar::handle:horizontal:hover {
                background: #42D1FF;
            }

            QScrollBar::add-line:horizontal,
            QScrollBar::sub-line:horizontal {
                width: 0;
            }
        """)

        self.card_strip = QWidget()
        self.card_strip.setStyleSheet("background: transparent;")

        strip_layout = QHBoxLayout(self.card_strip)
        strip_layout.setContentsMargins(4, 4, 4, 8)
        strip_layout.setSpacing(10)

        self.card_widgets = []

        for index, card in enumerate(self.CARDS):
            card_widget = self._create_card(card, index)
            self.card_widgets.append(card_widget)
            strip_layout.addWidget(card_widget)

        self.card_scroll.setWidget(self.card_strip)
        holder_layout.addWidget(self.card_scroll)
        machine_layout.addWidget(self.holder)

        # Bottom controls
        controls = QHBoxLayout()

        self.cancel_button = QPushButton("←  CANCEL")
        self.cancel_button.clicked.connect(self.reject)

        self.insert_button = QPushButton("⇧  INSERT CARD")
        self.insert_button.setObjectName("insertButton")
        self.insert_button.setEnabled(False)
        self.insert_button.clicked.connect(self.insert_selected_card)

        controls.addWidget(self.cancel_button)
        controls.addStretch()
        controls.addWidget(self.insert_button)

        machine_layout.addLayout(controls)
        root.addWidget(self.machine)

        footer = QLabel(
            "DEMO SIMULATION  •  NO PHYSICAL CARD READER"
        )
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer.setStyleSheet(
            "color:#58728C;font-size:9px;letter-spacing:1px;"
        )
        root.addWidget(footer)

        # Floating card for the insertion animation
        self.moving_card = QLabel(self)
        self.moving_card.hide()
        self.moving_card.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.moving_card.setStyleSheet("""
            background: #075A79;
            color: white;
            border: 2px solid #70DFFF;
            border-radius: 8px;
            font-size: 11px;
            font-weight: bold;
        """)

    def _create_card(self, card, index):
        button = QPushButton()
        button.setFixedSize(190, 112)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setCheckable(True)

        button.setStyleSheet(f"""
            QPushButton {{
                text-align: left;
                padding: 9px;
                color: white;
                background: {card['color']};
                border: 2px solid #53667A;
                border-radius: 9px;
            }}

            QPushButton:hover {{
                border: 2px solid {card['accent']};
            }}

            QPushButton:checked {{
                border: 3px solid {card['accent']};
            }}
        """)

        button.setText(
            f"▦  STARK\n"
            f"◉  CONTACTLESS\n\n"
            f"{card['name']}\n"
            f"••••  {card['number'][-4:]}\n"
            f"{card['holder']}"
        )

        button.clicked.connect(
            lambda checked=False, i=index: self.select_card(i)
        )

        return button

    def select_card(self, index):
        if self.animating or self.inserted:
            return

        self.selected_index = index
        card = self.CARDS[index]

        for i, widget in enumerate(self.card_widgets):
            widget.setChecked(i == index)

        self.instruction.setText(
            f"{card['name']} selected. "
            "Press INSERT CARD to continue."
        )

        self.status_text.setText("CARD SELECTED")
        self.status_light.setStyleSheet(
            "color:#42D1FF;font-size:15px;"
        )
        self.insert_button.setEnabled(True)

    def insert_selected_card(self):
        if self.animating or self.inserted:
            return

        if self.selected_index is None:
            self.instruction.setText(
                "Select one of the cards in the holder first."
            )
            return

        self.animating = True
        self.insert_button.setEnabled(False)
        self.cancel_button.setEnabled(False)

        card = self.CARDS[self.selected_index]
        source = self.card_widgets[self.selected_index]

        start = QRect(
            source.mapTo(self, QPoint(0, 0)),
            source.size()
        )

        end = QRect(
            self.slot.mapTo(self, QPoint(0, 0)),
            self.slot.size()
        )

        self.moving_card.setText(
            f"STARK  ••••  {card['number'][-4:]}"
        )

        self.moving_card.setStyleSheet(f"""
            background: {card['color']};
            color: white;
            border: 2px solid {card['accent']};
            border-radius: 7px;
            font-size: 10px;
            font-weight: bold;
        """)

        self.moving_card.setGeometry(start)
        self.moving_card.show()
        self.moving_card.raise_()

        self.status_text.setText("INSERTING")
        self.status_light.setStyleSheet(
            "color:#F5CC72;font-size:15px;"
        )
        self.slot_light.setStyleSheet(
            "background:#F5CC72;border:none;border-radius:1px;"
        )

        animation = QPropertyAnimation(
            self.moving_card, b"geometry", self
        )
        animation.setDuration(950)
        animation.setStartValue(start)
        animation.setEndValue(end)
        animation.setEasingCurve(QEasingCurve.Type.InOutCubic)

        self._animation = animation
        animation.finished.connect(self._finish_insertion)
        animation.start()

    def _finish_insertion(self):
        if self.selected_index is None:
            return

        card = self.CARDS[self.selected_index]

        self.moving_card.hide()
        self.animating = False
        self.inserted = True

        self.status_text.setText("CARD INSERTED")
        self.status_light.setStyleSheet(
            "color:#43E8AE;font-size:15px;"
        )
        self.slot_light.setStyleSheet(
            "background:#43E8AE;border:none;border-radius:1px;"
        )

        self.instruction.setText(
            f"{card['name']} inserted successfully. "
            "Returning control to the ATM."
        )

        self.insert_button.setText("✓  CARD INSERTED")
        self.insert_button.setEnabled(False)

        # Send the selected card details to the main ATM window.
        self.card_submitted.emit(
            card["number"].replace(" ", ""),
            card["holder"],
            card["expiry"]
        )

        self.accept()
