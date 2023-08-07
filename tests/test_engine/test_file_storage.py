#!/usr/bin/python3
"""Tests the file_storage module"""

import unittest
from engine.file_storage import FileStorage
import os


class TestFileStorage(unittest.TestCase):

    def setUp(self):
        """Set up test methods"""
        self.storage = FileStorage()
        self.link = 'https://open.spotify.com/track/7uZObZTHwL3DbEx05TXSRh'
        self.test_dict = {
            "title": "Funeral (feat. Lil' Kim)",
            "cover": "https://i.scdn.co/image/ab67616d0000b27329e356286b54b9287fca38eb",
            "artist": "DreamDoll",
            "tracknumber": "4/10",
            "album": "Life In Plastic 2",
            "lyrics": "",
            "release_date": "2019",
            "link": "https://open.spotify.com/track/7uZObZTHwL3DbEx05TXSRh",
            "genre": ""
        }

    def tearDown(self):
        """Tear down test methods"""
        try:
            os.remove(".metadata.json")
        except:
            pass

    def test_all(self):
        """Test all method"""
        self.assertEqual(self.storage.all(), {})

    def test_new(self):
        """Test new method"""
        self.storage.new(self.test_dict)
        self.assertIn(self.link, self.storage.all())

    def test_save(self):
        """Test save method"""
        self.storage.new(self.test_dict)
        self.storage.save()
        self.assertTrue(os.path.exists(".metadata.json"))

    def test_reload(self):
        """Test reload method"""
        self.storage.new(self.test_dict)
        self.storage.save()
        storage2 = FileStorage()
        storage2.reload()
        self.assertEqual(self.storage.all(), storage2.all())

    def test_get(self):
        """Test get method"""
        self.storage.new(self.test_dict)
        obj = self.storage.get(self.link)
        self.assertEqual(obj, self.test_dict)


if __name__ == '__main__':
    unittest.main()
