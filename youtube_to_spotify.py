#!/usr/bin/python3
"""A class that searches for a track from youtube on spotify"""

from __future__ import unicode_literals
from get_spotify_track import GetSpotifyTrack
from spotify_to_youtube import ProcessSpotifyLink
from html import unescape
from pytube import YouTube
import logging

logging.basicConfig(level=logging.ERROR)

class ProcessYoutubeLink(GetSpotifyTrack, ProcessSpotifyLink):
    """Searches for a track from youtube on deezer"""

    def __init__(self, youtube_url='', search_title=''):
        """initializes the url for title to be searched for

        Args:
            youtube_url (str, optional): the url to be processed. Defaults to ''.
            search_title = (str, optional): a title to be searched for. Defaults to ''.
        """
        self.youtube_url = youtube_url or self.get_youtube_video(search_title)
        self.youtube = YouTube(youtube_url) if youtube_url else None
        self.__sp = self._GetSpotifyTrack__sp

    def process_youtube_url(self):
        """Processes a youtube url and downloads it"""
        search_response = self.youtube

        result_title = search_response.title

        # Decode the string
        try:
            youtube_video_title = unescape(result_title)
        except TypeError:
            youtube_video_title = result_title

        youtube_video_title = youtube_video_title.replace(" (Official Video)", '')
        youtube_video_title = youtube_video_title.replace(" (Audio)", '')
        youtube_video_title = youtube_video_title.replace(" Uncut [HD]", '')
        youtube_video_title = youtube_video_title.replace(" [Video]", '')
        youtube_video_title = youtube_video_title.replace(" (HD)", '')
        youtube_video_title = youtube_video_title.replace(" (Complete)", '')

        # determine if original artist uploaded video
        artist = '' if '-' in youtube_video_title else search_response.author
        search_title = f'{artist} - {youtube_video_title}' if artist else youtube_video_title

        # search for title on deezer
        track_search = self.deezer_client.search(search_title)

        # first result should be most relevant
        if len(track_search):
            first_track = track_search[0]
            first_track_title = first_track.title
            spotify_id = ''
        else:
            # search for title on spotify
            spotify_search = self.__sp.search(search_title)

            items = spotify_search['tracks']['items']

            # if spotify search empty
            if not len(items):
                first_track_title = 'Not a valid title'
                spotify_id = ''
            else:
                first_track = spotify_search['tracks']['items'][0]
                first_track_title = first_track['name']
                spotify_id = first_track['id']

        condition = [
            first_track_title.lower() in youtube_video_title.lower(),
            youtube_video_title.lower() in first_track_title.lower()
            ]

        # then download from spotify
        if any(condition):
            logging.info('Downloading with metadata...')

            # retrieve metadata from spotify if found on spotify
            if spotify_id:
                metadata = self.get_track(spotify_id)
            # else use deezer
            else:
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
            }
            ProcessSpotifyLink.__init__(self, metadata)
            logging.info('Downloading from Youtube without editing metadata')
            self.download_youtube_video()
