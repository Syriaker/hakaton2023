import sys, os
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtWidgets import *
from pygame import mixer
from pathlib import Path
paused = False
app = QApplication([])
main_win = QWidget()
layout = QGridLayout()
main_win.setLayout(layout)
file_list = QListWidget()
lbl = QLabel()
file_choice = QPushButton('Выбрать файл')
play = QPushButton('Начать трек')
pause = QPushButton('▋▋')
main_win.resize(800, 400)
main_win.setWindowTitle('Player')
mixer.init()
def choosefile():
    global path
    filename = QFileDialog.getOpenFileName()
    path = filename[0]
def playMusic():
    global path
    mixer.music.load(path)
    mixer.music.play()
def pauseMusic():
    global paused
    if not paused:
        mixer.music.pause()
        paused = True
        pause.setText('►')
    else:
        mixer.music.unpause()
        paused = False
        pause.setText('▋▋')

file_choice.clicked.connect(choosefile)
play.clicked.connect(playMusic)
pause.clicked.connect(pauseMusic)

main_win.show()
app.exec_()