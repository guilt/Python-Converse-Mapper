"""
Simple tests for the transformer.
Much easier to test than the original complex implementation.
"""

import unittest

from converse_mapper.models import (
    ContentBlock,
    InferenceConfig,
    Message,
    ProviderRequest,
    ProviderResponse,
    Role,
    StopReason,
    UnifiedRequest,
    UnifiedResponse,
)
from converse_mapper.transformer import ModelTransformer


class TestTransformer(unittest.TestCase):

    def setUp(self):
        self.transformer = ModelTransformer()

    def testAi21RequestTransformation(self):
        """Test transforming a request to AI21 format."""
        request = UnifiedRequest(
            messages=[Message(role=Role.USER, content=[ContentBlock(text="Hello world")])],
            inferenceConfig=InferenceConfig(maxTokens=50, temperature=0.5),
        )

        result = self.transformer.transformRequest(request, "ai21")

        # Check the basic structure
        self.assertIn("messages", result.body)
        self.assertIn("max_tokens", result.body)
        self.assertIn("temperature", result.body)
        self.assertEqual(result.body["max_tokens"], 50)
        self.assertEqual(result.body["temperature"], 0.5)

    def testAi21ResponseTransformation(self):
        """Test transforming an AI21 response to unified format."""
        response = ProviderResponse(
            body={
                "choices": [
                    {
                        "message": {"content": "Hello back!", "role": "assistant"},
                        "finish_reason": "length",
                    }
                ]
            }
        )

        result = self.transformer.transformResponse(response, "ai21")

        self.assertEqual(result.message.role, Role.ASSISTANT)
        self.assertEqual(result.message.content[0].text, "Hello back!")
        self.assertEqual(result.stopReason.value, "TOKEN_LIMIT")

    def testResponseTransformationFallback(self):
        """Test response transformation fallback when no mapper handles response."""
        # Create response that no mapper will handle
        response = ProviderResponse(body={"unknown": "format"})

        result = self.transformer.transformResponse(response, "ai21")

        # Should return fallback response
        self.assertIsInstance(result, UnifiedResponse)
        self.assertEqual(result.message.role, Role.ASSISTANT)
        self.assertEqual(result.stopReason, StopReason.UNKNOWN)

    def testTransformRequestForModel(self):
        """Test transformRequestForModel method with ModelProvider enum."""
        from converse_mapper.models import ModelProvider

        request = UnifiedRequest(
            messages=[Message(role=Role.USER, content=[ContentBlock(text="Hello")])]
        )

        result = self.transformer.transformRequestForModel(request, ModelProvider.AI21)
        self.assertIsInstance(result, ProviderRequest)
        self.assertIsInstance(result.body, dict)

    def testTransformResponseForModel(self):
        """Test transformResponseForModel method with ModelProvider enum."""
        from converse_mapper.models import ModelProvider

        response = ProviderResponse(body={"unknown": "format"})
        result = self.transformer.transformResponseForModel(response, ModelProvider.AI21)

        self.assertIsInstance(result, UnifiedResponse)
        self.assertEqual(result.stopReason, StopReason.UNKNOWN)

    def testResponseMapperException(self):
        """Test exception handling in response mapper loop."""

        # Create a mock mapper that raises an exception
        class FailingMapper:
            def mapResponse(self, response, config, reader):
                raise ValueError("Test exception")

        # Add failing mapper to test exception handling
        original_mappers = self.transformer.responseMappers
        self.transformer.responseMappers = [FailingMapper()] + original_mappers

        response = ProviderResponse(body={"test": "data"})
        result = self.transformer.transformResponse(response, "ai21")

        # Should still return fallback response despite exception
        self.assertEqual(result.stopReason, StopReason.UNKNOWN)

        # Restore original mappers
        self.transformer.responseMappers = original_mappers


if __name__ == "__main__":
    unittest.main()
