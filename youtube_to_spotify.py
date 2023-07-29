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

    def __init__(self, youtube_url):
        """initializes the url for title to be searched for

        Args:
            youtube_url (str): the url to be processed
        """
        self.youtube_url = youtube_url
        self.youtube = YouTube(youtube_url)

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

        # determine if original artist uploaded video
        artist = '' if ' - ' in youtube_video_title else search_response.author
        search_title = f'{artist} - {youtube_video_title}' if artist else youtube_video_title

        # search for title on spotify
        track_search = self.deezer_client.search(search_title)

        # first result should be most relevant
        first_track = track_search[0]

        first_track_title = first_track.title

        # Extracted values from YouTube video
        substring = first_track_title
        string = search_title
        title = youtube_video_title

        condition = [title in substring, title in string]

        track_name = search_title.split(' - ')[1]
        artist = search_title.split(' - ')[0]
        artist = artist.replace(' - Topic', '')

        # then download from spotify
        if any(condition):
            logging.info('Downloading with metadata...')
            metadata = self.get_metadata(search_title, self.youtube_url)

            ProcessSpotifyLink.__init__(self, metadata, self.youtube_url)

            # download video as audio
            self.download_youtube_video()

        # else download from youtube without editing metadata
        else:
            metadata = {
                'title': track_name,
                'artist': artist,
            }
            ProcessSpotifyLink.__init__(self, metadata)
            logging.info('Downloading from Youtube without editing metadata')
            self.download_youtube_video()
