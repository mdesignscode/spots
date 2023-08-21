#!/usr/bin/python3
"""Download Audio from Spotify or Youtube"""

from argparse import ArgumentParser
from logging import basicConfig, error, ERROR, info, INFO
from os import mkdir, chdir, getcwd
from tenacity import retry, stop_after_delay
from engine import storage
from download_urls import convert_url
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

    storage.reload()

    download()

    # Change back to the original directory
    chdir(current_dir)


@retry(stop=stop_after_delay(120))
def download():
    # search for titles provided
    for title in search_titles:
        basicConfig(level=INFO)
        info(f'searching for {title}...')
        youtube = ProcessYoutubeLink(search_title=title)
        youtube.process_youtube_url()

        storage.save()

    # download all links
    if links:
        for link in links:
            is_valid_url = 'spotify' in link or 'youtu' in link
            if not is_valid_url:
                basicConfig(level=ERROR)
                error(f'{link} not valid YouTube or Spotify url')
                continue
            convert_url(link)

            storage.save()


if __name__ == '__main__':
    main()
