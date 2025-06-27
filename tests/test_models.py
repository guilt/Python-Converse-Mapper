"""
Tests for data models.
"""

import unittest

from converse_mapper.models import (
    ContentBlock,
    DocumentBlock,
    ImageBlock,
    ImageSource,
    InferenceConfig,
    Message,
    Role,
    StopReason,
    ToolConfig,
    ToolSpecification,
    ToolUseBlock,
    UnifiedRequest,
    VideoBlock,
)


class TestModels(unittest.TestCase):

    def testBasicMessage(self):
        """Test basic message creation."""
        message = Message(role=Role.USER, content=[ContentBlock(text="Hello")])

        self.assertEqual(message.role, Role.USER)
        self.assertEqual(len(message.content), 1)
        self.assertEqual(message.content[0].text, "Hello")

    def testUnifiedRequest(self):
        """Test unified request creation."""
        request = UnifiedRequest(
            messages=[Message(role=Role.USER, content=[ContentBlock(text="Hello")])],
            inferenceConfig=InferenceConfig(maxTokens=100, temperature=0.7),
        )

        self.assertEqual(len(request.messages), 1)
        self.assertEqual(request.inferenceConfig.maxTokens, 100)
        self.assertEqual(request.inferenceConfig.temperature, 0.7)

    def testImageBlock(self):
        """Test image block creation."""
        imageBlock = ImageBlock(
            format="png", source=ImageSource(bytes=b"fake_data", s3Uri="s3://bucket/image.png")
        )

        self.assertEqual(imageBlock.format, "png")
        self.assertEqual(imageBlock.source.bytes, b"fake_data")
        self.assertEqual(imageBlock.source.s3Uri, "s3://bucket/image.png")

    def testDocumentBlock(self):
        """Test document block creation."""
        docBlock = DocumentBlock(name="test.pdf", format="pdf", content="Document content")

        self.assertEqual(docBlock.name, "test.pdf")
        self.assertEqual(docBlock.format, "pdf")
        self.assertEqual(docBlock.content, "Document content")

    def testToolConfiguration(self):
        """Test tool configuration."""
        toolConfig = ToolConfig(
            tools=[
                ToolSpecification(
                    name="calculator",
                    description="A calculator tool",
                    inputSchema={"type": "object", "properties": {"operation": {"type": "string"}}},
                )
            ]
        )

        self.assertEqual(len(toolConfig.tools), 1)
        self.assertEqual(toolConfig.tools[0].name, "calculator")
        self.assertEqual(toolConfig.tools[0].description, "A calculator tool")
        self.assertIn("properties", toolConfig.tools[0].inputSchema)

    def testComplexContentBlock(self):
        """Test content block with multiple types."""
        # Test that only one content type should be set at a time
        textBlock = ContentBlock(text="Hello")
        self.assertEqual(textBlock.text, "Hello")
        self.assertIsNone(textBlock.image)
        self.assertIsNone(textBlock.document)

        imageBlock = ContentBlock(image=ImageBlock(format="png", source=ImageSource(bytes=b"data")))
        self.assertIsNone(imageBlock.text)
        self.assertIsNotNone(imageBlock.image)
        self.assertEqual(imageBlock.image.format, "png")

    def testVideoBlock(self):
        """Test video block creation."""
        videoBlock = VideoBlock(format="mp4", source=ImageSource(s3Uri="s3://bucket/video.mp4"))

        self.assertEqual(videoBlock.format, "mp4")
        self.assertEqual(videoBlock.source.s3Uri, "s3://bucket/video.mp4")

    def testToolUseBlock(self):
        """Test tool use block creation."""
        toolUse = ToolUseBlock(
            toolUseId="tool_123", name="calculator", input={"operation": "add", "a": 1, "b": 2}
        )

        self.assertEqual(toolUse.toolUseId, "tool_123")
        self.assertEqual(toolUse.name, "calculator")
        self.assertEqual(toolUse.input["operation"], "add")
        self.assertEqual(toolUse.input["a"], 1)

    def testEnums(self):
        """Test enum values."""
        self.assertEqual(Role.USER.value, "user")
        self.assertEqual(Role.ASSISTANT.value, "assistant")

        self.assertEqual(StopReason.TURN_END.value, "TURN_END")
        self.assertEqual(StopReason.TOKEN_LIMIT.value, "TOKEN_LIMIT")
        self.assertEqual(StopReason.STOP_SEQUENCE.value, "STOP_SEQUENCE")


if __name__ == "__main__":
    unittest.main()
