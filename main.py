import sys
import fitz
from PyQt6.QtWidgets import QSizePolicy
from PyQt6.QtWidgets import QHBoxLayout
from PyQt6.QtWidgets import QScrollArea

from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QPushButton,
    QLabel,
    QVBoxLayout,
    QFileDialog
)

from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt


class Arcana(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Arcana")

        self.setStyleSheet("""
            QWidget {
                background-color: #121212;
                color: white;
                font-size: 14px;
            }

            QPushButton {
                background-color: #1E1E1E;
                border: 1px solid #333;
                padding: 8px;
                border-radius: 8px;
            }

            QPushButton:hover {
                background-color: #2A2A2A;
            }

            QLabel {
                color: white;
            }

            QScrollArea {
                border: none;
            }
        """)

        # Open window relative to screen size
        screen = QApplication.primaryScreen().availableGeometry()

        self.resize(
            int(screen.width() * 0.7),
            int(screen.height() * 0.85)
        )

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setScaledContents(False)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.image_label)

        self.image_label.setSizePolicy(
        QSizePolicy.Policy.Ignored,
        QSizePolicy.Policy.Ignored
        )

        self.open_button = QPushButton("Open PDF")
        self.next_button = QPushButton("Next Page")
        self.prev_button = QPushButton("Previous Page")
        self.zoom_in_button = QPushButton("Zoom In")
        self.zoom_out_button = QPushButton("Zoom Out")

        self.open_button.clicked.connect(self.open_pdf)
        self.next_button.clicked.connect(self.next_page)
        self.prev_button.clicked.connect(self.prev_page)
        self.zoom_in_button.clicked.connect(self.zoom_in)
        self.zoom_out_button.clicked.connect(self.zoom_out)

        self.page_label = QLabel("Page: -")

        controls_layout = QHBoxLayout()
        controls_layout.addWidget(self.open_button)
        controls_layout.addWidget(self.prev_button)
        controls_layout.addWidget(self.next_button)
        controls_layout.addWidget(self.page_label)
        controls_layout.addWidget(self.zoom_out_button)
        controls_layout.addWidget(self.zoom_in_button)
        

        layout = QVBoxLayout()
        layout.addLayout(controls_layout)
        layout.addWidget(self.scroll_area)

        self.setLayout(layout)

        self.current_pixmap = None

        self.doc = None
        self.current_page = 0
        self.zoom_factor = 1.0

    def open_pdf(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open PDF",
            "",
            "PDF Files (*.pdf)"
        )

        if file_path:
            self.doc = fitz.open(file_path)
            self.current_page = 0
            self.display_pdf_page()
            self.update_page_label()

    def display_pdf_page(self):
        page = self.doc[self.current_page]

        matrix = fitz.Matrix(self.zoom_factor, self.zoom_factor)
        pix = page.get_pixmap(matrix=matrix)

        img = QImage(
            pix.samples,
            pix.width,
            pix.height,
            pix.stride,
            QImage.Format.Format_RGB888
        )

        self.current_pixmap = QPixmap.fromImage(img)

        self.update_image()

    def update_page_label(self):
        if self.doc:
            total_pages = len(self.doc)

            self.page_label.setText(
                f"Page {self.current_page + 1} / {total_pages}"
            )

    def update_image(self):
        if self.current_pixmap:
            self.image_label.setPixmap(self.current_pixmap)

    def next_page(self):
        if self.doc and self.current_page < len(self.doc) - 1:
            self.current_page += 1
            self.display_pdf_page()
            self.update_page_label()

    def prev_page(self):
        if self.doc and self.current_page > 0:
            self.current_page -= 1
            self.display_pdf_page()
            self.update_page_label()

    def zoom_in(self):
        self.zoom_factor += 0.1
        self.display_pdf_page()

    def zoom_out(self):
        if self.zoom_factor > 0.2:
            self.zoom_factor -= 0.1
            self.display_pdf_page()

    def wheelEvent(self, event):
        if event.angleDelta().y() > 0:
            self.zoom_factor += 0.1
        else:
            if self.zoom_factor > 0.2:
                self.zoom_factor -= 0.1
        self.update_image()

    # Trigger whenever window resizes
    def resizeEvent(self, event):
        self.update_image()
        super().resizeEvent(event)


app = QApplication(sys.argv)

window = Arcana()
window.show()

sys.exit(app.exec())