import json


class MusicList:
    def __init__(self):
        self.data = None
        self.file: str = "user_data.json"

    def read(self):
        self.data = json.load(open(self.file))

    def write(self):
        json.dump(self.data, open(self.file))

    def push_track(self, file: str, name: str, type: int):
        self.data[name].append({"name": name, "type": type, "file": file})