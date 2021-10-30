import sys
import os.path
import catte
from PyQt5.QtWidgets import (
    QPlainTextEdit, QPushButton, QApplication, QVBoxLayout, QDialog,
    QLabel, QGraphicsView, QFrame, QAbstractScrollArea, QGraphicsScene, QGraphicsPixmapItem)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QSize
from PIL.ImageQt import ImageQt
from PIL import Image, ImageDraw, ImageFont
import textwrap


class Form(QDialog):

    def __init__(self, parent=None):
        super(Form, self).__init__(parent)
        # Create widgets
        self.edit = QPlainTextEdit()
        self.edit.setPlaceholderText("Write text here")
        self.edit.textChanged.connect(self.update_preview)
        self.edit.cursorPositionChanged.connect(self.update_preview)
        self.edit.setStyleSheet("QPlainTextEdit { min-height: 15em; }")

        self.pic = QGraphicsView()
        self.pic.setStyleSheet("QGraphicsView { min-height: 15em }")
        self.pic.setSizeIncrement(QSize(0, 0))
        self.pic.setFrameShadow(QFrame.Raised)
        self.pic.setSizeAdjustPolicy(
            QAbstractScrollArea.AdjustToContents)
        self.pic.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.pic.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.pic.setAlignment(Qt.AlignTop)
        self.pic.setObjectName("pic")
        self.update_preview()

        self.button = QPushButton("Print!")

        # Create layout and add widgets
        layout = QVBoxLayout()
        layout.addWidget(self.edit)
        layout.addWidget(self.pic)
        layout.addWidget(self.button)

        # Set dialog layout
        self.setLayout(layout)
        self.setStyleSheet("QDialog { min-width: 400px }")

        # Add button signal to greetings slot
        self.button.clicked.connect(self.save_image)

    def generate_image(self):
        # Clear Image
        im = Image.new(mode="RGBA", size=(324, 1),
                       color=(255, 255, 255, 255))

        # Draw Text
        script_path = os.path.abspath(os.path.dirname(__file__))
        font_path = os.path.join(script_path, 'RobotoMono.ttf')
        font = ImageFont.truetype(font=font_path, size=24)
        ascent, descent = font.getmetrics()
        (font_width, baseline) = font.getsize('0')
        line_height = ascent + descent

        # Convert input to string with newlines
        # apparently this is non-trivial ¯\_(ツ)_/¯
        text = self.edit.toPlainText()
        paragraphs = text.splitlines()

        lines = []
        for p in paragraphs:
            lines += textwrap.wrap(
                p,
                width=int(im.size[0] / font_width - 1),
                replace_whitespace=False)

        lineCount = len(lines)

        # Resize image to fit number of lines
        newCanvasSize = (
            im.size[0],
            max(line_height, line_height * lineCount))
        im = im.resize(newCanvasSize)

        # Draw text on image
        draw = ImageDraw.Draw(im)
        draw.multiline_text(
            (0, 0),
            '\n'.join(lines),
            fill=(0, 0, 0),
            font=font)

        return im

    def update_preview(self):
        # Update preview image
        im = self.generate_image()
        scene = QGraphicsScene(self)
        pixmap = QPixmap.fromImage(ImageQt(im))
        item = QGraphicsPixmapItem(pixmap)
        scene.addItem(item)
        self.pic.setScene(scene)

        # Scroll to match vertical position of cursor
        cursor_line = self.edit.textCursor().block().firstLineNumber()
        line_count = self.edit.document().blockCount()
        scroll_height = self.pic.verticalScrollBar().maximum()
        self.pic.verticalScrollBar().setValue(cursor_line / line_count * scroll_height)

    # Greets the user
    def save_image(self):
        im = self.generate_image()
        im.save('catapp.png')


if __name__ == '__main__':
    # Create the Qt Application
    app = QApplication(sys.argv)
    # Create and show the form
    form = Form()
    form.show()
    # Run the main Qt loop
    sys.exit(app.exec())
