#!/usr/bin/python3
"""
Contains the FileStorage class
"""

import json


class FileStorage:
    """serializes instances to a JSON file & deserializes back to instances"""

    # string - path to the JSON file
    __file_path = ".metadata.json"
    # dictionary - empty but will store all objects by Artist
    __objects = {}

    def all(self):
        """returns the dictionary __objects"""
        return self.__objects

    def new(self, obj):
        """sets in __objects the obj with key <obj artist name>.<obj title name>"""
        if obj is not None:
            key = obj['link']
            self.__objects[key] = obj

    def save(self):
        """serializes __objects to the JSON file (path: __file_path)"""
        with open(self.__file_path, 'w') as f:
            json.dump(self.__objects, f, indent=4)

    def reload(self):
        """deserializes the JSON file to __objects"""
        try:
            with open(self.__file_path, 'r') as f:
                jo = json.load(f)
            for key in jo:
                self.__objects[key] = jo[key]
        except:
            pass

    def close(self):
        """call reload() method for deserializing the JSON file to objects"""
        self.reload()

    def get(self, url):
        """
        Returns the object based on the url, or None if not found
        """
        return self.__objects.get(url, None)
