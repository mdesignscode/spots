#!/usr/bin/python3
"""A class to retrieve metadata for a spotify track, album or playlist"""

from datetime import datetime
from deezer import Client
from dotenv import load_dotenv
from engine import storage
from os import getenv
from requests.exceptions import ConnectionError, ReadTimeout
from spotipy.oauth2 import SpotifyClientCredentials
from tenacity import retry, stop_after_delay
import logging
import lyricsgenius
import spotipy

load_dotenv()


class GetSpotifyTrack:
    """A class to retrieve metadata for a spotify track, album or playlist"""

    # create a Spotify API client
    __sp = spotipy.Spotify(
        auth_manager=SpotifyClientCredentials(
            client_id=getenv('SPOTIPY_CLIENT_ID'),
            client_secret=getenv('client_secret')
        )
    )

    # create genius api for lyrics
    __genius = lyricsgenius.Genius(getenv('lyricsgenius_key'))

    deezer_client = Client()

    def __init__(self, track_url=''):
        """initializes the spotify url to retrieve metadata from

        Args:
            track_url (str, optional): the spotify url. Defaults to ''.
        """
        self.track_url = track_url

    def get_track(self, track_id):
        """
            Retrieves metadata for a spotify track

            Arguments:
                track_id -- the track to retrieve data from

            Returns:
                dict -- an object with retrieved data
        """
        try:
            metadata_in_file = storage.get(self.track_url)
            if metadata_in_file:
                return metadata_in_file

            track = self.__sp.track(track_id)

            if track:
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
                    release_date_obj = datetime.strptime(release_date_str, "%Y-%m-%d")
                    release_date = release_date_obj.strftime("%Y-%")
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
                title = f'{artist} - {track_name}'
                album_name = album['name']

                # get track lyrics
                song = self.__genius.search_song(track_name, artist)
                not_found = not song or 'Verse' not in song.lyrics
                lyrics = None if not_found else song.lyrics

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

            else:
                metadata = self.get_metadata(title, track_url)

            # add metadata to metadata objects
            storage.new(metadata)

            return metadata
        except ConnectionError:
            logging.basicConfig(level=logging.ERROR)
            logging.error('No internet connection')
            quit()

    @retry(stop=stop_after_delay(10))
    def process_url(self):
        """processes spotify url according to resource type"""
        track_list = []
        try:
            resource_type = self.track_url.split('/')[3]
            track_id = self.track_url.split('/')[-1].split('?')[0]

            if resource_type == 'playlist':
                logging.info('Processing Spotify Playlist...')
                get_playlist = self.__sp.__getattribute__(resource_type)
                spotify_obj = get_playlist(track_id)
                playlist = spotify_obj['tracks']['items']
                for track in playlist:
                    track_list.append(self.get_track(track["track"]["id"]))
                return track_list, spotify_obj['name']

            elif resource_type == 'album':
                print('Processing Album...')
                get_playlist = self.__sp.__getattribute__(resource_type)
                spotify_obj = get_playlist(track_id)
                playlist = spotify_obj['tracks']['items']
                for track in playlist:
                    track_list.append(self.get_track(track["id"]))

                return track_list, spotify_obj['name']

            elif resource_type == 'track':
                print('Processing Single')
                return self.get_track(track_id)
        except ReadTimeout:
            logging.basicConfig(level=logging.ERROR)
            logging.error('Network Connection Timed Out')
            return track_list

    def get_metadata(self, title, url):
        """retrieve metadata using deezer api

        Args:
            title (str): the title to be searched for
            url (str): the url for the track
        """
        res = self.deezer_client.search(title)

        track = res[0]

        genre = ', '.join([genre.name for genre in track.album.genres])

        track_name = track.title
        cover = track.album.cover
        artist = track.artist.name
        track_number = f'{track.track_position}/{track.album.nb_tracks}'
        album_name = track.album.title
        release_date_obj = track.album.release_date
        release_date = release_date_obj.strftime("%Y-%m-%d")

        # get track lyrics
        song = self.__genius.search_song(track_name, artist)
        not_found = not song or 'Verse' not in song.lyrics
        lyrics = None if not_found else song.lyrics

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
