#!/usr/bin/python3
"""Testing the youtube_to_spotify module"""

from datetime import datetime
import unittest
from unittest.mock import patch, MagicMock, Mock
from models.errors import InvalidURL
from models.youtube_to_spotify import ProcessYoutubeLink


class TestProcessYoutubeLink(unittest.TestCase):

    def setUp(self):
        """create test objects for all tests"""
        self.youtube_url = 'https://youtu.be/4wKFIBmefiY'
        self.title = "BIA - CAN'T TOUCH THIS"

    @patch('models.youtube_to_spotify.YouTube')
    def test_get_title(self, mock_youtube):
        """Tests that the get_title method returns a title to be searched for"""
        mock_youtube.return_value.author = "BIA"
        mock_youtube.return_value.title = "CAN'T TOUCH THIS"

        proc_yt_link = ProcessYoutubeLink(self.youtube_url)
        search_title, youtube_video_title = proc_yt_link.get_title()
        self.assertEqual(search_title, self.title)
        self.assertEqual(youtube_video_title, "CAN'T TOUCH THIS")

    @patch('models.youtube_to_spotify.YouTube')
    def test_get_title_raises_error(self, mock_youtube):
        """Tests that the get_title method raises an InvalidURL exception with an url"""
        mock_youtube.return_value.check_availability.side_effect = InvalidURL

        youtube_url = 'https://youtu.be/5wKFIBmefiY'

        proc_yt_link = ProcessYoutubeLink(youtube_url)
        with self.assertRaises(InvalidURL):
            proc_yt_link.get_title()

    @patch('models.youtube_to_spotify.GetSpotifyTrack.spotify.search')
    @patch('models.youtube_to_spotify.ProcessYoutubeLink.search_title')
    def test_search_title(self, mock_search, mock_spotify):
        """Test that the search_title method returns a list of booleans and a search string"""
        # mock api response
        mock_response = {
            'tracks': {
                'items': [
                    {
                        'name': "CAN'T TOUCH THIS",
                        'external_urls': {
                            'spotify': 'https://spotify.track.mock'
                        }
                    }
                ]
            }
        }

        # set return values
        mock_spotify.return_value = mock_response
        mock_search.return_value = ([True, True], self.title)

        # action
        proc_yt_link = ProcessYoutubeLink(self.youtube_url)
        condition, search_title = proc_yt_link.search_title()

        # assertions
        self.assertEqual(search_title, self.title)
        self.assertListEqual(condition, [True, True])

    @patch('models.get_spotify_track.GetSpotifyTrack.genius.search_song')
    @patch('models.youtube_to_spotify.ProcessYoutubeLink.deezer_client.search')
    def test_get_metadata(self, mock_deezer, mock_genius):
        """Tests that the get_metadata method returns a dict with metadata"""
        # create mock instances
        deezer_response = MagicMock()
        mock_genius.return_value = Mock(
            lyrics="Mock Lyrics\nVerse 1...", title="CAN'T TOUCH THIS")

        # set required properties
        deezer_response.title = "CAN'T TOUCH THIS"
        deezer_response.album.cover = "https://example.mock"
        deezer_response.artist.name = "BIA"
        deezer_response.track_position = 1
        deezer_response.album.nb_tracks = 12
        deezer_response.album.title = "CAN'T TOUCH THIS"
        deezer_response.album.release_date = datetime.strptime("2023", "%Y")

        # set return value
        mock_deezer.return_value = [deezer_response]

        # action
        proc_yt_link = ProcessYoutubeLink(self.youtube_url)
        metadata = proc_yt_link.get_metadata(self.title, self.youtube_url)

        self.assertEqual(metadata['title'], "CAN'T TOUCH THIS")
        self.assertEqual(metadata['cover'], 'https://example.mock')
        self.assertEqual(metadata['artist'], 'BIA')
        self.assertEqual(metadata['tracknumber'], '1/12')
        self.assertEqual(metadata['album'], "CAN'T TOUCH THIS")
        self.assertEqual(metadata['lyrics'], 'Mock Lyrics\nVerse 1...')
        self.assertEqual(metadata['release_date'], '2023')
        self.assertEqual(metadata['link'], self.youtube_url)
        self.assertEqual(metadata['genre'], '')


if __name__ == '__main__':
    unittest.main()
