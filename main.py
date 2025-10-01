import json
import glob
import sys
import os.path
import requests
from tqdm import tqdm
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

class BColors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class TimeFormater:
    def ms_to_hmsms(self, ms):
        hours = ms // 3_600_000
        ms_remaining = ms % 3_600_000
        minutes = ms_remaining // 60_000
        ms_remaining = ms_remaining % 60_000
        seconds = ms_remaining // 1_000
        milliseconds = ms_remaining % 1_000
        return f'{hours}h {minutes}m {seconds}s {milliseconds}ms'

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
                               datetime.strptime(entry['endTime'], '%Y-%m-%d %H:%M')
                           ]
                           ])
                    else:
                        songs[entry['trackName']].ms_played += entry['msPlayed']
                        songs[entry['trackName']].listens_list.append([
                            [
                                entry['msPlayed'],
                                datetime.strptime(entry['endTime'], '%Y-%m-%d %H:%M')
                            ]
                        ])


        return songs

    def get_artists(self):
        artists = {}
        for song in tqdm(self.songs):
            track = self.songs[song]
            if track.artist not in artists:
                artists[track.artist] = Artist(
                    track.artist,
                    track.ms_played,
                    len(track.listens_list),
                    [track]
                )
            else:
                artists[track.artist].songs_played += len(track.listens_list)
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

class VersionControl:
    def __init__(self):
        self.current_version = self.get_current_version()
        self.recent_version = self.get_recent_version()

    def get_current_version(self):
        with open('version.json', mode='r') as file:
            data = json.load(file)
            self.current_version = data['version']
            return data['version']

    # Eventually come back to make it compatible with being offline.
    def get_recent_version(self):
        print(f'Checking version..')
        try:
            response = requests.get('https://raw.githubusercontent.com/Honuluau/Simple-Spotify-Data-Analyzer/refs/heads/master/version.json')
            self.recent_version = response.json()['version']
            return self.recent_version
        except Exception as e:
            print(f'{BColors.FAIL}Failed to grab latest version, setting most recent version to current version.{BColors.ENDC}')
            return self.get_current_version()


    def compare_version(self):
        if self.current_version != self.recent_version:
            print(f'{BColors.FAIL}VERSION MISMATCH: Current (v{self.current_version}), Most Recent: (v{self.recent_version}){BColors.ENDC}')
            return False
        else:
            print(f'{BColors.OKGREEN}VERSION MATCH: Current (v{self.current_version}), Most Recent: (v{self.recent_version}){BColors.ENDC}')
            return True

def main():
    version_control = VersionControl()
    if not version_control.compare_version():
        input("Press anything to close.")
        os.system('exit')

    print(f'Open any json file within the Spotify Data Folder')
    data_directory = os.path.dirname(askopenfilename(title='Select Spotify Data Folder', filetypes=[('Any Spotify Data Json File', '.json')]))

    music_reader = StreamingHistoryMusicReader(data_directory)
    """most_played_artists = music_reader.sort_most_played_artists(True)

    for artist in most_played_artists:
        print(f'{artist.name} - {artist.songs_played} times played.')
        """
    most_listened_songs = music_reader.sort_listen_songs(True)
    for song in most_listened_songs:
        print(f'{song.title} - {song.ms_played}')

    sys.exit(1)

if __name__ == '__main__':
    main()