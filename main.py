import json
import glob
import sys
import os.path
from datetime import datetime
from dataclasses import dataclass
from tkinter.filedialog import askopenfilename

@dataclass
class Song:
    title: str
    artist: str
    ms_played: int
    listens_list: list

@dataclass
class Artist:
    name: str
    ms_played: int
    songs_played: int
    songs: list

class TimeFormater:
    def ms_to_hmsms(self, ms):
        hours = ms // 3_600_000
        ms_remaining = ms % 3_600_000
        minutes = ms_remaining // 60_000
        ms_remaining = ms_remaining % 60_000
        seconds = ms_remaining // 1_000
        milliseconds = ms_remaining % 1_000
        return f"{hours}h {minutes}m {seconds}s {milliseconds}ms"

class StreamingHistoryMusicReader:
    def __init__(self, url):
        self.url = url
        self.page = 0
        self.pages = glob.glob(f'{url}/StreamingHistory_music_*')
        self.songs = self.get_songs()
        self.artists = self.get_artists()

    def get_songs(self):
        songs = {}
        for page in self.pages:
            with open(page, 'r', encoding='utf-8') as f:
                data = json.load(f)

                for entry in data:
                    if entry['trackName'] not in songs:
                       songs[entry['trackName']] = Song(
                           entry['trackName'],
                           entry['artistName'],
                           entry['msPlayed'],
                           [
                           [
                               entry['msPlayed'],
                               datetime.strptime(entry['endTime'], "%Y-%m-%d %H:%M")
                           ]
                           ])
                    else:
                        songs[entry['trackName']].ms_played += entry['msPlayed']
                        songs[entry['trackName']].listens_list.append([
                            [
                                entry['msPlayed'],
                                datetime.strptime(entry['endTime'], "%Y-%m-%d %H:%M")
                            ]
                        ])


        return songs

    def get_artists(self):
        artists = {}
        for song in self.songs:
            track = self.songs[song]
            if track.artist not in artists:
                artists[track.artist] = Artist(
                    track.artist,
                    track.ms_played,
                    1,
                    [track]
                )
            else:
                artists[track.artist].songs_played += 1
                artists[track.artist].ms_played += track.ms_played
                artists[track.artist].songs.append(track)

        return artists

    def sort_listen_songs(self, longest: bool):
        sorted_songs = sorted(self.songs.values(), key=lambda s: s.ms_played, reverse=longest)
        return sorted_songs

    def sort_listen_artists(self, longest: bool):
        sorted_artists = sorted(self.artists.values(), key=lambda s: s.ms_played, reverse=longest)
        return sorted_artists

    def sort_most_played_artists(self, longest: bool):
        sorted_artists = sorted(self.artists.values(), key=lambda s: s.songs_played, reverse=longest)
        return sorted_artists

def main():
    print(f'Open any json file within the Spotify Data Folder')
    data_directory = os.path.dirname(askopenfilename(title="Select Spotify Data Folder", filetypes=[("Any Spotify Data Json File", ".json")]))

    music_reader = StreamingHistoryMusicReader(data_directory)
    most_played_artists = music_reader.sort_most_played_artists(True)

    for artist in most_played_artists:
        print(f"{artist.name} - {artist.songs_played} times played.")

    sys.exit(1)

if __name__ == '__main__':
    main()