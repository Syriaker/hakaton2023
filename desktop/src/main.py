from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QLabel, QGridLayout, QWidget, qApp, QAction, QPushButton
from PyQt5.QtCore import QSize


class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)

        self.setMinimumSize(QSize(480, 320))
        self.setWindowTitle("Hello world!!!")
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        def hello():
            print('hello')

        grid_layout = QGridLayout(self)
        central_widget.setLayout(grid_layout)

        title = QLabel("Hello World on the PyQt5", self)
        button = QPushButton(hello())
        title.setAlignment(QtCore.Qt.AlignCenter)
        grid_layout.addWidget(button, 0, 0)
        grid_layout.addWidget(title, 0, 0)

        exit_action = QAction("&Exit", self)  #
        exit_action.setShortcut('Ctrl+Q')

        exit_action.triggered.connect(qApp.quit)

        file_menu = self.menuBar()
        file_menu.addAction(exit_action)



if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec())
