"""
Tests for Bedrock client functionality.
"""

import unittest
from unittest.mock import patch

from converse_mapper.models import ContentBlock, Message, Role, UnifiedRequest


class TestBedrockClient(unittest.TestCase):

    def testImportWithoutBoto3(self):
        """Test that import fails gracefully without boto3."""
        # This test verifies the import error handling
        try:
            from converse_mapper.bedrock_client import BedrockConverseClient

            # If we get here, boto3 is available
            self.assertTrue(hasattr(BedrockConverseClient, "invoke"))
        except ImportError:
            # Expected when boto3 not available
            pass

    @patch("converse_mapper.bedrock_client.HAS_BOTO3", True)
    def testSimpleHttpClient(self):
        """Test SimpleHttpClient basic functionality."""
        try:
            from converse_mapper.bedrock_client import SimpleHttpClient

            client = SimpleHttpClient()

            # Test basic request structure
            _ = UnifiedRequest(
                messages=[Message(role=Role.USER, content=[ContentBlock(text="Hello")])]
            )

            # Should not crash when creating client
            self.assertIsNotNone(client)

        except ImportError:
            # Skip test if boto3 not available
            self.skipTest("boto3 not available")

    def testClientCreationWithoutBoto3(self):
        """Test client creation fails properly without boto3."""
        with patch("converse_mapper.bedrock_client.HAS_BOTO3", False):
            with self.assertRaises(ImportError):
                from converse_mapper.bedrock_client import BedrockConverseClient

                BedrockConverseClient()


if __name__ == "__main__":
    unittest.main()
