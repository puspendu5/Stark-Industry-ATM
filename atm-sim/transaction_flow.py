from PySide6.QtCore import QObject, Signal

from transaction_screens import (
    TransactionProcessingOverlay,
    CashCollectionOverlay,
)


class TransactionFlow(QObject):
    """
    Controls the ATM transaction sequence:

    1. Show the processing screen.
    2. Show the cash-collection screen, if requested.
    3. Return control to main.py when finished.

    Expected by main.py:
        TransactionFlow(
            background_widget,
            get_language=...,
            parent=...
        )

        flow.start(show_cash_screen=True)
        flow.completed.connect(...)
        flow.resize_overlays()
        flow.cancel()
    """

    completed = Signal()
    failed = Signal(str)

    def __init__(
        self,
        background_widget,
        get_language=lambda: "en",
        parent=None,
    ):
        super().__init__(parent)

        self.background_widget = background_widget
        self.get_language = get_language

        self.processing_screen = None
        self.cash_screen = None

        self.is_active = False
        self.show_cash_screen = True
        self.current_stage = "idle"

    def start(self, show_cash_screen=True):
        """Start a new transaction flow."""
        if self.is_active:
            return False

        self.is_active = True
        self.show_cash_screen = show_cash_screen
        self.current_stage = "processing"

        try:
            self._start_processing_stage()
            return True

        except Exception as error:
            self._fail(str(error))
            return False

    def _start_processing_stage(self):
        """Display the processing screen independently."""
        self._close_screen("processing_screen")

        screen = TransactionProcessingOverlay(
            self.background_widget,
            language=self.get_language(),
            duration=4000,
        )

        self.processing_screen = screen
        screen.setGeometry(self.background_widget.rect())

        screen.finished.connect(
            self._on_processing_finished
        )

        screen.show()
        screen.raise_()

    def _on_processing_finished(self):
        """Continue to cash collection after processing."""
        if not self.is_active:
            return

        if self.current_stage != "processing":
            return

        self._close_screen("processing_screen")

        if not self.show_cash_screen:
            self._finish()
            return

        self.current_stage = "cash_collection"

        try:
            self._start_cash_stage()

        except Exception as error:
            self._fail(str(error))

    def _start_cash_stage(self):
        """Display the cash-collection screen."""
        self._close_screen("cash_screen")

        screen = CashCollectionOverlay(
            self.background_widget,
            language=self.get_language(),
        )

        self.cash_screen = screen
        screen.setGeometry(self.background_widget.rect())

        screen.closed.connect(
            self._on_cash_collection_finished
        )

        screen.show()
        screen.raise_()

    def _on_cash_collection_finished(self):
        """Finish after the cash screen closes."""
        if not self.is_active:
            return

        if self.current_stage != "cash_collection":
            return

        self._close_screen("cash_screen")
        self._finish()

    def _finish(self):
        self.current_stage = "idle"
        self.is_active = False
        self.completed.emit()

    def _fail(self, message):
        self._close_screen("processing_screen")
        self._close_screen("cash_screen")

        self.current_stage = "idle"
        self.is_active = False

        self.failed.emit(message)

    def _close_screen(self, attribute_name):
        """Close and release a screen safely."""
        screen = getattr(self, attribute_name, None)

        if screen is None:
            return

        setattr(self, attribute_name, None)

        try:
            screen.close()
            screen.deleteLater()
        except RuntimeError:
            pass

    def resize_overlays(self):
        """Keep the active screen fitted to the ATM background."""
        geometry = self.background_widget.rect()

        for screen in (
            self.processing_screen,
            self.cash_screen,
        ):
            if screen is not None:
                try:
                    screen.setGeometry(geometry)
                except RuntimeError:
                    pass

    def cancel(self):
        """Stop the current flow and close both screens."""
        self._close_screen("processing_screen")
        self._close_screen("cash_screen")

        self.current_stage = "idle"
        self.is_active = False
