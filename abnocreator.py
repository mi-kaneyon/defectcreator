from PyQt5.QtGui import QColor
from PyQt5.QtGui import QLinearGradient
import sys
import os
import random
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QListWidget, QLabel, QFileDialog
from PyQt5.QtGui import QPixmap, QImage, QPainter, QPen
from PyQt5.QtCore import Qt, QRect, QPoint

class ImageDefectApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.selection_start_point = None
        self.selection_end_point = None
        self.is_selecting_area = False
        super().__init__()
        self.setWindowTitle('Defect Synthesis Tool')
        self.setGeometry(100, 100, 1024, 768)
        self.defects_directory = 'defects'
        self.current_image = None
        self.selection_started = False
        self.selection_rect = QRect()
        self.initUI()
    


    def apply_transparency_gradient(self, pixmap):
        if pixmap.isNull():
            print("Error: QPixmap is null.")
            return pixmap

        # Create a new QPixmap to hold the gradient mask with the same size as the defect image
        mask = QPixmap(pixmap.size())
        mask.fill(Qt.transparent)

        # Start painting the gradient on the mask
        painter = QPainter(mask)
        if not painter.isActive():
            print("Error: Unable to activate QPainter.")
            return pixmap

        # Define the gradient from transparent at the edges to opaque at the center
        gradient = QLinearGradient(0, 0, mask.width(), mask.height())
        gradient.setColorAt(0.0, QColor(0, 0, 0, 0))
        gradient.setColorAt(0.2, QColor(0, 0, 0, 128))
        gradient.setColorAt(0.5, QColor(0, 0, 0, 255))
        gradient.setColorAt(0.8, QColor(0, 0, 0, 128))
        gradient.setColorAt(1.0, QColor(0, 0, 0, 0))
        painter.setBrush(gradient)
        painter.drawRect(0, 0, mask.width(), mask.height())
        painter.end()

        # Apply the mask to the pixmap
        painter = QPainter(pixmap)
        if not painter.isActive():
            print("Error: Unable to activate QPainter.")
            return pixmap

        painter.setCompositionMode(QPainter.CompositionMode_DestinationIn)
        painter.drawPixmap(0, 0, mask)
        painter.end()

        return pixmap

    def initUI(self):
        self.imageLabel = QLabel(self)
        self.imageLabel.setGeometry(10, 10, 640, 480)
        self.imageLabel.setStyleSheet("background-color: white;")
        self.loadButton = QPushButton('Load Image', self)
        self.loadButton.setGeometry(660, 10, 150, 30)
        self.loadButton.clicked.connect(self.load_image)

        self.addButton = QPushButton('Add Defect Manually', self)
        self.addButton.setGeometry(660, 50, 150, 30)
        self.addButton.clicked.connect(self.add_defect_manually)

        self.autoButton = QPushButton('Auto Mode', self)
        self.autoButton.setGeometry(660, 90, 150, 30)
        self.autoButton.clicked.connect(self.add_defect_automatically)

        self.saveButton = QPushButton('Save Image', self)
        self.saveButton.setGeometry(660, 130, 150, 30)
        self.saveButton.clicked.connect(self.save_image)

        self.defectListWidget = QListWidget(self)
        self.defectListWidget.setGeometry(660, 200, 150, 200)
        self.load_defects()
                # EXIT Button
        self.exitButton = QPushButton('Exit', self)
        self.exitButton.setGeometry(660, 170, 150, 30)  # Adjust placement as needed
        self.exitButton.clicked.connect(self.close)
                # 範囲指定ボタンの追加
        self.select_area_button = QPushButton('Select Area', self)
        self.select_area_button.clicked.connect(self.toggle_selection_mode)


    def load_image(self):
        fname, _ = QFileDialog.getOpenFileName(self, 'Open file', './', "Image files (*.jpg *.png)")
        if fname:
            self.current_image = QPixmap(fname)
            self.imageLabel.setPixmap(self.current_image)

    def load_defects(self):
        for defect_name in os.listdir(self.defects_directory):
            if defect_name.endswith(('.jpg', '.png')):
                self.defectListWidget.addItem(defect_name)

    def add_defect_manually(self):
        # This function will be triggered when the user wants to manually add a defect.
        # The actual defect application logic will be handled in the mousePressEvent.
        self.imageLabel.setFocus()

    def add_defect_automatically(self):
        if self.current_image and self.defectListWidget.currentItem():
            defect_name = self.defectListWidget.currentItem().text()
            defect_path = os.path.join(self.defects_directory, defect_name)
            defect_image = QPixmap(defect_path)
            self.apply_defect_at_random_position(defect_image.scaledToWidth(int(self.current_image.width() * 0.02)))

    def save_image(self):
        if self.current_image:
            fname, _ = QFileDialog.getSaveFileName(self, 'Save file', './', "Image files (*.jpg *.png)")
            if fname:
                self.current_image.save(fname)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.imageLabel.underMouse():
            self.apply_defect_at_position(event.pos())

    def apply_defect_at_position(self, position):
        if self.current_image and self.defectListWidget.currentItem():
            defect_name = self.defectListWidget.currentItem().text()
            defect_path = os.path.join(self.defects_directory, defect_name)
            defect_image = QPixmap(defect_path)
        # Scale the defect image to be 5% of the current image width
            painter = QPainter(self.current_image)
            pixmap_with_transparency = self.apply_transparency_gradient(defect_image)
            painter.drawPixmap(position, defect_image.scaledToWidth(int(self.current_image.width() * 0.02)))
            painter.end()
            self.imageLabel.setPixmap(self.current_image)

    def apply_defect_at_random_position(self, defect_image):
        x = random.randint(0, self.current_image.width() - defect_image.width())
        y = random.randint(0, self.current_image.height() - defect_image.height())
        painter = QPainter(self.current_image)
        pixmap_with_transparency = self.apply_transparency_gradient(defect_image)
        painter.drawPixmap(QPoint(x, y), defect_image)
        painter.end()
        self.imageLabel.setPixmap(self.current_image)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ImageDefectApp()
    ex.show()
    sys.exit(app.exec_())
