#!/usr/bin/python3
"""Tests the spotify_to_youtube module"""

from os import path, remove
from unittest import TestCase, main
from unittest.mock import patch, MagicMock, Mock, mock_open
from models.errors import TitleExistsError, InvalidURL
from mutagen.id3 import ID3
from models.spotify_to_youtube import ProcessSpotifyLink


class TestProcessSpotifyLink(TestCase):

    def setUp(self):
        self.title = 'Lakeyah - Mind Yo Business (feat. Latto)'
        self.spotify_track = {
            "title": "Mind Yo Business (feat. Latto)",
            "cover": "https://i.scdn.co/image/ab67616d0000b2735d3f520fe42974fea09ee5c9",
            "artist": "Lakeyah",
            "tracknumber": "2/5",
            "album": "No Pressure (Pt. 1)",
            "lyrics": None,
            "release_date": "2022-%",
            "link": "https://open.spotify.com/track/0vf5rFpdpHnRh3hUQNqZJg",
            "genre": ""
        }
        self.history_file = '.spots_download_history.txt'
        self.youtube_url = 'https://youtu.be/4hCogXAzONk'
        self.process_spotify_link = ProcessSpotifyLink(
            self.spotify_track, self.youtube_url)

    def tearDown(self):
        """Remove any test files"""
        history_file = ".spots_download_history.txt"
        if path.exists(history_file):
            remove(history_file)

    @patch("models.spotify_to_youtube.open", new_callable=mock_open)
    def test_add_to_download_history(self, mock_file):
        """Tests adding titles to download history"""
        # Setup the mock file to have some content (existing titles)
        mock_file.return_value.read.return_value = "Title 1\nTitle 2\nTitle 3\n"

        # Test adding a new title to the history
        new_title = "New Title"
        self.process_spotify_link.add_to_download_history(new_title, True)

        # Ensure the file was opened in append mode and the new title was written
        mock_file.assert_called_with(
            ".spots_download_history.txt", "a", newline="")

        # Test adding an existing title, should raise TitleExistsError
        existing_title = "Title 2"
        with self.assertRaises(TitleExistsError):
            self.process_spotify_link.add_to_download_history(
                existing_title, True)

        # Ensure the file was not opened in append mode (since we're not adding a new title)
        mock_file.assert_called_with(".spots_download_history.txt", "r")

    @patch("models.spotify_to_youtube.get")
    @patch("models.spotify_to_youtube.MP3")
    def test_update_metadata(self, mock_mp3, mock_get):
        """tests that method updates metadata tags on mp3 file"""
        test_path = 'test_file.mp3'

        # Create a mock ID3 and image objects
        audio_mock = Mock(spec=ID3)
        cover_mock = b""

        # set return values
        mock_get.return_value.content = cover_mock
        mock_mp3.return_value = audio_mock

        self.process_spotify_link.update_metadata(test_path)

        audio_mock.save.assert_called_once_with(test_path)

    @patch("models.spotify_to_youtube.VideosSearch")
    def test_get_youtube_video(self, mock_video_search):
        """method should return the first url for a title search on youtube"""
        mock_result = MagicMock()
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        mock_result.result.return_value = {'result': [{'link': url}]}
        mock_video_search.return_value = mock_result
        result = self.process_spotify_link.get_youtube_video("Test Title")
        self.assertEqual(result, url)

    @patch('models.spotify_to_youtube.getenv')
    @patch('models.spotify_to_youtube.YouTube')
    @patch('models.spotify_to_youtube.ProcessSpotifyLink.convert_to_mp3')
    def test_download_youtube_video(
        self,
        mock_convert_to_mp3,
        mock_youtube,
        mock_getenv
    ):
        """tests that method downloads youtube video and converts it"""
        # create mock instances
        mock_youtube_instance = MagicMock()
        mock_audio_stream = MagicMock()

        # set required values
        mock_youtube.return_value = mock_youtube_instance
        mock_audio_stream.mime_type = 'audio/mp4'
        mock_youtube_instance.streams.get_audio_only.return_value = mock_audio_stream
        mock_getenv.return_value = None

        # action
        self.process_spotify_link.download_youtube_video()

        # assertions
        mock_youtube.assert_called_once_with(self.youtube_url, use_oauth=False)
        audio = mock_youtube_instance.streams.get_audio_only
        audio.assert_called_once_with()

        # should download to a file name based on title
        audio.return_value.download.assert_called_once_with(
            output_path='', filename=f'{self.title}.mp4'
        )
        # and convert it to mp3
        mock_convert_to_mp3.assert_called_once_with(
            f'{self.title}.mp4',
            f'{self.title}.mp3',
            self.title
        )

    @patch('models.spotify_to_youtube.getenv')
    @patch('models.spotify_to_youtube.md5')
    @patch('models.spotify_to_youtube.YouTube')
    @patch('models.spotify_to_youtube.ProcessSpotifyLink.convert_to_mp3')
    def test_download_youtube_video_with_long_title(
            self,
            mock_convert_to_mp3,
            mock_youtube,
            mock_hash,
            mock_getenv
    ):
        """tests that method converts a long title to a shortened hash"""
        # create mock instances
        mock_youtube_instance = MagicMock()
        mock_audio_stream = MagicMock()
        mock_hash_instance = MagicMock()
        hex_digest = 'a6f61ef8f5423c8d99e3f7f83f4ccd48'

        # set required values
        mock_youtube.return_value = mock_youtube_instance
        mock_audio_stream.mime_type = 'audio/mp4'
        mock_youtube_instance.streams.get_audio_only.return_value = mock_audio_stream
        mock_hash_instance.hexdigest.return_value = hex_digest
        mock_hash.return_value = mock_hash_instance
        mock_getenv.return_value = None

        # create a long title
        title = self.spotify_track['title']
        long_title = f'{title}{"a" * 256}'
        self.spotify_track.__setitem__('title', long_title)

        # action
        self.process_spotify_link.download_youtube_video()

        # assertions
        mock_youtube.assert_called_once_with(self.youtube_url, use_oauth=False)
        audio = mock_youtube_instance.streams.get_audio_only
        audio.assert_called_once_with()

        # should download to a file name based on title
        audio.return_value.download.assert_called_once_with(
            output_path='', filename=f'{hex_digest[:25]}.mp4'
        )
        # and convert it to mp3
        mock_convert_to_mp3.assert_called_once_with(
            f'{hex_digest[:25]}.mp4',
            f'{hex_digest[:25]}.mp3',
            f'Lakeyah - {long_title}'
        )

    @patch('models.spotify_to_youtube.YouTube')
    @patch('models.spotify_to_youtube.ProcessSpotifyLink.convert_to_mp3')
    def test_download_youtube_video_no_url(self, mock_convert_to_mp3, mock_youtube):
        """tests that method does nothing when no youtube url is provided"""
        self.process_spotify_link.youtube_url = None

        self.process_spotify_link.download_youtube_video()

        mock_youtube.assert_not_called()
        mock_convert_to_mp3.assert_not_called()

    @patch('models.spotify_to_youtube.YouTube')
    def test_download_youtube_video_invalid_url(self, mock_youtube):
        """tests that method raises error when invalid youtube url is provided"""
        self.process_spotify_link.youtube_url = 'https://youtu.be/invalidId'
        mock_youtube.return_value.check_availability.side_effect = Exception

        with self.assertRaises(InvalidURL):
            self.process_spotify_link.download_youtube_video()

    @patch('models.spotify_to_youtube.AudioFileClip')
    @patch('models.spotify_to_youtube.ProcessSpotifyLink.update_metadata')
    def test_convert_to_mp3(self, mock_update_metadata, mock_audio_clip):
        """tests that method converts audio file to mp3"""
        mock_audio = MagicMock()
        mock_audio_clip.return_value = mock_audio
        old_file = 'file.wav'
        new_file = 'file.mp3'
        song_title = 'Mock Song Title'

        mock_update_metadata.side_effect = lambda *args, **kwargs: None

        self.process_spotify_link.convert_to_mp3(
            old_file, new_file, song_title)

        mock_audio.write_audiofile.assert_called_once_with(
            new_file, codec='mp3')


if __name__ == '__main__':
    main()
