from __future__ import annotations

import typing
from threading import Thread
from em_st_artifacts.emotional_math import *
from neurosdk.scanner import *

class Core:
    def __init__(self):
        self.emotion_detector = EmotionDetector()

    def __del__(self):
        del self.emotion_detector

class EmotionDetector:
    def __init__(self):
        self.scanner: Scanner = Scanner([SensorFamily.LEBrainBit])
        self.current_sensors_info_list: List[SensorInfo] = None
        self.current_sensor: Sensor = None

        # settings start
        self.math_lib_settings: MathLibSetting = MathLibSetting(sampling_rate=250,
                                                                process_win_freq=25,
                                                                fft_window=1000,
                                                                n_first_sec_skipped=4,
                                                                bipolar_mode=False,
                                                                channels_number=4,
                                                                channel_for_analysis=3)

        self.artifact_detect_setting: ArtifactDetectSetting = ArtifactDetectSetting(hanning_win_spectrum=True,
                                                                                    num_wins_for_quality_avg=125)

        self.short_artifact_detect_setting: ShortArtifactDetectSetting = ShortArtifactDetectSetting(
            ampl_art_extremum_border=25)

        self.mental_amd_spectral_settings: MentalAndSpectralSetting = MentalAndSpectralSetting()
        # settings end

        # create emotion math
        self.emotions: EmotionalMath = EmotionalMath(self.math_lib_settings, self.artifact_detect_setting,
                                                     self.short_artifact_detect_setting,
                                                     self.mental_amd_spectral_settings)

    def read_data(self):
        pass

    def on_sensors_info_list_changed(self, scanner: Scanner, sensors_info: List[Sensor]):
        self.current_sensors_info_list = sensors_info

    def start_sensors_search(self):
        self.scanner.sensorsChanged = self.on_sensors_info_list_changed
        self.scanner.start()

    def stop_sensors_search(self):
        self.scanner.sensorsChanged = None
        self.scanner.stop()

    def get_sensors_info_list(self) -> List[SensorInfo]:
        return self.current_sensors_info_list

    def connect_to_sensor(self, sensor: int | Sensor) -> Sensor | typing.NoReturn:
        if self.current_sensor is not None:
            self.current_sensor.disconnect()

        if type(sensor) == int:
            s = self.scanner.create_sensor(self.current_sensors_info_list[sensor])
            s.batteryChanged = self.on_current_sensor_battery_state_changed
            return s
        elif type(sensor) == Sensor:
            Thread(target=lambda: sensor.connect()).start()

    def disconnect_from_sensor(self):
        if self.current_sensor is not None:
            self.current_sensor.disconnect()
            self.current_sensor = None

    def on_current_sensor_battery_state_changed(self, battery: int):
        pass

    def get_current_sensor_parameter(self) -> List[ParameterInfo]:
        return self.current_sensor.parameters

    def get_current_sensor_command(self):
        return self.current_sensor.commands

    def calibrate(self):
        # resistance < 2e6
        pass

    def __del__(self):
        del self.scanner
        del self.emotions