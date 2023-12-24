import json


class MusicList:
    def __init__(self):
        self.data = None
        self.file: str = "user_data.json"

    def read(self):
        file = open(self.file, "w")
        self.data = json.load(file)
        file.close()


    def write(self):
        file = open(self.file, "w")
        json.dump(self.data, file)
        file.close()

    def push_track(self, file: str, name: str,