import json
import os.path
from glob import glob
from tkinter.filedialog import askopenfilename
from dataclasses import dataclass
from datetime import datetime
from turtledemo.penrose import start


@dataclass
class Song:
    title: str
    artist: str
    ms_played: int
    listens_list: list

class MusicReader:
    def __init__(self, url):
        self.url = url
        self.pages = glob(f'{url}/StreamingHistory_music_*')
        self.songs = self.get_songs()

    def get_songs(self):
        songs = {}
        for page in self.pages:
            with open(page, 'r', encoding='utf-8') as f:
                data = json.load(f)

                for entry in data:
                    # check if song is not already in dictionary
                    if entry['trackName'] not in songs:
                        # create song
                        songs[entry['trackName']] = Song(entry['trackName'],entry['artistName'],entry['msPlayed'],[[
                            entry['msPlayed'],
                            datetime.strptime(entry['endTime'], '%Y-%m-%d %H:%M')
                        ]])
                    else:
                        songs[entry['trackName']].ms_played += entry['msPlayed']
                        songs[entry['trackName']].listens_list.append([
                            entry['msPlayed'],
                            datetime.strptime(entry['endTime'], '%Y-%m-%d %H:%M')
                        ])

        return songs


def main():
    random_file = askopenfilename(title='Open any JSON file from the Spotify Data Directory', filetypes=[('Any Spotify Data Json File', '.json')])
    spotify_data_dir = os.path.dirname(random_file)

    reader = MusicReader(spotify_data_dir)

    start_month = 8
    organized_listening = {}

    for title in reader.songs:
        song = reader.songs[title]
        for listen in song.listens_list:
            ms = listen[0] # milliseconds
            dt = listen[1] # datetime
            year = dt.year
            month = dt.month

            key = f'{year}-{month}'
            if key not in organized_listening:
                organized_listening[key] = [[title, ms]]
            else:
                organized_listening[key].append([title, ms])

    for month in range(0,13):
        current_year = 2024
        current_month = start_month + month

        # Balance into 2025
        if current_month > 12:
            current_month -= 12
            current_year = 2025

        monthly_song_summed = {}
        for listen in organized_listening[f'{current_year}-{current_month}']:
            title = listen[0]
            ms = listen[1]

            if title not in monthly_song_summed:
                monthly_song_summed[title] = ms
            else:
                monthly_song_summed[title] += ms

        most_listend_to = max(monthly_song_summed, key=monthly_song_summed.get)
        print(f'{current_year}-{current_month}: {most_listend_to}')



if __name__ == '__main__':
    main()