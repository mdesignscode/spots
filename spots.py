#!/usr/bin/python3
"""Download Audio from Spotify or Youtube"""

from engine import storage
from get_spotify_track import GetSpotifyTrack
from os import mkdir, chdir, getcwd
from pytube import Playlist
from spotify_to_youtube import ProcessSpotifyLink
from youtube_to_spotify import ProcessYoutubeLink
import argparse
import logging

parser = argparse.ArgumentParser(description="Convert a YouTube or Spotify url to mp3")
parser.add_argument('--url', type=str, nargs='+', help='One or more urls to be converted.')
parser.add_argument('--search', type=str, nargs='+', default='', help='Search for a track by title and name.', metavar='"Artist - Title"')
args = parser.parse_args()
links = args.url
search_titles = args.search

logging.basicConfig(level=logging.INFO)


def main():
    # Get the current working directory
    current_dir = getcwd()

    # Create a new directory
    new_dir = 'Music'
    try:
        mkdir(new_dir)
    except FileExistsError:
        pass

    # Change to the new directory
    chdir(new_dir)

    # search for titles provided
    for title in search_titles:
        logging.basicConfig(level=logging.INFO)
        logging.info(f'searching for {title}...')
        youtube = ProcessYoutubeLink(search_title=title)
        youtube.process_youtube_url()

    # download all links
    for link in links:
        is_valid_url = 'spotify' in link or 'youtu' in link
        if not is_valid_url:
            logging.basicConfig(level=logging.ERROR)
            logging.error(f'{link} not valid YouTube or Spotify url')
            continue
        ConvertToMP3(link)

    storage.save()

    # Change back to the original directory
    chdir(current_dir)


def ConvertToMP3(url):
    """Converts a youtube or spotify url to mp3, or a youtube video to mp4

    Args:
        url (str): the url to be converted
        video_only (bool, optional): if true, downloads only video. Defaults to False.
    """
    # download spotify link
    if 'spotify' in url:
        spotify_client = GetSpotifyTrack(url)
        # single
        if 'track' in url:
            metadata = spotify_client.process_url()
            youtube_client = ProcessSpotifyLink(metadata)
            youtube_client.download_youtube_video()
        # playlist
        else:
            spotify_playlist, playlist_name = spotify_client.process_url()
            download_spotify_url(spotify_playlist, playlist_name)

    elif 'youtu' in url:
        # download a youtube playlist
        if 'playlist' in url:
            logging.info('Downloading YouTube Playlist...')
            download_youtube_playlist(url)
        else:
            search_client = ProcessYoutubeLink(url)
            search_client.process_youtube_url()


def download_spotify_url(spotify_playlist, album_folder):
    """downloads a spotify playlist

    Args:
        spotify_playlist (list): list of metadata objects
        album_folder (str): The folder to download an album or playlist to.
    """
    logging.info(f'Downloading {album_folder}...')
    for track in spotify_playlist:
        youtube_client = ProcessSpotifyLink(track)
        youtube_client.download_youtube_video(album_folder)


def download_youtube_playlist(url):
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
    logging.info(f'Downloading {new_dir}...')
    for video_url in playlist_urls:
        search_client = ProcessYoutubeLink(video_url)
        search_client.process_youtube_url()

    # Change back to the original directory
    chdir(current_dir)


if __name__ == '__main__':
    main()
