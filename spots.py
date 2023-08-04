#!/usr/bin/python3
"""Download Audio from Spotify or Youtube"""

from argparse import ArgumentParser
from logging import basicConfig, error, ERROR, info, INFO
from os import mkdir, chdir, getcwd
from engine import storage
from models.download_urls import ConvertToMP3
from models.youtube_to_spotify import ProcessYoutubeLink

# set cli arguments
parser = ArgumentParser(
    description="Convert a YouTube or Spotify url to mp3"
)
parser.add_argument(
    '--url', type=str, nargs='+', default=[],
    help='One or more urls to be converted.'
)
parser.add_argument(
    '--search', type=str, nargs='+', default=[],
    help='Search for one or more tracks by title and name.',
    metavar='"Artist - Title"'
)
args = parser.parse_args()

# retrieve list of links and search titles
links = args.url
search_titles = args.search


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
        basicConfig(level=INFO)
        info(f'searching for {title}...')
        youtube = ProcessYoutubeLink(search_title=title)
        youtube.process_youtube_url()

    # download all links
    for link in links:
        is_valid_url = 'spotify' in link or 'youtu' in link
        if not is_valid_url:
            basicConfig(level=ERROR)
            error(f'{link} not valid YouTube or Spotify url')
            continue
        converter = ConvertToMP3(link)
        converter.convert_url()

        storage.save()

    # Change back to the original directory
    chdir(current_dir)


if __name__ == '__main__':
    main()
