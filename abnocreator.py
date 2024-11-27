import sys
import os
import random
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QListWidget, QLabel, QFileDialog, QRubberBand
from PyQt5.QtGui import QPixmap, QPainter, QColor, QPen, QLinearGradient, QImage
from PyQt5.QtCore import Qt, QRect, QPoint, QSize

class ImageDefectApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Defect Synthesis Tool')
        self.setGeometry(100, 100, 1024, 768)
        self.defects_directory = 'defects'
        self.current_image = None
        self.selection_start_point = None
        self.selection_end_point = None
        self.is_selecting_area = False
        self.selection_rect = QRect()
        self.rubber_band = None
        self.drawing_scratch = False
        self.initUI()

    def initUI(self):
        # Image display label
        self.imageLabel = QLabel(self)
        self.imageLabel.setGeometry(10, 10, 640, 480)
        self.imageLabel.setStyleSheet("background-color: white;")

        # Add buttons
        self.loadButton = QPushButton('Load Image', self)
        self.loadButton.setGeometry(660, 10, 150, 30)
        self.loadButton.clicked.connect(self.load_image)

        self.selectAreaButton = QPushButton('Select Area', self)
        self.selectAreaButton.setGeometry(660, 50, 150, 30)
        self.selectAreaButton.clicked.connect(self.toggle_selection_mode)

        self.manualAddButton = QPushButton('Manual Add Defect', self)
        self.manualAddButton.setGeometry(660, 90, 150, 30)
        self.manualAddButton.clicked.connect(self.start_manual_add_defect)

        self.autoAddButton = QPushButton('Auto Add Defect', self)
        self.autoAddButton.setGeometry(660, 130, 150, 30)
        self.autoAddButton.clicked.connect(self.auto_add_defect)

        self.saveButton = QPushButton('Save Image', self)
        self.saveButton.setGeometry(660, 170, 150, 30)
        self.saveButton.clicked.connect(self.save_image)

        self.quitButton = QPushButton('Quit', self)
        self.quitButton.setGeometry(660, 210, 150, 30)
        self.quitButton.clicked.connect(self.close)

        # Defect sample list
        self.defectListWidget = QListWidget(self)
        self.defectListWidget.setGeometry(660, 250, 150, 200)
        self.load_defects()

    def load_image(self):
        fname, _ = QFileDialog.getOpenFileName(self, 'Open file', './', "Image files (*.jpg *.png)")
        if fname:
            self.current_image = QPixmap(fname)
            self.imageLabel.setPixmap(self.current_image)

    def load_defects(self):
        for defect_name in os.listdir(self.defects_directory):
            if defect_name.endswith(('.jpg', '.png')):
                self.defectListWidget.addItem(defect_name)

    def toggle_selection_mode(self):
        self.is_selecting_area = not self.is_selecting_area
        if self.is_selecting_area:
            self.selectAreaButton.setText('Select Area: ON')
            self.rubber_band = QRubberBand(QRubberBand.Rectangle, self)
        else:
            self.selectAreaButton.setText('Select Area: OFF')
            if self.rubber_band:
                self.rubber_band.hide()
                self.rubber_band = None
            self.selection_rect = QRect()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.is_selecting_area and self.imageLabel.underMouse():
            self.selection_start_point = event.pos() - self.imageLabel.pos()
            if not self.rubber_band:
                self.rubber_band = QRubberBand(QRubberBand.Rectangle, self.imageLabel)
            self.rubber_band.setGeometry(QRect(self.selection_start_point, QSize()))
            self.rubber_band.show()
        elif event.button() == Qt.LeftButton and self.drawing_scratch:
            # Start drawing scratch
            self.scratch_start_point = event.pos() - self.imageLabel.pos()
            # Get background pattern at start point
            self.scratch_pattern = self.get_background_pattern(self.scratch_start_point, 10)

    def mouseMoveEvent(self, event):
        if self.is_selecting_area and self.selection_start_point:
            current_point = event.pos() - self.imageLabel.pos()
            self.selection_rect = QRect(self.selection_start_point, current_point).normalized()
            if self.rubber_band:
                self.rubber_band.setGeometry(self.selection_rect)
                self.rubber_band.show()
        elif self.drawing_scratch and hasattr(self, 'scratch_start_point'):
            # Draw scratch line
            current_point = event.pos() - self.imageLabel.pos()
            painter = QPainter(self.current_image)
            pen = QPen(self.scratch_pattern, 3, Qt.SolidLine)  # Use background pattern for scratch
            painter.setPen(pen)
            painter.drawLine(self.scratch_start_point, current_point)
            painter.end()
            self.scratch_start_point = current_point
            self.imageLabel.setPixmap(self.current_image)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.is_selecting_area:
            self.selection_end_point = event.pos() - self.imageLabel.pos()
            self.selection_rect = QRect(self.selection_start_point, self.selection_end_point).normalized()
            self.is_selecting_area = False
            self.selectAreaButton.setText('Select Area: OFF')
            # Hide the selection after releasing the mouse button
            if self.rubber_band:
                self.rubber_band.hide()
                self.rubber_band = None
        elif event.button() == Qt.RightButton and self.drawing_scratch:
            # End drawing scratch
            self.drawing_scratch = False

    def start_manual_add_defect(self):
        if self.current_image and self.selection_rect.isValid():
            self.drawing_scratch = True
        else:
            print("Select a valid area before adding manually.")

    def auto_add_defect(self):
        if self.current_image and self.defectListWidget.currentItem():
            defect_name = self.defectListWidget.currentItem().text()
            defect_path = os.path.join(self.defects_directory, defect_name)
            defect_image = QPixmap(defect_path)
            if self.selection_rect.isValid():
                self.apply_defect_in_selection_area(defect_image.scaledToWidth(int(self.selection_rect.width() * 0.5)))
                # Clear selection after adding defect
                if self.rubber_band:
                    self.rubber_band.hide()
                    self.rubber_band = None
                self.selection_rect = QRect()
            else:
                self.apply_defect_at_random_position(defect_image.scaledToWidth(int(self.current_image.width() * 0.02)))

    def apply_defect_in_selection_area(self, defect_image):
        if not self.selection_rect.isValid():
            print("Invalid selection area.")
            return

        # Get the background color at the selection area's top-left corner
        bg_color = self.get_background_color(self.selection_rect.topLeft())
        defect_image = self.adjust_defect_color(defect_image, bg_color)

        x = self.selection_rect.x() + random.randint(0, max(1, self.selection_rect.width() - defect_image.width()))
        y = self.selection_rect.y() + random.randint(0, max(1, self.selection_rect.height() - defect_image.height()))

        painter = QPainter(self.current_image)
        painter.drawPixmap(QPoint(x, y), defect_image)
        painter.end()
        self.imageLabel.setPixmap(self.current_image)

    def apply_defect_at_random_position(self, defect_image):
        if not self.current_image:
            return

        # Get a random position
        x = random.randint(0, max(1, self.current_image.width() - defect_image.width()))
        y = random.randint(0, max(1, self.current_image.height() - defect_image.height()))

        # Get the background color at the random position
        bg_color = self.get_background_color(QPoint(x, y))
        defect_image = self.adjust_defect_color(defect_image, bg_color)

        painter = QPainter(self.current_image)
        painter.drawPixmap(QPoint(x, y), defect_image)
        painter.end()
        self.imageLabel.setPixmap(self.current_image)

    def get_background_color(self, position):
        if not self.current_image:
            return QColor(255, 255, 255)  # Default to white

        image = self.current_image.toImage()
        color = image.pixelColor(position)
        return color

    def get_background_pattern(self, position, radius):
        if not self.current_image:
            return QColor(255, 255, 255)  # Default to white

        image = self.current_image.toImage()
        colors = []
        for x in range(max(0, position.x() - radius), min(image.width(), position.x() + radius)):
            for y in range(max(0, position.y() - radius), min(image.height(), position.y() + radius)):
                colors.append(image.pixelColor(x, y))

        # Average the colors to get a pattern color
        avg_red = sum([c.red() for c in colors]) // len(colors)
        avg_green = sum([c.green() for c in colors]) // len(colors)
        avg_blue = sum([c.blue() for c in colors]) // len(colors)

        return QColor(avg_red, avg_green, avg_blue)

    def adjust_defect_color(self, defect_image, target_color):
        image = defect_image.toImage().convertToFormat(QImage.Format_ARGB32)
        for x in range(image.width()):
            for y in range(image.height()):
                pixel_color = image.pixelColor(x, y)
                if pixel_color.alpha() > 0:  # Only adjust non-transparent pixels
                    blended_color = QColor(
                        (pixel_color.red() + target_color.red()) // 2,
                        (pixel_color.green() + target_color.green()) // 2,
                        (pixel_color.blue() + target_color.blue()) // 2,
                        pixel_color.alpha()
                    )
                    image.setPixelColor(x, y, blended_color)
        return QPixmap.fromImage(image)

    def save_image(self):
        if self.current_image:
            # Save image
            fname, _ = QFileDialog.getSaveFileName(self, 'Save file', './', "Image files (*.jpg *.png)")
            if fname:
                self.current_image.save(fname)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ImageDefectApp()
    ex.show()
    sys.exit(app.exec_())
