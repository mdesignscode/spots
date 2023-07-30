#!/usr/bin/python3
"""Factor an object to Retrieve and Download a Youtube Video as MP3"""

from __future__ import unicode_literals
from csv import writer, reader
from moviepy.editor import *
from mutagen.id3 import ID3, APIC, TIT2, TPE1, TRCK, TALB, USLT, TDRL, TCON
from mutagen.mp3 import MP3
from os import path, remove
from pytube import YouTube
from requests import get
from tenacity import retry, stop_after_delay
import logging


class ProcessSpotifyLink:
    """A client that Retrieves and Download a Youtube Video as MP3"""

    def __init__(self, spotify_track: dict, youtube_url=''):
        """initializes an object with metadata

        Args:
            spotify_track (dict): an object with metadata
            youtube_url (str, optional): youtube url to be downloaded. Defaults to ''.
        """
        self.spotify_track = spotify_track
        self.youtube_url = youtube_url if youtube_url else self.get_youtube_video()
        self.youtube = YouTube(self.youtube_url)

    # @retry(stop=stop_after_delay(10))
    def download_youtube_video(self, directory_path=''):
        """Converts a youtube video to mp3

        Args:
            directory_path (str, optional): The directory to save a playlist to. Defaults to ''.
        """
        yt = self.youtube
        # add title to downloads history
        track_title = f'{self.spotify_track["artist"]} - {self.spotify_track["title"]}'
        should_download = self.add_to_download_history(track_title)
        if not should_download:
            logging.basicConfig(level=logging.INFO)
            logging.info(f'{self.spotify_track["title"]} already in list')
            return

        try:
            audio = yt.streams.get_audio_only()
            ext = audio.mime_type.split('/')[1]
            filename = f'{track_title}.{ext}'
            output = f'{directory_path}/{filename}' if directory_path else filename

            logging.basicConfig(level=logging.INFO)
            logging.info(f'Downloading {track_title}...')
            audio.download(output_path=directory_path, filename=filename)

            # convert to mp3 if mp4
            # Load the video clip (as audio)
            clip = AudioFileClip(output)
            # Convert and save as MP3 format
            new_mp3 = f"{directory_path}/{track_title}.mp3" if directory_path else f"{track_title}.mp3"
            clip.write_audiofile(new_mp3, codec='mp3')

            # Close the clip
            clip.close()
            remove(output)

            if self.spotify_track:
                self.update_metadata(new_mp3)

            self.add_to_download_history(track_title, True)

        except FileNotFoundError:
            logging.basicConfig(level=logging.ERROR)
            logging.info(f'{track_title} not downloaded')
            return

    def update_metadata(self, audio_path):
        """Updates the metadata of song to be downloaded

        Args:
            audio_path (str): the path of the audio file to be updated
        """
        # try:
        audio = MP3(audio_path, ID3=ID3)

        metadata = self.spotify_track

        # Remove existing ID3 tags
        audio.tags = None

        # Create new ID3 tags
        audio.tags = ID3()

        # Set the metadata attributes
        audio.tags.add(TIT2(encoding=3, text=metadata.get('title', '')))
        audio.tags.add(TPE1(encoding=3, text=metadata.get('artist', '')))
        audio.tags.add(TRCK(encoding=3, text=metadata.get('tracknumber', '')))
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
        # except Exception as e:
        # print(e)

    @staticmethod
    def add_to_download_history(title=None, add_title=False):
        """Adds a downloaded song's title to history or returns False if the title already exists.

        Args:
            download_title (str, optional): The title to be added. Defaults to None.
            add_title (bool, optional): If False, only checks if title already exists. Defaults to false.

        Returns:
            str or bool: the path to history file if download_title is None, False if the title already exists.
        """
        csv_file = ".spots_download_history.csv"

        # Check if the file exists, otherwise create it
        if not path.isfile(csv_file):
            with open(csv_file, "w", newline="") as file:
                csv_writer = writer(file)
                csv_writer.writerow(["Download Title"])

        # Check if title is provided
        if not title:
            return path.abspath(csv_file)

        # Check if the title already exists in the file
        with open(csv_file, "r") as file:
            csv_reader = reader(file)
            for row in csv_reader:
                if row and title == row[0]:
                    return False

        # Add the title to the file
        if add_title:
            with open(csv_file, "a", newline="") as file:
                csv_writer = writer(file)
                song_name = title.strip('"')
                csv_writer.writerow([song_name])

        return True

    def get_youtube_video(self, search_title=''):
        """Searches for a given title on youtube

        Args:
            search_title (str, optional): the path of the audio file to be updated. Defaults to ''.

        Returns:
            str: the watch url
        """
        from youtubesearchpython import VideosSearch

        title = f'{search_title} Audio' if search_title else f"{self.spotify_track['title']} - {self.spotify_track['artist']} Audio"
        videosSearch = VideosSearch(title, limit=1)

        first_result = videosSearch.result()['result'][0]

        return first_result['link']
