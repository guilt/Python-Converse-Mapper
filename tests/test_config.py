"""
Tests for configuration loading.
"""

import os
import tempfile
import unittest

from converse_mapper.config import ConfigLoader


class TestConfigLoader(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.config_loader = ConfigLoader(self.temp_dir)

    def tearDown(self):
        import shutil

        shutil.rmtree(self.temp_dir)

    def testLoadYamlConfig(self):
        """Test loading YAML configuration."""
        # Create test YAML config
        provider_dir = os.path.join(self.temp_dir, "test_provider")
        os.makedirs(provider_dir)

        yaml_content = """
provider: test_provider
version: 1
requestMapping:
  messageMappings:
    user:
      textMapping:
        pointer: /prompt
responseMapping:
  resultMapping:
    outputMapping:
      messageMapping:
        roleMapping:
          overrideValue: assistant
"""

        config_path = os.path.join(provider_dir, "v1.yml")
        with open(config_path, "w") as f:
            f.write(yaml_content)

        config = self.config_loader.loadConfig("test_provider", 1)

        self.assertEqual(config.provider, "test_provider")
        self.assertEqual(config.version, 1)
        self.assertIn("messageMappings", config.requestMapping)

    def testLoadJsonConfig(self):
        """Test loading JSON configuration."""
        provider_dir = os.path.join(self.temp_dir, "json_provider")
        os.makedirs(provider_dir)

        json_content = """{
  "provider": "json_provider",
  "version": 1,
  "requestMapping": {
    "messageMappings": {
      "user": {
        "textMapping": {
          "pointer": "/text"
        }
      }
    }
  },
  "responseMapping": {
    "resultMapping": {}
  }
}"""

        config_path = os.path.join(provider_dir, "v1.json")
        with open(config_path, "w") as f:
            f.write(json_content)

        config = self.config_loader.loadConfig("json_provider", 1)

        self.assertEqual(config.provider, "json_provider")
        self.assertEqual(config.version, 1)

    def testConfigNotFound(self):
        """Test error when config file not found."""
        with self.assertRaises(FileNotFoundError):
            self.config_loader.loadConfig("nonexistent", 1)

    def testConfigCaching(self):
        """Test that configs are cached properly."""
        provider_dir = os.path.join(self.temp_dir, "cache_test")
        os.makedirs(provider_dir)

        yaml_content = """
provider: cache_test
version: 1
requestMapping: {}
responseMapping: {}
"""

        config_path = os.path.join(provider_dir, "v1.yml")
        with open(config_path, "w") as f:
            f.write(yaml_content)

        # Load twice - should use cache second time
        config1 = self.config_loader.loadConfig("cache_test", 1)
        config2 = self.config_loader.loadConfig("cache_test", 1)

        # Should be same object due to caching
        self.assertIs(config1, config2)


if __name__ == "__main__":
    unittest.main()
