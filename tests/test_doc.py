"""
Tests for configuration utilities.
"""

import unittest

from converse_mapper.doc import DocBuilder, DocReader


class TestDocUtils(unittest.TestCase):

    def testDocBuilderBasic(self):
        """Test basic document building."""
        builder = DocBuilder()
        builder.setValue("/name", "test")
        builder.setValue("/age", 25)

        result = builder.getResult()
        self.assertEqual(result["name"], "test")
        self.assertEqual(result["age"], 25)

    def testDocBuilderNested(self):
        """Test nested path building."""
        builder = DocBuilder()
        builder.setValue("/user/profile/name", "John")
        builder.setValue("/user/profile/age", 30)
        builder.setValue("/user/settings/theme", "dark")

        result = builder.getResult()
        self.assertEqual(result["user"]["profile"]["name"], "John")
        self.assertEqual(result["user"]["profile"]["age"], 30)
        self.assertEqual(result["user"]["settings"]["theme"], "dark")

    def testDocBuilderAppend(self):
        """Test append mode."""
        builder = DocBuilder()
        builder.setValue("/message", "Hello", append=False)
        builder.setValue("/message", " World", append=True)

        result = builder.getResult()
        self.assertEqual(result["message"], "Hello World")

    def testDocBuilderPrefixSuffix(self):
        """Test prefix and suffix."""
        builder = DocBuilder()
        builder.setValue("/greeting", "World", prefix="Hello ", suffix="!")

        result = builder.getResult()
        self.assertEqual(result["greeting"], "Hello World!")

    def testDocReaderBasic(self):
        """Test basic document reading."""
        data = {"name": "test", "age": 25}
        reader = DocReader(data)

        self.assertEqual(reader.getValue("/name"), "test")
        self.assertEqual(reader.getValue("/age"), 25)
        self.assertIsNone(reader.getValue("/missing"))

    def testDocReaderNested(self):
        """Test nested path reading."""
        data = {"user": {"profile": {"name": "John", "age": 30}, "settings": {"theme": "dark"}}}
        reader = DocReader(data)

        self.assertEqual(reader.getValue("/user/profile/name"), "John")
        self.assertEqual(reader.getValue("/user/settings/theme"), "dark")
        self.assertIsNone(reader.getValue("/user/missing/field"))

    def testDocReaderArrays(self):
        """Test array index reading."""
        data = {"items": [{"name": "first"}, {"name": "second"}]}
        reader = DocReader(data)

        self.assertEqual(reader.getValue("/items/0/name"), "first")
        self.assertEqual(reader.getValue("/items/1/name"), "second")
        self.assertIsNone(reader.getValue("/items/2/name"))

    def testDocReaderValueMap(self):
        """Test value mapping."""
        data = {"status": "active"}
        reader = DocReader(data)

        valueMap = {"active": "ENABLED", "inactive": "DISABLED"}
        result = reader.getValue("/status", valueMap=valueMap, defaultValue="UNKNOWN")

        self.assertEqual(result, "ENABLED")

        # Test default value
        data2 = {"status": "unknown_status"}
        reader2 = DocReader(data2)
        result2 = reader2.getValue("/status", valueMap=valueMap, defaultValue="UNKNOWN")

        self.assertEqual(result2, "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
