from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWebEngineWidgets import QWebEngineView

app = QApplication([])
view = QWebEngineView()

url = QUrl.fromLocalFile("C:/Users/hakaton2023/core/res/player.html")
view.load(url)

view.show()
app.exec_()
