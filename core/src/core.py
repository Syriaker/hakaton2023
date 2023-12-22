from em_st_artifacts.emotional_math import *
from neurosdk.scanner import *


class Core:
    def __init__(self):
        self.emotion_detector = EmotionDetector()

def on_sensor_found(scanner: Scanner, sensor: Sensor):
    print(scanner, sensor)

class EmotionDetector:
    def __init__(self):
        # settings start
        self.scanner: Scanner = Scanner([SensorFamily.LEBrainBit])
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

    def search_device(self):
        self.scanner.start()
        self.scanner.sensorsChanged = on_sensor_found

        self.scanner.sensors()

    def calibrate(self):
        # resistance < 2e6
        pass

    def __del__(self):
        del self.emotions


