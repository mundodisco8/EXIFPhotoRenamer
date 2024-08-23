import unittest

from massRenamer.massRenamerClasses import *

class TestgetFileSource(unittest.TestCase):
    def test_getFileSource_ModelOneTag(self):
        """
        Success when the EXIF data has only one "Model" tag
        """
        self.assertEqual(getFileSource({"EXIF:Model": "Device X"}), "Device X")

    def test_getFileSource_ModelManyTagsSameValue(self):
        """
        Success when the EXIF data has two or more "Model" tags, with same value
        """
        self.assertEqual(getFileSource({"EXIF:Model": "Device X", "XMP:Model": "Device X"}), "Device X")
        self.assertEqual(getFileSource({"EXIF:Model": "Device X", "XMP:Model": "Device X", "Something:Model": "Device X", "Silly:Model": "Device X"}), "Device X")

    # def test_getFileSource_ModelManyTagsDiffValue(self):
    #     self.assertRaises(Exception, getFileSource({"EXIF:Model": "Device X", "XMP:Model": "Device Y"}))
if __name__ == '__main__':
    unittest.main()