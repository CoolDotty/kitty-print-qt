import sys
import os.path
import catte
from PySide6.QtWidgets import (
    QPlainTextEdit, QPushButton, QApplication, QVBoxLayout, QDialog,
    QLabel, QScrollArea)
from PySide6.QtGui import QPixmap
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
        self.edit.setStyleSheet("QPlainTextEdit { min-height: 15em }")

        self.pic = QLabel()
        self.update_preview()

        self.scrollArea = QScrollArea()

        self.button = QPushButton("Print!")

        # Create layout and add widgets
        layout = QVBoxLayout()
        layout.addWidget(self.edit)
        layout.addWidget(self.scrollArea)
        layout.addWidget(self.button)

        self.scrollArea.setWidget(self.pic)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setStyleSheet("QScrollArea { min-height: 15em }")

        # Set dialog layout
        self.setLayout(layout)
        self.setStyleSheet("QVBoxLayout { min-width: 400px }")

        # Add button signal to greetings slot
        self.button.clicked.connect(self.save_image)

    def generate_image(self):
        # Clear Image
        im = Image.new(mode="RGB", size=(324, 1),
                       color=(255, 255, 255))

        # Draw Text
        script_path = os.path.abspath(os.path.dirname(__file__))
        font_path = os.path.join(script_path, 'RobotoMono.ttf')
        font = ImageFont.truetype(font=font_path, size=16)
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
                width=int(im.size[0] / font_width),
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
        im = self.generate_image()

        # Show image in widget
        qim = ImageQt(im)
        pix = QPixmap.fromImage(qim)
        self.pic.setPixmap(pix)

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
