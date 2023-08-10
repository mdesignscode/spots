- [Spots](#spots)
  - [Features](#features)
  - [Dependencies](#dependencies)
  - [Setup](#setup)
  - [Usage](#usage)
  - [Classes](#classes)
  - [Unit Tests](#unit-tests)
    - [GetSpotifyTrack Unit Tests](#getspotifytrack-unit-tests)
      - [`test_get_track`](#test_get_track)
      - [`test_process_url_with_invalid_url`](#test_process_url_with_invalid_url)
      - [`test_process_url_with_playlist`](#test_process_url_with_playlist)
      - [`test_process_url_with_album`](#test_process_url_with_album)
      - [`test_process_url_with_single`](#test_process_url_with_single)
    - [ProcessSpotifyLink Unit Tests](#processspotifylink-unit-tests)
      - [`test_add_to_download_history`](#test_add_to_download_history)
      - [`test_update_metadata`](#test_update_metadata)
      - [`test_get_youtube_video`](#test_get_youtube_video)
      - [`test_download_youtube_video`](#test_download_youtube_video)
    - [ProcessYoutubeLink Unit Tests](#processyoutubelink-unit-tests)
      - [`test_get_title`](#test_get_title)
      - [`test_get_title_raises_error`](#test_get_title_raises_error)
      - [`test_search_title`](#test_search_title)
      - [`test_get_metadata`](#test_get_metadata)
    - [FileStorage Unit Tests](#filestorage-unit-tests)
      - [`test_all`](#test_all)
      - [`test_new`](#test_new)
      - [`test_save`](#test_save)
      - [`test_reload`](#test_reload)
      - [`test_get`](#test_get)
  - [License](#license)
  - [Disclaimer](#disclaimer)
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
<em>*Note: This setup assumes a shell environment</em>
1. Clone this repository:
    ```bash
    git clone https://github.com/mdesignscode/spots.
2. Go to spots directory
    ```bash
    cd spots
    ```
3. Create environment file
    ```bash
    touch .env
    ```
4. Set the following environment variables in `.env`:
   - `SPOTIPY_CLIENT_ID=spotify_client_id`
   - `client_secret=client_secret_client_secret`
   - `lyricsgenius_key=genius_secret_key`
5. Create a python virtual environment to avoid dependency collisions
    - Create environment
    ```bash
    python -m venv spots_venv
    ```
    - Activate environment:
    ```bash
    source spots_venv/bin/activate
    ```
    - You should now see `(spots_venv)` in your terminal
6. Install the dependencies.
    ```bash
    pip install -r requirements.txt
    ```


## Usage

You can add your current downloaded songs to the spots history

```bash
python3 add_to_history.py /path/to/folder/with/songs
```

Spots takes in two positional arguments: a list of URLs to be downloaded, and a list of titles to be searched for:

```shell
python3 spots.py --urls [url1, url2, ...] --search [title1, title2, ...]
```

Here's an example of how to use it:

<em>Downloading a list of urls</em>

```bash
python3 spots.py --urls https://youtu.be/aqeVwhR_wrM https://open.spotify.com/playlist/37i9dQZF1DZ06evO1jdg13?si=5cb56e184b954537
```

<em>Searching for a list of titles</em>

```bash
python3 spots.py --search "Artist1 - Title 1" "Artist2 - Title 2"
```

## Classes

<h3>GetSpotifyTrack</h3>

<em>Retrieve metadata for a spotify track, album or playlist</em>

```python3
class GetSpotifyTrack:
    """A class to retrieve metadata for a spotify track, album or playlist

    Attributes:
        track_url (str): The spotify url to be processed
    """

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

    def process_url(self):
        """processes spotify url according to resource type"""
```

<h3>ProcessSpotifyLink</h3>

<em>Retrieves and Download a Youtube Video as MP3</em>

```python3
class ProcessSpotifyLink:
    """A client that Retrieves and Download a Youtube Video as MP3

    Attributes:
        spotify_track (dict): an object with metadata
        youtube_url (str, optional): youtube url to be downloaded. Defaults to ''.
    """

    def __init__(self, spotify_track: dict, youtube_url=''):
        self.spotify_track = spotify_track
        self.youtube_url = youtube_url or self.get_youtube_video()

    def download_youtube_video(self, directory_path=''):
        """Downloads a youtube video as audio

        Args:
            directory_path (str, optional): The directory to save a playlist to. Defaults to ''.
        """

    def update_metadata(self, audio_path: str):
        """Updates the metadata of song to be downloaded

        Args:
            audio_path (str): the path of the audio file to be updated
        """

    @staticmethod
    def add_to_download_history(title='', add_title=False):
        """Adds a downloaded song's title to history

        Args:
            title (str, optional): The title to be added. Defaults to ''.
            add_title (bool, optional): If False, only checks if title already exists. Defaults to false.

        Raises:
            TitleExistsError: if title already in downloads history
        """

    def get_youtube_video(self, search_title=''):
        """Searches for a given title on youtube

        Args:
            search_title (str, optional): the path of the audio file to be updated. Defaults to ''.

        Returns:
            str: the watch url
        """

    def convert_to_mp3(self, old_file: str, new_file: str, song_title: str):
        """converts an audio file to mp3, updates the metadata and removes the original file

        Args:
            old_file (str): the file to be converted
            new_file (str): the name of the new file
            song_title (str): the title to be added to downloads history
        """
```

<h3>ProcessYoutubeLink</h3>

<em>Searches for a track from youtube on deezer or spotify</em>


```python3
class ProcessYoutubeLink(GetSpotifyTrack, ProcessSpotifyLink):
    """Searches for a track from youtube on deezer or spotify"""
    deezer_client = Client()

    def __init__(self, youtube_url: str = '', search_title: str = ''):
        """initializes the url for title to be searched for

        Args:
            youtube_url (str, optional): the url to be processed. Defaults to ''.
            search_title (str, optional): a title to be searched for. Defaults to ''.
        """
        self.youtube_url = youtube_url or self.get_youtube_video(search_title)
        self.youtube = YouTube(youtube_url) if youtube_url else None

    def process_youtube_url(self):
        """Processes a youtube url and downloads it"""

    def get_metadata(self, title: str, url: str) -> dict:
        """retrieve metadata using deezer api

        Args:
            title (str): the title to be searched for
            url (str): the url for the track

        Returns:
            dict: the metadata of searched track

        Raises:
            MetadataNotFound: if search title not found
        """

    def get_title(self) -> tuple:
        """Retrieve artist and title on YouTube video object

        Returns:
            tuple: the search title and youtube video title

        Raises:
            InvalidURL: if invalid YouTube video url provided
        """

    def search_title(self) -> tuple:
        """Processes a youtube url and downloads it

        Returns:
            tuple: the condition to download search result and the search title string
        """

```

## Unit Tests

To run unit tests:

```bash
python3 -m unittest discover -s tests
```

### GetSpotifyTrack Unit Tests

#### `test_get_track`

This test verifies that the `get_track` method of the `GetSpotifyTrack` class returns the correct metadata for a Spotify track. It mocks the Spotify API's `track` and Genius API's `search_song` methods to simulate fetching track information and lyrics.

#### `test_process_url_with_invalid_url`

This test checks if the `process_url` method of the `GetSpotifyTrack` class raises an `InvalidURL` error when an invalid Spotify URL is provided.

#### `test_process_url_with_playlist`

This test validates that the `process_url` method correctly processes a Spotify playlist URL. It mocks the necessary API calls and asserts that the returned metadata and album name match the expected values.

#### `test_process_url_with_album`

Similar to the previous test, this one ensures that the `process_url` method handles a Spotify album URL correctly. It mocks the API calls and confirms that the metadata and album name are as expected.

#### `test_process_url_with_single`

This test validates that the `process_url` method behaves correctly with a single Spotify track URL. It mocks API calls and asserts that the returned metadata matches the expected values.

### ProcessSpotifyLink Unit Tests

#### `test_add_to_download_history`

This test checks the `add_to_download_history` method of the `ProcessSpotifyLink` class. It verifies that the method correctly adds new titles to the download history file and raises `TitleExistsError` when attempting to add an existing title.

#### `test_update_metadata`

This test validates the `update_metadata` method of the `ProcessSpotifyLink` class. It confirms that the method properly updates metadata tags on an MP3 file.

#### `test_get_youtube_video`

This test checks the `get_youtube_video` method of the `ProcessSpotifyLink` class. It verifies that the method correctly returns the first YouTube video URL for a title search.

#### `test_download_youtube_video`

This test ensures the `download_youtube_video` method of the `ProcessSpotifyLink` class correctly downloads a YouTube video, converts it to MP3, and handles different scenarios, such as long titles and invalid URLs.

### ProcessYoutubeLink Unit Tests

#### `test_get_title`

This test verifies that the `get_title` method of the `ProcessYoutubeLink` class correctly fetches the YouTube video's title for searching on Spotify. It simulates API calls and asserts that the expected title is obtained.

#### `test_get_title_raises_error`

This test checks if the `get_title` method raises an `InvalidURL` exception when an invalid YouTube URL is provided.

#### `test_search_title`

This test validates the `search_title` method of the `ProcessYoutubeLink` class. It simulates Spotify API calls and asserts that the method correctly returns a list of conditions and a search title.

#### `test_get_metadata`

This test ensures that the `get_metadata` method of the `ProcessYoutubeLink` class correctly fetches metadata from external sources (Deezer and Genius) for a given YouTube video title.

### FileStorage Unit Tests

#### `test_all`

This test checks the `all` method of the `FileStorage` class, which should return all objects currently stored in memory.

#### `test_new`

This test verifies that the `new` method of the `FileStorage` class correctly adds a new metadata object to memory.

#### `test_save`

This test validates the `save` method of the `FileStorage` class. It confirms that the method serializes objects stored in memory to a JSON file.

#### `test_reload`

This test ensures that the `reload` method of the `FileStorage` class correctly deserializes objects from a JSON file back into memory.

#### `test_get`

This test checks the `get` method of the `FileStorage` class, confirming that it returns the correct object when given a key.

## License

This project is licensed under the terms of the MIT license.

## Disclaimer

Spots is for educational purposes only. It does not promote or encourage the illegal downloading of copyrighted content. Please respect the rights of content creators.
