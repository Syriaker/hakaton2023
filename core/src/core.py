from __future__ import annotations

import time
import typing
from threading import Thread
from em_st_artifacts.emotional_math import *
from neurosdk.scanner import *

def start_separate_thread(target: typing.Callable):
    Thread(target=target).start()

class Core:
    def __init__(self):
        self.emotion_detector = EmotionDetector()

    def __del__(self):
        del self.emotion_detector

class EmotionDetector:
    def __init__(self):
        self.data_buffer: List[List[float]] = None
        self.read_data_stop: bool = False
        self.resistence: List[float] = None

        self.scanner: Scanner = Scanner([SensorFamily.LEBrainBit])
        self.current_sensors_info_list: List[SensorInfo] = []
        self.current_sensor: Sensor = None

        # settings start
        self.math_lib_settings: MathLibSetting = MathLibSetting(sampling_rate=250,
                                                                process_win_freq=25,
                                                                fft_window=1000,
                                                                n_first_sec_skipped=4,
                                                                bipolar_mode=True,
                                                                channels_number=4,
                                                                channel_for_analysis=3)

        self.artifact_detect_setting: ArtifactDetectSetting = ArtifactDetectSetting(hanning_win_spectrum=True,
                                                                                    num_wins_for_quality_avg=125)

        self.short_artifact_detect_setting: ShortArtifactDetectSetting = ShortArtifactDetectSetting(
            ampl_art_extremum_border=25)

        self.mental_amd_spectral_settings: MentalAndSpectralSetting = MentalAndSpectralSetting()

        self.emotions: EmotionalMath = EmotionalMath(self.math_lib_settings, self.artifact_detect_setting,
                                                     self.short_artifact_detect_setting,
                                                     self.mental_amd_spectral_settings)

        self.emotions.set_calibration_length(8)
        self.emotions.set_mental_estimation_mode(False)
        self.emotions.set_skip_wins_after_artifact(10)
        self.emotions.set_zero_spect_waves(True, 0, 1, 1, 1, 0)
        self.emotions.set_spect_normalization_by_bands_width(True)
        # settings end

    def read_data(self):
        def target():
            self.read_data_stop = False

            channels: List[RawChannels] = []

            def on_brain_bit_signal_data_received(sensor, data):
                for d in data:
                    channels.append(RawChannels(d.T3 - d.O1, d.T4 - d.O2))

                self.emotions.push_data(channels)
                self.emotions.process_data_arr()

                if not self.emotions.calibration_finished():
                    print(f"Calibration A:{self.emotions.is_both_sides_artifacted()} P:{self.emotions.get_calibration_percents()}")
                else:
                    if not self.emotions.is_artifacted_sequence():
                        d = self.emotions.read_mental_data_arr()[-1]
                        self.data_buffer.append([d.rel_relaxation, d.rel_attention])
                    print(f"Data D:{self.emotions.read_mental_data_arr()[-1]} A:{self.emotions.is_artifacted_sequence()}")

            self.current_sensor.signalDataReceived = on_brain_bit_signal_data_received
            start_separate_thread(self.current_sensor.exec_command(SensorCommand.StartSignal))

            while not self.read_data_stop:
                time.sleep(0.2)

            self.current_sensor.signalDataReceived = None
            start_separate_thread(self.current_sensor.exec_command(SensorCommand.StopSignal))

        start_separate_thread(target)

    def stop_read_data(self):
        self.read_data_stop = True

    def on_sensors_info_list_changed(self, scanner: Scanner, sensors_info: List[SensorInfo]):
        print(sensors_info[-1])
        self.current_sensors_info_list = sensors_info

    def start_sensors_search(self):
        self.scanner.sensorsChanged = self.on_sensors_info_list_changed
        self.scanner.start()

    def stop_sensors_search(self):
        self.scanner.sensorsChanged = None
        self.scanner.stop()

    def get_sensors_info_list(self) -> List[SensorInfo]:
        return self.current_sensors_info_list

    def connect_to_sensor(self, sensor: int | SensorInfo) -> Sensor:
        if self.current_sensor is not None:
            self.current_sensor.disconnect()

        if type(sensor) == int:
            s = self.scanner.create_sensor(self.current_sensors_info_list[sensor])
            s.batteryChanged = self.on_current_sensor_battery_state_changed
            self.current_sensor = s
            return s
        elif type(sensor) == SensorInfo:
            s = self.scanner.create_sensor(sensor)
            s.batteryChanged = self.on_current_sensor_battery_state_changed
            self.current_sensor = s
            return s

    def disconnect_from_sensor(self):
        if self.current_sensor is not None:
            self.current_sensor.disconnect()
            self.current_sensor = None

    def get_current_sensor_resistence(self):
        def target():
            def on_brain_bit_resist_data_received(sensor: Sensor, data: BrainBitResistData):
                print(data.O1, data.O2, data.T3, data.T4)

            self.current_sensor.resistDataReceived = on_brain_bit_resist_data_received
            self.current_sensor.exec_command(SensorCommand.StartResist)
            self.start_calibration()

            time.sleep(10)

            self.current_sensor.resistDataReceived = None
            self.current_sensor.exec_command(SensorCommand.StopResist)

        start_separate_thread(target)

    def on_current_sensor_battery_state_changed(self, sensor: Sensor, battery: int):
        pass

    def get_current_sensor_parameters(self) -> List[ParameterInfo]:
        return self.current_sensor.parameters

    def get_current_sensor_commands(self):
        return self.current_sensor.commands

    def start_calibration(self):
        self.emotions.start_calibration()

    def stop_calibration(self):
        self.emotions.calibration_finished()

    def start(self):
        self.read_data()

    def get_data(self) -> List[float]:
        relax = 0
        attention = 0
        count = 0

        for datum in self.data_buffer:
            relax += datum[0]
            attention += datum[1]

        return [relax / count, attention / count]

    def flush_data(self):
        self.data_buffer = None

    def __del__(self):
        self.disconnect_from_sensor()
        del self.scanner
        del self.emotions

if __name__ == '__main__':
    core = Core()

    commands: typing.Dict[str, typing.Callable] = {
        "strsr": lambda d: core.emotion_detector.start_sensors_search(),
        "stpsr": lambda d: core.emotion_detector.stop_sensors_search(),
        "snrinflst": lambda d: print(core.emotion_detector.get_sensors_info_list()),
        "snrcnt": lambda d: core.emotion_detector.connect_to_sensor(int(d[0])),
        "start": lambda d: core.emotion_detector.start(),
        "snrrst": lambda d: core.emotion_detector.get_current_sensor_resistence(),
        "clb": lambda d: core.emotion_detector.start_calibration(),
    }

    while False:
        command = input()
        command.replace("\n", "")

        if command == "exit":
            break

        cmd = command.split(" ")
        if len(cmd) > 0 and cmd[0] in commands.keys():
            commands[cmd[0]](cmd[1:] if len(cmd) > 1 else [])
        else:
            print("illegal command")

    core.emotion_detector.start_sensors_search()
    time.sleep(10)
    core.emotion_detector.stop_sensors_search()

    for si in core.emotion_detector.get_sensors_info_list():
        if si.SerialNumber == "132007":
            core.emotion_detector.connect_to_sensor(si)
    else:
        if core.emotion_detector.current_sensor is None:
            print("no sensor with id 132007")
            sys.exit(1)

    core.emotion_detector.get_current_sensor_resistence()

    core.emotion_detector.read_data()
    input()
    core.emotion_detector.stop_read_data()

    del core