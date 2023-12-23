from PyQt5.QtCore import QEvent
from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui, QtWidgets
from pygame import mixer
import sys
import icon
import json
import core
import time


class Player():
    def choose_file(self):
        global path
        filename = QFileDialog.getOpenFileName(filter=('*.mp3'))
        path = filename[0]
        mixer.music.load(path)
        mixer.music.play()
        self.core.emotion_detector.read_data()
        #self.lenght = mixer.music.get_pos()
        self.core.emotion_detector.stop_read_data()
        if (self.core.emotion_detector.get_data())[0] > (self.core.emotion_detector.get_data())[1]:
            print('релакс')
        else:
            print('концентрация')


    def pauseMusic(self):
        if not self.paused:
            mixer.music.pause()
            self.paused = True
        else:
            mixer.music.unpause()
            self.paused = False
        self.core.emotion_detector.stop_read_data()
        print(self.core.emotion_detector.get_data())



    def volume_change(self):
        volume = self.ui.music_slider.value() / 100
        mixer.music.set_volume(volume)
    def analysis(self):
        print("ку")

    def __init__(self):
        self.core = core.Core()
        app = QtWidgets.QApplication(sys.argv)

        self.core.emotion_detector.start_sensors_search()
        time.sleep(10)
        self.core.emotion_detector.stop_sensors_search()
        for si in self.core.emotion_detector.get_sensors_info_list():
            if si.SerialNumber == "132007":
                self.core.emotion_detector.connect_to_sensor(si)
        else:
            if self.core.emotion_detector.current_sensor is None:
                print("no sensor with id 132007")
                sys.exit(1)

        self.core.emotion_detector.get_current_sensor_resistence()

        Form = QtWidgets.QWidget()
        mixer.init()
        self.paused = False
        self.ui = icon.Ui_Form()
        self.ui.setupUi(Form)
        self.ui.add_music.clicked.connect(self.choose_file)
        self.ui.pauseButton.clicked.connect(self.pauseMusic)
        self.ui.music_slider.setValue(100)
        self.ui.music_slider.valueChanged.connect(self.volume_change)
        Form.show()

        ec = app.exec_()
        del self.core
        sys.exit(ec)




Player()
