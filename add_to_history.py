#!/usr/bin/python3
"""Adds user's downloaded songs to spots history file"""

from os import listdir, path, chdir, getcwd
from sys import argv
from mutagen.id3 import ID3
from mutagen.mp3 import MP3, HeaderNotFoundError


folder = argv[1]

if __name__ == '__main__':
  if path.exists(folder):
    # spots history file
    spots_path = getcwd()
    history_file = f"{spots_path}/Music/.spots_download_history.txt"

    # open folder
    files = listdir(folder)
    chdir(folder)

    for file in files:
      # read mp3 tags
      if file[-4:] == '.mp3':
        try:
          song = MP3(file, ID3)
          artist = song.get('TPE1', '')
          artist = f'{artist} - ' if artist else ''
          title = song.get('TIT2', '')
          song_name = f"{artist}{title}"
          if not title:
            continue
          with open(history_file, "a", newline="") as file:
            file.write(f'{song_name}\n')
        except HeaderNotFoundError:
          pass
