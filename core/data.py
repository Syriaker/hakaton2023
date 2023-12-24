import json
import pathlib


class MusicList:
    def __init__(self):
        self.data = None
        self.file: str = "user_data.json"

    def read(self):

        if not pathlib.Path(self.file).exists():
            self.data = {"tracks": []}
        else:
            file = open(self.file, "r")
            self.data = json.load(file)
            file.close()
        print(self.data)

    def write(self):
        file = open(self.file, "w")
        json.dump(self.data, file)
        file.close()

    def push_track(self, file: str, name: str, track_type: int):
        if self.data == None:
            self.data = {"tracks": []}
        self.data["tracks"].append({"name": name, "file": file, "type": track_type})

if __name__ == '__main__':
    lst = MusicList()

    lst.read()
    lst.push_track("soviet anthem", "svtatm.mp3", 1)
    lst.write()