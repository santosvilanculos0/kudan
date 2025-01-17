from PySide6.QtCore import QTimer
from PySide6.QtGui import QFont, QGuiApplication, QHideEvent, QShowEvent, QTextDocument
from PySide6.QtWidgets import QTextBrowser, QVBoxLayout, QWidget


class Widget(QWidget):
    def __init__(self) -> None:
        super().__init__()

        q_v_box_layout = QVBoxLayout(self)
        q_v_box_layout.setContentsMargins(0, 0, 0, 0)
        q_v_box_layout.setSpacing(0)
        self.q_text_browser = QTextBrowser()
        self.q_text_browser.setFont(QFont("Inter", int(14 / (96 / 72)), 400))
        q_v_box_layout.addWidget(self.q_text_browser)

        self.q_timer = QTimer(self)
        self.q_timer.setInterval(1_000)
        self.q_timer.timeout.connect(self.q_timer_timeout)

    def q_timer_timeout(self) -> None:
        q_text_document = QTextDocument()
        q_text_document.setPlainText(
            f"{str([f"(name={screen.name()}, size={screen.size()}, depth={screen.depth()}, device_pixel_ratio={screen.devicePixelRatio()}, refresh_rate={screen.refreshRate()}, model={screen.model()}, serial_number={screen.serialNumber()}, manufacturer={screen.manufacturer()}, native_interface={screen.nativeInterface()}, native_orientation={screen.nativeOrientation()}, orientation={screen.orientation()})" for screen in QGuiApplication.screens()])}"
        )
        self.q_text_browser.setDocument(q_text_document)

    def showEvent(self, event: QShowEvent) -> None:
        self.q_timer_timeout()
        self.q_timer.start()
        return super().showEvent(event)

    def hideEvent(self, event: QHideEvent) -> None:
        self.q_timer.stop()
        return super().hideEvent(event)
