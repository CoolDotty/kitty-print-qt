import sys
import io
import os.path
import catte
from PyQt5.QtWidgets import (
    QPlainTextEdit, QPushButton, QApplication, QVBoxLayout,
    QWidget, QGraphicsView, QFrame, QAbstractScrollArea, QGraphicsScene, QGraphicsPixmapItem)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QSize, QRectF
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
from PIL.ImageQt import ImageQt
import textwrap
import asyncio


class Main(QWidget):

    def __init__(self, parent=None):
        super(Main, self).__init__(parent)
        # Create widgets
        self.edit = QPlainTextEdit()
        self.edit.setPlaceholderText("Write text here")
        self.edit.textChanged.connect(self.update_preview)
        self.edit.cursorPositionChanged.connect(self.update_preview)

        self.pic = QGraphicsView()
        self.pic.setSizeIncrement(QSize(0, 0))
        self.pic.setFrameShadow(QFrame.Raised)
        self.pic.setSizeAdjustPolicy(
            QAbstractScrollArea.AdjustToContents)
        self.pic.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.pic.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.pic.setAlignment(Qt.AlignTop)
        self.pic.setObjectName("pic")
        # self.pic.setStyleSheet("""
        #    QGraphicsView {
        #        max-width: 384px;
        #        max-height: 384px;
        #        background: white;
        #    }
        # """)
        self.update_preview()

        self.button = QPushButton("Print!")

        # Create layout and add widgets
        layout = QVBoxLayout()
        layout.addWidget(self.edit)
        layout.addWidget(self.pic)
        layout.addWidget(self.button)

        # Set dialog layout
        self.setLayout(layout)

        # Add button signal to greetings slot
        self.button.clicked.connect(self.save_image)

    def generate_image(self):
        # Clear Image
        im = Image.new(mode="RGBA", size=(384, 1),
                       color=(255, 255, 255, 255))

        # Draw Text
        script_path = os.path.abspath(os.path.dirname(__file__))
        font_path = os.path.join(script_path, 'RobotoMono.ttf')
        font = ImageFont.truetype(font=font_path, size=15)
        ascent, descent = font.getmetrics()
        (font_width, baseline) = font.getsize('M')
        line_height = ascent + descent

        # Convert input to string with newlines
        # apparently this is non-trivial ¯\_(ツ)_/¯
        text = self.edit.toPlainText()
        paragraphs = text.splitlines()

        lines = []
        for p in paragraphs:
            wrapped = textwrap.wrap(
                p,
                width=int(im.size[0] / font_width),
                replace_whitespace=False,
                drop_whitespace=False)
            if (len(wrapped) > 0):
                lines += wrapped
            else:
                lines += ['']

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

        # Convert to black and white
        bw = None
        should_dither = True
        if should_dither:
            bw = im.convert("1", dither=Image.FLOYDSTEINBERG)
        else:
            bw = im.point(lambda x: 0 if x < 128 else 255, '1')

        return bw

    def update_preview(self):
        # Update preview image
        im = self.generate_image()

        qi = ImageQt(im)
        scene = QGraphicsScene(self)
        pixmap = QPixmap.fromImage(qi)
        item = QGraphicsPixmapItem(pixmap)
        scene.addItem(item)
        self.pic.setScene(scene)

        # Scroll to match vertical position of cursor
        # TODO: excessively long lines break this
        cursor_line = self.edit.textCursor().block().firstLineNumber()
        line_count = self.edit.document().blockCount()
        scroll_height = self.pic.verticalScrollBar().maximum()
        approx_cursor_pos = int(cursor_line / line_count * scroll_height)
        self.pic.verticalScrollBar().setValue(approx_cursor_pos)

    # Greets the user
    def save_image(self):
        im = self.generate_image()

        buf = io.BytesIO()
        im.save(buf, format='PPM')
        image_buffer = buf.getvalue()

        loop = asyncio.get_event_loop()

        async def coroutine():
            try:
                await catte.run('60:16:55:C1:AE:10', image_buffer, 128, 25)
            except:
                print('Error connecting.')

        loop.run_until_complete(coroutine())


if __name__ == '__main__':
    # Create the Qt Application
    app = QApplication(sys.argv)
    # Create and show the form
    main = Main()
    main.show()
    # Run the main Qt loop
    sys.exit(app.exec())
