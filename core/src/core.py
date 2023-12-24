import math
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
        self.data_buffer: List[typing.Tuple[float, float]] = []
        self.read_data_stop: bool = False
        self.resistence: List[float] = None

        self.scanner: Scanner = Scanner([SensorFamily.LEBrainBit])
        self.current_sensors_info_list: List[SensorInfo] = []
        self.current_sensor: Sensor = None

        self.is_ready_current_sensor: bool = False

        # section start settings
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
        # section end settings

    # section start data reading
    def start_read_data(self):
        def on_brain_bit_signal_data_received(sensor, data):
            channels: List[RawChannels] = []

            for d in data:
                channels.append(RawChannels(d.T3 - d.O1, d.T4 - d.O2))

            self.emotions.push_data(channels)
            self.emotions.process_data_arr()

            if not self.emotions.calibration_finished():
                pass
                print(f"\rCalibration A:{self.emotions.is_both_sides_artifacted()} P:{self.emotions.get_calibration_percents()}",
                      end="")
            else:
                if len(self.data_buffer) == 0:
                    print("\nCalibration ended")
                if not self.emotions.is_artifacted_sequence():
                    mental_data = self.emotions.read_mental_data_arr()
                    for d in mental_data:
                        self.data_buffer.append((d.rel_relaxation, d.rel_attention))
                        print(f"\rA:{d.rel_attention:<5}  R:{d.rel_relaxation:<5s}", end='')

        self.current_sensor.signalDataReceived = on_brain_bit_signal_data_received

        start_separate_thread(self.current_sensor.exec_command(SensorCommand.StartSignal))

    def stop_read_data(self):
        self.current_sensor.signalDataReceived = None
        start_separate_thread(self.current_sensor.exec_command(SensorCommand.StopSignal))

    def get_data(self) -> List[typing.Tuple[float, float]]:
        return self.data_buffer

    def flush_data(self):
        self.data_buffer = []

    # section end data reading
    # section start sensors management

    def on_sensors_info_list_changed(self, scanner: Scanner, sensors_info: List[SensorInfo]):
        self.current_sensors_info_list = sensors_info

    def start_sensors_search(self):
        self.scanner.sensorsChanged = self.on_sensors_info_list_changed
        self.scanner.start()

    def stop_sensors_search(self):
        self.scanner.sensorsChanged = None
        self.scanner.stop()

    def get_sensors_info_list(self) -> List[SensorInfo]:
        return self.current_sensors_info_list

    def connect_to_sensor(self, sensor: int) -> Sensor:
        if self.current_sensor is not None:
            self.current_sensor.disconnect()

        s = self.scanner.create_sensor(self.current_sensors_info_list[sensor] if type(sensor) == int else sensor)
        s.batteryChanged = self.on_current_sensor_battery_state_changed
        self.current_sensor = s
        return s

    def disconnect_from_sensor(self):
        if self.current_sensor is not None:
            self.current_sensor.disconnect()
            self.current_sensor = None

    def get_current_sensor_resistence(self):
        self.start_get_current_sensor_resistence()

    def start_get_current_sensor_resistence(self):
        def target():
            def on_brain_bit_resist_data_received(sensor: Sensor, data: BrainBitResistData):
                if not any(map(math.isinf, [data.O1, data.O2, data.T3, data.T4])):
                    print(*map(math.ceil, [data.O1, data.O2, data.T3, data.T4]))
                    start_separate_thread(self.stop_get_current_sensor_resistence)
                    self.is_ready_current_sensor = True

            self.current_sensor.resistDataReceived = on_brain_bit_resist_data_received
            self.current_sensor.exec_command(SensorCommand.StartResist)

        self.is_ready_current_sensor = False
        start_separate_thread(target)

    def stop_get_current_sensor_resistence(self):
        print("stop")
        self.current_sensor.resistDataReceived = None
        self.current_sensor.exec_command(SensorCommand.StopResist)

    def on_current_sensor_battery_state_changed(self, sensor: Sensor, battery: int):
        pass

    def get_current_sensor_parameters(self) -> List[ParameterInfo]:
        return self.current_sensor.parameters

    def get_current_sensor_commands(self) -> List[SensorCommand]:
        return self.current_sensor.commands

    def start_calibration(self):
        self.emotions.start_calibration()

    # section end sensors management

    def start(self):
        self.start_read_data()

    def __del__(self):
        self.disconnect_from_sensor()
        del self.scanner
        del self.emotions


if __name__ == '__main__':
    def test():
        global core

        core.emotion_detector.start_sensors_search()
        time.sleep(5)
        core.emotion_detector.stop_sensors_search()

        for si in core.emotion_detector.get_sensors_info_list():
            if si.SerialNumber == "132007":
                core.emotion_detector.connect_to_sensor(si)
        else:
            if core.emotion_detector.current_sensor is None:
                print("no sensor with serial number 132007 founded")
                return

        core.emotion_detector.get_current_sensor_resistence()

        input("1\n")
        core.emotion_detector.start_calibration()
        core.emotion_detector.start_read_data()
        input("2\n")
        core.emotion_detector.stop_read_data()
        del core

    core = Core()

    commands: typing.Dict[str, typing.Callable] = {
        "strsr": lambda d: core.emotion_detector.start_sensors_search(),
        "stpsr": lambda d: core.emotion_detector.stop_sensors_search(),
        "list": lambda d: print(core.emotion_detector.get_sensors_info_list()),
        "cnt": lambda d: core.emotion_detector.connect_to_sensor(int(d[0])),
        "rst": lambda d: core.emotion_detector.get_current_sensor_resistence(),
        "start": lambda d: test(),
        "btr": lambda d: print(core.emotion_detector.current_sensor.batt_power),
    }

    while True:
        command = input(">>> ")
        command.replace("\n", "")

        if command == "exit":
            break

        cmd = command.split(" ")
        if len(cmd) > 0 and cmd[0] in commands.keys():
            commands[cmd[0]](cmd[1:] if len(cmd) > 1 else [])
        else:
            print("illegal command")
