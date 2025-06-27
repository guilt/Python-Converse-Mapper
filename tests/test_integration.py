"""
Integration tests for the complete transformation pipeline.
"""

import unittest

from converse_mapper import (
    AudioBlock,
    ContentBlock,
    ImageSource,
    InferenceConfig,
    Message,
    ModelTransformer,
    ProviderResponse,
    Role,
    StopReason,
    ToolResultBlock,
    ToolResultContentBlock,
    UnifiedRequest,
)


class TestIntegration(unittest.TestCase):

    def setUp(self):
        self.transformer = ModelTransformer()

    def testCompleteAi21Pipeline(self):
        """Test complete request -> response pipeline for AI21."""
        # Create request
        request = UnifiedRequest(
            messages=[Message(role=Role.USER, content=[ContentBlock(text="Hello AI")])],
            inferenceConfig=InferenceConfig(maxTokens=25, temperature=0.8),
        )

        # Transform to AI21 format
        providerRequest = self.transformer.transformRequest(request, "ai21")

        # Verify request transformation
        self.assertIn("messages", providerRequest.body)
        self.assertEqual(providerRequest.body["max_tokens"], 25)
        self.assertEqual(providerRequest.body["temperature"], 0.8)

        # Simulate AI21 response
        mockResponse = ProviderResponse(
            body={
                "choices": [
                    {
                        "message": {"content": "Hello human!", "role": "assistant"},
                        "finish_reason": "length",
                    }
                ]
            }
        )

        # Transform response back
        unifiedResponse = self.transformer.transformResponse(mockResponse, "ai21")

        # Verify response transformation
        self.assertEqual(unifiedResponse.message.role, Role.ASSISTANT)
        self.assertEqual(unifiedResponse.message.content[0].text, "Hello human!")
        self.assertEqual(unifiedResponse.stopReason, StopReason.TOKEN_LIMIT)

    def testMultipleProviders(self):
        """Test that same request works with multiple providers."""
        request = UnifiedRequest(
            messages=[Message(role=Role.USER, content=[ContentBlock(text="Test message")])]
        )

        from converse_mapper.models import ModelProvider

        providers = [ModelProvider.AI21, ModelProvider.ANTHROPIC, ModelProvider.META]

        for provider in providers:
            with self.subTest(provider=provider.provider):
                try:
                    result = self.transformer.transformRequest(
                        request, provider.provider, provider.version
                    )
                    self.assertIsInstance(result.body, dict)
                    self.assertTrue(len(result.body) > 0)
                except Exception as e:
                    self.fail(f"Provider {provider} failed: {e}")

    def testAudioBlockModel(self):
        """Test AudioBlock model creation."""
        audio = AudioBlock(format="mp3", source=ImageSource(s3Uri="s3://bucket/audio.mp3"))

        self.assertEqual(audio.format, "mp3")
        self.assertEqual(audio.source.s3Uri, "s3://bucket/audio.mp3")

    def testToolResultBlockModel(self):
        """Test ToolResultBlock model creation."""
        toolResult = ToolResultBlock(
            toolUseId="tool_123",
            content=[
                ToolResultContentBlock(text="Result text"),
                ToolResultContentBlock(json={"result": "success"}),
            ],
            status="success",
        )

        self.assertEqual(toolResult.toolUseId, "tool_123")
        self.assertEqual(len(toolResult.content), 2)
        self.assertEqual(toolResult.content[0].text, "Result text")
        self.assertEqual(toolResult.content[1].json, {"result": "success"})
        self.assertEqual(toolResult.status, "success")

    def testContentBlockWithAudio(self):
        """Test ContentBlock with audio content."""
        audio = AudioBlock(format="wav", source=ImageSource(bytes=b"fake_audio_data"))
        content = ContentBlock(audio=audio)

        self.assertIsNotNone(content.audio)
        self.assertEqual(content.audio.format, "wav")

    def testContentBlockWithToolResult(self):
        """Test ContentBlock with tool result content."""
        toolResult = ToolResultBlock(
            toolUseId="tool_456",
            content=[ToolResultContentBlock(text="Tool completed successfully")],
        )
        content = ContentBlock(toolResult=toolResult)

        self.assertIsNotNone(content.toolResult)
        self.assertEqual(content.toolResult.toolUseId, "tool_456")

    def testRequestWithAudioContent(self):
        """Test transformation request with audio content (should not fail)."""
        request = UnifiedRequest(
            messages=[
                Message(
                    role=Role.USER,
                    content=[
                        ContentBlock(text="Listen to this audio"),
                        ContentBlock(
                            audio=AudioBlock(format="mp3", source=ImageSource(bytes=b"audio_data"))
                        ),
                    ],
                )
            ]
        )

        # Should not raise exception even though audio mapping might not be implemented
        try:
            result = self.transformer.transformRequest(request, "ai21")
            self.assertIsInstance(result.body, dict)
        except Exception as e:
            self.fail(f"Audio content transformation failed: {e}")

    def testRequestWithToolResultContent(self):
        """Test transformation request with tool result content."""
        request = UnifiedRequest(
            messages=[
                Message(
                    role=Role.USER,
                    content=[
                        ContentBlock(
                            toolResult=ToolResultBlock(
                                toolUseId="tool_789",
                                content=[
                                    ToolResultContentBlock(text="Analysis complete"),
                                    ToolResultContentBlock(json={"confidence": 0.95}),
                                ],
                            )
                        )
                    ],
                )
            ]
        )

        # Should handle tool result content
        try:
            result = self.transformer.transformRequest(request, "ai21")
            self.assertIsInstance(result.body, dict)
        except Exception as e:
            self.fail(f"Tool result content transformation failed: {e}")

    def testToolResultContentBlockVariations(self):
        """Test different ToolResultContentBlock variations."""
        # Text content
        text_content = ToolResultContentBlock(text="Success")
        self.assertEqual(text_content.text, "Success")
        self.assertIsNone(text_content.json)

        # JSON content
        json_content = ToolResultContentBlock(json={"status": "ok"})
        self.assertEqual(json_content.json, {"status": "ok"})
        self.assertIsNone(json_content.text)

        # Image content (reusing ImageBlock)
        from converse_mapper import ImageBlock

        image_content = ToolResultContentBlock(
            image=ImageBlock(format="png", source=ImageSource(bytes=b"image_data"))
        )
        self.assertIsNotNone(image_content.image)
        self.assertEqual(image_content.image.format, "png")


if __name__ == "__main__":
    unittest.main()
