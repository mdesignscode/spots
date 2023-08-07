#!/usr/bin/python3
"""Contains functions that processes a Spotify or YouTube url"""

from logging import basicConfig, ERROR, error
from os import mkdir, chdir, getcwd
from pytube import Playlist, YouTube
from models.get_spotify_track import GetSpotifyTrack
from models.errors import InvalidURL
from models.spotify_to_youtube import ProcessSpotifyLink
from models.youtube_to_spotify import ProcessYoutubeLink


def convert_url(url: str):
    """Converts a youtube or spotify url to mp3, or a youtube video to mp3

    Args:
        url (str): url to be converted

    Raises:
        InvalidURL: if provided url not available
    """
    try:
        # download spotify link
        if 'spotify' in url:
            spotify = GetSpotifyTrack(url)
            # single
            if 'track' in url:
                metadata = spotify.process_url()
                youtube = ProcessSpotifyLink(metadata)
                youtube.download_youtube_video()
            # playlist
            else:
                spotify_playlist, playlist_name = spotify.process_url()
                download_spotify_playlist(spotify_playlist, playlist_name)

        elif 'youtu' in url:
            # check url availability
            try:
                youtube = YouTube(url)
                youtube.check_availability()
            except:
                basicConfig(level=ERROR)
                error(f'{url} is not available')
                raise InvalidURL

            # download a youtube playlist
            if 'playlist' in url:
                download_youtube_playlist(url)
            else:
                yt_to_spotify = ProcessYoutubeLink(youtube_url=url)
                yt_to_spotify.process_youtube_url()

    except InvalidURL:
        return

def download_spotify_playlist(spotify_playlist: [{}], album_folder: str):
    """downloads a spotify playlist

    Args:
        spotify_playlist (list): list of metadata objects
        album_folder (str): The folder to download an album or playlist to.
    """
    print(f'Downloading {album_folder}...')
    for track in spotify_playlist:
        spotify = ProcessSpotifyLink(track)
        spotify.download_youtube_video(album_folder)

def download_youtube_playlist(url: str):
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
        youtube = ProcessYoutubeLink(video_url)
        youtube.process_youtube_url()

    # Change back to the original directory
    chdir(current_dir)
