- [Spots](#spots)
  - [Features](#features)
  - [Dependencies](#dependencies)
  - [Setup](#setup)
  - [Usage](#usage)
  - [Disclaimer](#disclaimer)
  - [License](#license)
# Spots

Spots is a command-line interface (CLI) tool written in Python that automates the process of adding metadata to downloaded tracks from Spotify or YouTube. It was born out of a need for a more organized and visually appealing music library.

## Features

- Downloads tracks from Spotify or YouTube and converts them to MP3.
- Automatically adds metadata (cover pictures, artist details, title, album information) to the downloaded tracks.
- Handles edge cases and network glitches for smooth operation.
- Reduces API calls by implementing local file storage for metadata and a downloads history file to avoid re-downloads.

## Dependencies

Spots uses the following libraries:

- spotipy for interacting with the Spotify API
- lyricsgenius for finding lyrics
- youtubesearchpython for searching titles on YouTube
- deezer-python for searching metadata if not found on Spotify
- moviepy for converting mp4 to mp3
- mutagen for adding mp3 metadata tags
- tenacity for network retries
- pytube for downloading from YouTube

## Setup

1. Clone this repository.
2. Install the dependencies.
3. Set the following environment variables:
   - `SPOTIPY_CLIENT_ID=spotify_client_id`
   - `client_secret=client_secret_client_secret`
   - `lyricsgenius_key=genius_secret_key`

## Usage

Spots takes in two positional arguments: a list of URLs to be downloaded, and a list of titles to be searched for.

Here's an example of how to use it:

```shell
python3 spots.py --urls [url1, url2, ...] --search [title1, title2, ...]
```

## Disclaimer

Spots is for educational purposes only. It does not promote or encourage the illegal downloading of copyrighted content. Please respect the rights of content creators.

## License

This project is licensed under the terms of the MIT license.
