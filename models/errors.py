#!/usr/bin/python3
"""Custom error classes"""

class MetadataNotFound(Exception):
  """No metadata found for song"""
  pass

class TitleExistsError(Exception):
    """File already downloaded"""
    pass

class InvalidURL(Exception):
    """Url not valid"""
    pass

class NoSearchResult(Exception):
    """No result found for title"""
    pass
