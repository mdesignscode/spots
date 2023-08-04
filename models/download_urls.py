#!/usr/bin/python3
"""A class that processes a Spotify or YouTube url"""

from os import mkdir, chdir, getcwd
from pytube import Playlist
from models.get_spotify_track import GetSpotifyTrack
from models.errors import InvalidURL
from models.spotify_to_youtube import ProcessSpotifyLink
from models.youtube_to_spotify import ProcessYoutubeLink


class ConvertToMP3(ProcessYoutubeLink):
    """Downloads a Spotify or YouTube url

    Args:
        url (str): the url to be downloaded
    """

    def __init__(self, url):
        self.url = url

    # @retry
    def convert_url(self):
        """Converts a youtube or spotify url to mp3, or a youtube video to mp3"""
        # download spotify link
        url = self.url

        if 'spotify' in url:
            try:
                GetSpotifyTrack.__init__(self, url)
                # single
                if 'track' in url:
                    metadata = self.process_url()
                    ProcessSpotifyLink.__init__(self, metadata)
                    self.download_youtube_video()
                # playlist
                else:
                    spotify_playlist, playlist_name = self.process_url()
                    self.download_spotify_playlist(spotify_playlist, playlist_name)
            except InvalidURL:
                return

        elif 'youtu' in url:
            # download a youtube playlist
            if 'playlist' in url:
                self.download_youtube_playlist(url)
            else:
                super().__init__(url)
                self.process_youtube_url()

    def download_spotify_playlist(self, spotify_playlist, album_folder):
        """downloads a spotify playlist

        Args:
            spotify_playlist (list): list of metadata objects
            album_folder (str): The folder to download an album or playlist to.
        """
        print(f'Downloading {album_folder}...')
        for track in spotify_playlist:
            ProcessSpotifyLink.__init__(self, track)
            self.download_youtube_video(album_folder)

    def download_youtube_playlist(self, url):
        """downloads all songs in a youtube playlist

        Args:
            url (str): the url of the playlist
        """
        playlist = Playlist(url)
        playlist_urls = playlist.video_urls

        # Get the current working directory
        current_dir = getcwd()

        # Create a new directory
        new_dir = playlist.title
        try:
            mkdir(new_dir)
        except FileExistsError:
            pass

        # Change to the new directory
        chdir(new_dir)

        # download each song in playlist directory
        print(f'Downloading {new_dir}...')
        for video_url in playlist_urls:
            super().__init__(video_url)
            self.process_youtube_url()

        # Change back to the original directory
        chdir(current_dir)
