#!/usr/bin/python3
"""A class that searches for a track from youtube on spotify"""

from __future__ import unicode_literals
from deezer import Client
from html import unescape
from logging import basicConfig, error, ERROR
from os import getenv
from pytube import YouTube
from models.errors import MetadataNotFound, InvalidURL
from models.get_spotify_track import GetSpotifyTrack
from models.spotify_to_youtube import ProcessSpotifyLink


class ProcessYoutubeLink(GetSpotifyTrack, ProcessSpotifyLink):
    """Searches for a track from youtube on deezer or spotify"""
    deezer_client = Client()

    def __init__(self, youtube_url: str = '', search_title: str = ''):
        """initializes the url for title to be searched for

        Args:
            youtube_url (str, optional): the url to be processed. Defaults to ''.
            search_title (str, optional): a title to be searched for. Defaults to ''.
        """
        self.youtube_url = youtube_url or self.get_youtube_video(search_title)
        self.youtube = YouTube(
            self.youtube_url,
            use_oauth=bool(getenv('use_oauth'))
        ) if self.youtube_url else None

    def process_youtube_url(self):
        """Processes a youtube url and downloads it"""
        try:
            condition, search_title = self.search_title()
        except InvalidURL:
            return

        # download with metadata
        if any(condition):
            print('Downloading with metadata...')

            metadata = self.get_metadata(search_title, self.youtube_url)

            ProcessSpotifyLink.__init__(self, metadata, self.youtube_url)

            # download video as audio
            self.download_youtube_video()

        # else download from youtube without editing metadata
        else:
            track_name = search_title.split('-')[1].strip()
            artist = search_title.split('-')[0].strip()
            artist = artist.replace(' - Topic', '')

            metadata = {
                'title': track_name,
                'artist': artist,
                'link': self.youtube_url
            }

            ProcessSpotifyLink.__init__(self, metadata)
            print('Downloading from Youtube without editing metadata...')
            self.download_youtube_video()

    def get_metadata(self, title: str, url: str) -> dict:
        """retrieve metadata using deezer api

        Args:
            title (str): the title to be searched for
            url (str): the url for the track

        Returns:
            dict: the metadata of searched track

        Raises:
            MetadataNotFound: if search title not found
        """
        res = self.deezer_client.search(title)
        if not res:
            raise MetadataNotFound

        track = res[0]

        genre = ', '.join([genre.name for genre in track.album.genres])

        track_name = track.title
        cover = track.album.cover
        artist = track.artist.name
        track_number = f'{track.track_position}/{track.album.nb_tracks}'
        album_name = track.album.title
        release_date_obj = track.album.release_date
        release_date = release_date_obj.strftime("%Y")

        # get track lyrics
        song = self.genius.search_song(track_name, artist)
        not_found = not song or 'Verse' not in song.lyrics
        lyrics = '' if not_found else song.lyrics

        metadata = {
            'title': track_name,
            'cover': cover,
            'artist': artist,
            'tracknumber': track_number,
            'album': album_name,
            'lyrics': lyrics,
            'release_date': release_date,
            'link': url,
            'genre': genre
        }

        return metadata

    def get_title(self) -> tuple:
        """Retrieve artist and title on YouTube video object

        Returns:
            tuple: the search title and youtube video title

        Raises:
            InvalidURL: if invalid YouTube video url provided
        """
        # check url availability
        search_response = self.youtube
        try:
            search_response.check_availability()
        except:
            basicConfig(level=ERROR)
            error(f'{self.youtube_url} is not available')
            raise InvalidURL

        result_title = search_response.title

        # Decode the string
        try:
            youtube_video_title = unescape(result_title)
        except TypeError:
            youtube_video_title = result_title

        # remove unnecessary keywords from title
        youtube_video_title = youtube_video_title.replace(
            " (Official Video)", '')
        youtube_video_title = youtube_video_title.replace(" (Audio)", '')
        youtube_video_title = youtube_video_title.replace(" Uncut [HD]", '')
        youtube_video_title = youtube_video_title.replace(" [Video]", '')
        youtube_video_title = youtube_video_title.replace(" (HD)", '')
        youtube_video_title = youtube_video_title.replace(" (Official Music Video)", '')
        youtube_video_title = youtube_video_title.replace(" (Complete)", '')

        # determine if original artist uploaded video
        artist = '' if '-' in youtube_video_title else search_response.author
        search_title = f'{artist} - {youtube_video_title}' if artist else youtube_video_title

        return (search_title, youtube_video_title)

    def search_title(self) -> tuple:
        """Processes a youtube url and downloads it

        Returns:
            tuple: the condition to download search result and the search title string
        """
        search_title, youtube_video_title = self.get_title()

        # search for title on deezer
        try:
            metadata = self.get_metadata(search_title, self.youtube_url)
            first_track_title = metadata['title']

        except MetadataNotFound:
            # search for title on spotify
            spotify_search = self.spotify.search(search_title)

            items = spotify_search['tracks']['items']

            # if spotify search empty
            if not items:
                first_track_title = 'Not a valid title'
            else:
                # retrieve metadata from spotify
                first_track = items[0]
                first_track_title = first_track['name']
                spotify_url = first_track['external_urls']['spotify']

                GetSpotifyTrack.__init__(self, spotify_url)

                metadata = self.process_url()
                first_track_title = metadata['title']

        condition = [
            first_track_title.lower() in youtube_video_title.lower(),
            youtube_video_title.lower() in first_track_title.lower()
        ]

        return (condition, search_title)
