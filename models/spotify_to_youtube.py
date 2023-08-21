#!/usr/bin/python3
"""Factor an object to Retrieve and Download a Youtube Video as MP3"""

from __future__ import unicode_literals
from dotenv import load_dotenv
from logging import basicConfig, error, ERROR, info, INFO
from hashlib import md5
from models.errors import TitleExistsError
from moviepy.editor import AudioFileClip
from mutagen.id3 import ID3, APIC, TIT2, TPE1, TRCK, TALB, USLT, TDRL, TCON
from mutagen.mp3 import MP3
from os import path, remove, getenv
from pytube import YouTube
from pytube.exceptions import AgeRestrictedError
from requests import get
from youtubesearchpython import VideosSearch
from engine import storage
from models.errors import InvalidURL

load_dotenv()


class ProcessSpotifyLink:
    """A client that Retrieves and Download a Youtube Video as MP3

    Attributes:
        spotify_track (dict): an object with metadata
        youtube_url (str, optional): youtube url to be downloaded. Defaults to ''.
    """

    def __init__(self, spotify_track: dict, youtube_url=''):
        self.spotify_track = spotify_track
        self.youtube_url = youtube_url or self.get_youtube_video()

    def download_youtube_video(self, directory_path=''):
        """Downloads a youtube video as audio

        Args:
            directory_path (str, optional): The directory to save a playlist to. Defaults to ''.
        """
        # no search result found
        if not self.youtube_url:
            return

        # check url availability
        try:
            yt = YouTube(self.youtube_url, use_oauth=bool(getenv('use_oauth')))
            yt.check_availability()
        except:
            basicConfig(level=ERROR)
            error(f'{self.youtube_url} is not available')
            raise InvalidURL

        storage.new(self.spotify_track)

        # add title to downloads history
        track_title = f'{self.spotify_track["artist"]} - {self.spotify_track["title"]}'
        # '/' will read file name as folder in *nix systems
        track_title = track_title.replace('/', '|')

        try:
            self.add_to_download_history(track_title)
        except TitleExistsError:
            basicConfig(level=INFO)
            info(f'{self.spotify_track["title"]} already in list')
            return

        # get highest quality audio file
        try:
            audio = yt.streams.get_audio_only()
        except:
            basicConfig(level=ERROR)
            error(f"Couldn't download {track_title}")
            return

        # get audio file name
        ext = audio.mime_type.split('/')[1]
        filename = f'{track_title}.{ext}'

        # file name to download to
        output = path.join(directory_path, filename)

        # Check if the file name length is too long, and truncate if necessary
        max_filename_length = 255  # Maximum allowed file name length on most systems
        if len(filename) > max_filename_length:
            # Generate a unique file name using a hash function (MD5 in this case)
            file_hash = md5(track_title.encode()).hexdigest()
            output = path.join(directory_path, f"{file_hash[:25]}.{ext}")
            filename = f"{file_hash[:25]}.{ext}"

        # download the audio file
        print(f'Downloading {track_title}...')
        audio.download(output_path=directory_path, filename=filename)

        # convert to mp3 and update metadata
        try:
            self.convert_to_mp3(
                output,
                path.join(directory_path, filename.replace('.mp4', '.mp3')),
                track_title
            )
        except:
            error(f"Failed to convert {track_title}.{ext}")
            self.add_to_download_history(track_title, True)
            return

    def update_metadata(self, audio_path: str):
        """Updates the metadata of song to be downloaded

        Args:
            audio_path (str): the path of the audio file to be updated
        """
        try:
            audio = MP3(audio_path, ID3=ID3)

            metadata = self.spotify_track

            # Remove existing ID3 tags
            audio.tags = None

            # Create new ID3 tags
            audio.tags = ID3()

            # Set the metadata attributes
            audio.tags.add(TIT2(encoding=3, text=metadata.get('title', '')))
            audio.tags.add(TPE1(encoding=3, text=metadata.get('artist', '')))
            audio.tags.add(
                TRCK(encoding=3, text=metadata.get('tracknumber', '')))
            audio.tags.add(TALB(encoding=3, text=metadata.get('album', '')))

            cover = metadata.get('cover', '')
            if cover:
                audio.tags.add(APIC(encoding=3, mime='image/jpeg', type=3,
                                    desc=u'Cover', data=get(metadata['cover']).content))

            # Add lyrics if provided
            lyrics = metadata.get('lyrics', '')
            if lyrics:
                audio.tags.add(
                    USLT(encoding=3, lang='eng', desc='', text=lyrics))

            # Set the release date
            release_date = metadata.get('release_date', '')
            if release_date:
                audio.tags.add(
                    TDRL(encoding=3, text=metadata['release_date']))

            # Add the new genre tag if provided
            genre = metadata.get('genre', '')
            if genre:
                audio["TCON"] = TCON(encoding=3, text=genre)

            # Save the changes
            audio.save(audio_path)

        except FileNotFoundError:
            basicConfig(level=ERROR)
            error(f'{audio_path} not found...')
            return

    @staticmethod
    def add_to_download_history(title='', add_title=False):
        """Adds a downloaded song's title to history

        Args:
            title (str, optional): The title to be added. Defaults to ''.
            add_title (bool, optional): If False, only checks if title already exists. Defaults to false.

        Raises:
            TitleExistsError: if title already in downloads history
        """
        history_file = ".spots_download_history.txt"

        # Check if the file exists, otherwise create it
        if not path.isfile(history_file):
            with open(history_file, "w", newline=""):
                pass

        # Check if the title already exists in the file
        with open(history_file, "r") as file:
            history = file.read().split('\n')
            for song in history:
                if title == song:
                    raise TitleExistsError

        # Add the title to the file
        if add_title:
            with open(history_file, "a", newline="") as file:
                file.write(f'{title}\n')

    def get_youtube_video(self, search_title=''):
        """Searches for a given title on youtube

        Args:
            search_title (str, optional): the path of the audio file to be updated. Defaults to ''.

        Returns:
            str: the watch url
        """
        title = f'{search_title} Audio' if search_title else f"{self.spotify_track['title']} - {self.spotify_track['artist']} Audio"
        videosSearch = VideosSearch(title, limit=1)

        search_result = videosSearch.result()['result']

        if not search_result:
            basicConfig(level=ERROR)
            error(f'No search results for {title}')
            return ''

        first_result = search_result[0]

        return first_result['link']

    def convert_to_mp3(self, old_file: str, new_file: str, song_title: str):
        """converts an audio file to mp3, updates the metadata and removes the original file

        Args:
            old_file (str): the file to be converted
            new_file (str): the name of the new file
            song_title (str): the title to be added to downloads history
        """
        try:
            # Load the audio clip
            clip = AudioFileClip(old_file)
            # Convert and save as MP3 format
            clip.write_audiofile(new_file, codec='mp3')

            # Close the clip
            clip.close()
            remove(old_file)

            if self.spotify_track:
                self.update_metadata(new_file)

        except FileNotFoundError:
            basicConfig(level=ERROR)
            error(f'{old_file} not found...')
            return

        self.add_to_download_history(song_title, True)
