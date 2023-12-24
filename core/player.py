from PyQt5.QtWidgets import *
from PyQt5 import QtWidgets
from pygame import mixer
import sys
import icon
import core


class Player():
    def __init__(self):
        def choose_file():
            global path
            filename = QFileDialog.getOpenFileName(filter=('*.mp3'))
            path = filename[0]
            mixer.music.load(path)
            mixer.music.play()
            print(self.core.emotion_detector.current_sensor)
            self.core.emotion_detector.flush_data()
            self.core.emotion_detector.start_read_data()

        def pause_music():
            if not self.paused:
                mixer.music.pause()
                self.paused = True
                self.core.emotion_detector.stop_read_data()
                print(self.core.emotion_detector.get_data())
            else:
                mixer.music.unpause()
                self.core.emotion_detector.start_read_data()
                self.paused = False

        def volume_change():
            volume = self.ui.music_slider.value() / 100
            mixer.music.set_volume(volume)

        def analysis():
            print("ку")

        def connect():
            print("Connecting")
            b = False
            while not b:
                for si in self.core.emotion_detector.get_sensors_info_list():
                    if si.SerialNumber == "132007":
                        self.core.emotion_detector.connect_to_sensor(si)
                        b = True
                        print("Connected")

            self.core.emotion_detector.get_current_sensor_resistence()

        self.core = core.Core()
        self.core.emotion_detector.start_sensors_search()
        mixer.init()
        self.app = QtWidgets.QApplication(sys.argv)
        Form = QtWidgets.QWidget()

        self.paused = False
        self.ui = icon.Ui_Form()

        self.ui.setupUi(Form)
        self.ui.add_music.clicked.connect(choose_file)

        self.ui.pausebutton.clicked.connect(pause_music)
        self.ui.music_slider.setValue(100)

        self.ui.B_button.clicked.connect(connect)

        self.ui.music_slider.valueChanged.connect(volume_change)
        Form.show()

        ec = self.app.exec_()
        del self.core
        sys.exit(ec)

Player()
