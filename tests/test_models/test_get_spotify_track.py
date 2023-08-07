#!/usr/bin/python3
"""Tests the get_spotify_track module"""

from unittest import main, TestCase
from unittest.mock import patch, Mock
from models.errors import InvalidURL
from models.get_spotify_track import GetSpotifyTrack


class TestGetSpotifyTrack(TestCase):
    """Test the GetSpotifyTrack class"""

    def setUp(self):
        self.track_url = 'https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6'
        self.track = GetSpotifyTrack(self.track_url)
        self.mock_track_data = {
            'album': {
                'total_tracks': 10,
                'images': [{'url': 'http://example.com'}],
                'release_date': '2023-01-01',
                'name': 'Mock Album'
            },
            'name': 'Mock Track',
            'artists': [{'name': 'Mock Artist'}],
            'track_number': 1,
            'external_urls': {'spotify': self.track_url}
        }
        self.mock_lyrics = 'Mock Lyrics\nVerse 1:...'

    @patch('models.get_spotify_track.GetSpotifyTrack.spotify.track')
    @patch('models.get_spotify_track.GetSpotifyTrack.genius.search_song')
    def test_get_track(self, mock_search_song, mock_track):
        mock_track.return_value = self.mock_track_data
        mock_search_song.return_value = Mock(
            lyrics=self.mock_lyrics, title='Mock Track')

        result = self.track.get_track('6rqhFgbbKwnb9MLmUQDhG6')

        self.assertEqual(result['title'], 'Mock Track')
        self.assertEqual(result['cover'], 'http://example.com')
        self.assertEqual(result['artist'], 'Mock Artist')
        self.assertEqual(result['tracknumber'], '1/10')
        self.assertEqual(result['album'], 'Mock Album')
        self.assertEqual(result['lyrics'], self.mock_lyrics)
        self.assertEqual(result['release_date'], '2023')
        self.assertEqual(result['link'], self.track_url)

    @patch('models.get_spotify_track.GetSpotifyTrack.get_track')
    def test_process_url_with_invalid_url(self, mock_get_track):
        mock_get_track.side_effect = InvalidURL
        with self.assertRaises(InvalidURL):
            self.track.get_track('invalidId')

    @patch('models.get_spotify_track.GetSpotifyTrack.spotify.track')
    @patch('models.get_spotify_track.GetSpotifyTrack.spotify.playlist')
    @patch('models.get_spotify_track.GetSpotifyTrack.genius.search_song')
    def test_process_url_with_playlist(self, mock_search_song, mock_playlist, mock_track):
        mock_track_data = {
            'tracks': {
                'items': [
                    {
                        'track': { 'id': '6rqhFgbbKwnb9MLmUQDhG6'}
                    }
                ]
            },
            'name': 'Mock Album',
        }

        mock_track.return_value = self.mock_track_data
        mock_playlist.return_value = mock_track_data
        mock_search_song.return_value = Mock(
            lyrics=self.mock_lyrics, title='Mock Track')

        self.track.track_url = 'https://open.spotify.com/playlist/4a9gZUsMoQoLoZGB1JeExu?si=08a6190d929847ac'
        result = self.track.process_url()

        self.assertIsInstance(result, tuple)

        self.assertEqual(result[0][0]['title'], 'Mock Track')
        self.assertEqual(result[0][0]['cover'], 'http://example.com')
        self.assertEqual(result[0][0]['artist'], 'Mock Artist')
        self.assertEqual(result[0][0]['tracknumber'], '1/10')
        self.assertEqual(result[0][0]['album'], 'Mock Album')
        self.assertEqual(result[0][0]['lyrics'], self.mock_lyrics)
        self.assertEqual(result[0][0]['release_date'], '2023')
        self.assertEqual(result[0][0]['link'], self.track_url)

        self.assertEqual(result[1], 'Mock Album')

    @patch('models.get_spotify_track.GetSpotifyTrack.spotify.track')
    @patch('models.get_spotify_track.GetSpotifyTrack.spotify.album')
    @patch('models.get_spotify_track.GetSpotifyTrack.genius.search_song')
    def test_process_url_with_album(self, mock_search_song, mock_album, mock_track):
        mock_track_data = {
            'tracks': {
                'items': [
                    { 'id': '6rqhFgbbKwnb9MLmUQDhG6'}
                ]
            },
            'name': 'Mock Album',
        }

        mock_track.return_value = self.mock_track_data
        mock_album.return_value = mock_track_data
        mock_search_song.return_value = Mock(
            lyrics=self.mock_lyrics, title='Mock Track')

        self.track.track_url = 'https://open.spotify.com/album/4jJCOc3LIu8xUUhrXYs86E?si=axqLH0wzTlSSvULIQxz81g'
        result = self.track.process_url()

        self.assertIsInstance(result, tuple)

        self.assertEqual(result[0][0]['title'], 'Mock Track')
        self.assertEqual(result[0][0]['cover'], 'http://example.com')
        self.assertEqual(result[0][0]['artist'], 'Mock Artist')
        self.assertEqual(result[0][0]['tracknumber'], '1/10')
        self.assertEqual(result[0][0]['album'], 'Mock Album')
        self.assertEqual(result[0][0]['lyrics'], self.mock_lyrics)
        self.assertEqual(result[0][0]['release_date'], '2023')
        self.assertEqual(result[0][0]['link'], self.track_url)

        self.assertEqual(result[1], 'Mock Album')

    @patch('models.get_spotify_track.GetSpotifyTrack.spotify.track')
    @patch('models.get_spotify_track.GetSpotifyTrack.genius.search_song')
    def test_process_url_with_single(self, mock_search_song, mock_track):
        mock_track.return_value = self.mock_track_data
        mock_search_song.return_value = Mock(
            lyrics=self.mock_lyrics, title='Mock Track')

        result = self.track.process_url()

        self.assertEqual(result['title'], 'Mock Track')
        self.assertEqual(result['cover'], 'http://example.com')
        self.assertEqual(result['artist'], 'Mock Artist')
        self.assertEqual(result['tracknumber'], '1/10')
        self.assertEqual(result['album'], 'Mock Album')
        self.assertEqual(result['lyrics'], self.mock_lyrics)
        self.assertEqual(result['release_date'], '2023')
        self.assertEqual(result['link'], self.track_url)


if __name__ == '__main__':
    main()
