#!/usr/bin/python3
"""A class to retrieve metadata for a spotify track, album or playlist"""

from datetime import datetime
from dotenv import load_dotenv
from engine import storage
from models.errors import InvalidURL
from os import getenv
from requests.exceptions import ReadTimeout
from spotipy.exceptions import SpotifyException
from spotipy.oauth2 import SpotifyClientCredentials
import logging
from lyricsgenius import Genius
from spotipy import Spotify

load_dotenv()


class GetSpotifyTrack:
    """A class to retrieve metadata for a spotify track, album or playlist

    Attributes:
        track_url (str): The spotify url to be processed
    """

    # create a Spotify API client
    spotify = Spotify(
        auth_manager=SpotifyClientCredentials(
            client_id=getenv('SPOTIPY_CLIENT_ID'),
            client_secret=getenv('client_secret')
        )
    )

    # create genius api for lyrics
    genius = Genius(getenv('lyricsgenius_key'))

    def __init__(self, track_url: str):
        self.track_url = track_url

    def get_track(self, track_id: str) -> dict:
        """
            Retrieves metadata for a spotify track

            Arguments:
                track_id (str): the track id to retrieve data from.

            Returns:
                dict: an object with retrieved data
        """
        print('Searching for metadata...')
        metadata_in_file = storage.get(self.track_url)
        if metadata_in_file:
            return metadata_in_file

        try:
            # retrieve track from spotify
            track = self.spotify.track(track_id)

            album = track['album']

            # get track number
            total_track = album['total_tracks']
            track_position = track['track_number']
            track_number = f'{track_position}/{total_track}'

            # cover image
            cover = album['images'][0]['url']

            # get release date
            try:
                release_date_str = album['release_date']
                release_date_obj = datetime.strptime(
                    release_date_str, "%Y-%m-%d")
                release_date = release_date_obj.strftime("%Y")
            except ValueError:
                release_date = None

            # get track name and artist
            track_name = track['name']

            # artists
            artistList = [artist['name'] for artist in track['artists']]
            # remove featured artists from artists list
            for artist in artistList:
                if artist.lower() in track_name.lower():
                    artistList.remove(artist)

            artist = ', '.join(artistList)

            track_url = track['external_urls']['spotify']
            album_name = album['name']

            # get track lyrics
            song = self.genius.search_song(track_name, artist)
            not_found = not song or 'Verse' not in song.lyrics or track_name not in song.title
            lyrics = '' if not_found else song.lyrics

            metadata = {
                'title': track_name,
                'cover': cover,
                'artist': artist,
                'tracknumber': track_number,
                'album': album_name,
                'lyrics': lyrics,
                'release_date': release_date,
                'link': track_url,
                'genre': ''
            }

            return metadata

        except SpotifyException:
            logging.basicConfig(level=logging.ERROR)
            logging.error(f'{self.track_url} is invalid')
            raise InvalidURL

    def process_url(self):
        """processes spotify url according to resource type"""
        track_list = []
        playlist_name = ''
        try:
            resource_type = self.track_url.split('/')[3]
            track_id = self.track_url.split('/')[-1].split('?')[0]

            if resource_type == 'playlist':
                print('Processing Spotify Playlist...')

                # get spotify playlist
                get_playlist = self.spotify.__getattribute__(resource_type)
                spotify_obj = get_playlist(track_id)

                # get playlist tracks
                playlist = spotify_obj['tracks']['items']

                playlist_name = spotify_obj['name']
                # get metadata for each track in playlist
                for track in playlist:
                    track_list.append(self.get_track(track["track"]["id"]))

                return track_list, playlist_name

            elif resource_type == 'album':
                print('Processing Album...')

                # get spotify album
                get_album = self.spotify.__getattribute__(resource_type)
                spotify_obj = get_album(track_id)

                # get album tracks
                album = spotify_obj['tracks']['items']

                playlist_name = spotify_obj['name']
                # get metadata for each track in playlist
                for track in album:
                    track_list.append(self.get_track(track["id"]))

                return track_list, playlist_name

            elif resource_type == 'track':
                print('Processing Single...')
                return self.get_track(track_id)

        except ReadTimeout:
            logging.basicConfig(level=logging.ERROR)
            logging.error('Network Connection Timed Out!')
            return track_list, playlist_name
