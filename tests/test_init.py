"""
Tests for __init__.py module imports.
"""

import sys
import unittest
from unittest.mock import patch


class TestInit(unittest.TestCase):

    def testImportErrorHandling(self):
        """Test that ImportError for bedrock_client is handled gracefully."""
        # Mock ImportError for bedrock_client
        with patch.dict("sys.modules", {"converse_mapper.bedrock_client": None}):
            # Force reimport to trigger ImportError handling
            if "converse_mapper" in sys.modules:
                del sys.modules["converse_mapper"]

            # This should not raise an exception
            import converse_mapper

            # Basic imports should still work
            self.assertTrue(hasattr(converse_mapper, "ModelTransformer"))
            self.assertTrue(hasattr(converse_mapper, "UnifiedRequest"))

            # Bedrock client should not be available
            self.assertFalse(hasattr(converse_mapper, "BedrockConverseClient"))

    def testNormalImports(self):
        """Test that normal imports work correctly."""
        import converse_mapper

        # Check that all expected classes are available
        expected_classes = [
            "UnifiedRequest",
            "UnifiedResponse",
            "ModelTransformer",
            "ModelProvider",
            "Role",
            "StopReason",
        ]

        for class_name in expected_classes:
            self.assertTrue(hasattr(converse_mapper, class_name))


if __name__ == "__main__":
    unittest.main()
