"""
Comprehensive tests for all content mappers.
"""

import base64
import unittest

from converse_mapper.config import TransformationConfig
from converse_mapper.content_mappers import DocumentMapper, ImageMapper, ToolMapper, VideoMapper
from converse_mapper.doc import DocBuilder, DocReader
from converse_mapper.models import (
    ContentBlock,
    DocumentBlock,
    ImageBlock,
    ImageSource,
    Message,
    Role,
    ToolConfig,
    ToolSpecification,
    ToolUseBlock,
    UnifiedRequest,
    VideoBlock,
)


class TestContentMappers(unittest.TestCase):

    def setUp(self):
        self.builder = DocBuilder()
        self.mockConfig = TransformationConfig(
            provider="test",
            version=1,
            requestMapping={
                "messageMappings": {
                    "user": {
                        "imageBlockMapping": {
                            "formatMapping": {"pointer": "/image/format", "prefix": "image/"},
                            "bytesMapping": {"pointer": "/image/data"},
                        },
                        "videoBlockMapping": {
                            "formatMapping": {"pointer": "/video/format"},
                            "s3UriMapping": {"pointer": "/video/s3_uri"},
                        },
                        "documentsMapping": {
                            "documentBlockMapping": {
                                "indexMapping": {"pointer": "/docs/index", "prefix": "doc_"},
                                "nameMapping": {"pointer": "/docs/name"},
                                "contentMapping": {"pointer": "/docs/content"},
                            },
                            "startAttributes": [
                                {"pointer": "/docs/start", "overrideValue": "<docs>"}
                            ],
                            "endAttributes": [{"pointer": "/docs/end", "overrideValue": "</docs>"}],
                        },
                        "toolUseBlockMapping": {
                            "toolUseIdMapping": {"pointer": "/tool_use/id"},
                            "nameMapping": {"pointer": "/tool_use/name"},
                            "inputMapping": {"pointer": "/tool_use/input"},
                        },
                    }
                },
                "toolConfigMapping": {
                    "toolSpecMapping": {
                        "nameMapping": {"pointer": "/tools/name"},
                        "descriptionMapping": {"pointer": "/tools/description"},
                    }
                },
            },
            responseMapping={},
        )

    def testImageMapper(self):
        """Test image content mapping."""
        imageData = b"fake_image_data"
        request = UnifiedRequest(
            messages=[
                Message(
                    role=Role.USER,
                    content=[
                        ContentBlock(
                            image=ImageBlock(format="png", source=ImageSource(bytes=imageData))
                        )
                    ],
                )
            ]
        )

        mapper = ImageMapper()
        mapper.mapRequest(request, self.mockConfig, self.builder)

        result = self.builder.getResult()
        self.assertEqual(result["image"]["format"], "image/png")

        # Check base64 encoding
        expectedEncoded = base64.b64encode(imageData).decode("utf-8")
        self.assertEqual(result["image"]["data"], expectedEncoded)

    def testVideoMapper(self):
        """Test video content mapping."""
        request = UnifiedRequest(
            messages=[
                Message(
                    role=Role.USER,
                    content=[
                        ContentBlock(
                            video=VideoBlock(
                                format="mp4", source=ImageSource(s3Uri="s3://bucket/video.mp4")
                            )
                        )
                    ],
                )
            ]
        )

        mapper = VideoMapper()
        mapper.mapRequest(request, self.mockConfig, self.builder)

        result = self.builder.getResult()
        self.assertEqual(result["video"]["format"], "mp4")
        self.assertEqual(result["video"]["s3_uri"], "s3://bucket/video.mp4")

    def testDocumentMapper(self):
        """Test document content mapping."""
        request = UnifiedRequest(
            messages=[
                Message(
                    role=Role.USER,
                    content=[
                        ContentBlock(
                            document=DocumentBlock(name="test.pdf", content="Document content here")
                        )
                    ],
                )
            ]
        )

        mapper = DocumentMapper()
        mapper.mapRequest(request, self.mockConfig, self.builder)

        result = self.builder.getResult()
        self.assertEqual(result["docs"]["start"], "<docs>")
        self.assertEqual(result["docs"]["index"], "doc_0")
        self.assertEqual(result["docs"]["name"], "test.pdf")
        self.assertEqual(result["docs"]["content"], "Document content here")
        self.assertEqual(result["docs"]["end"], "</docs>")

    def testToolMapper(self):
        """Test tool use mapping."""
        request = UnifiedRequest(
            messages=[
                Message(
                    role=Role.USER,
                    content=[
                        ContentBlock(
                            toolUse=ToolUseBlock(
                                toolUseId="tool_123",
                                name="calculator",
                                input={"operation": "add", "a": 1, "b": 2},
                            )
                        )
                    ],
                )
            ],
            toolConfig=ToolConfig(
                tools=[ToolSpecification(name="calculator", description="A simple calculator")]
            ),
        )

        mapper = ToolMapper()
        mapper.mapRequest(request, self.mockConfig, self.builder)

        result = self.builder.getResult()
        self.assertEqual(result["tool_use"]["id"], "tool_123")
        self.assertEqual(result["tool_use"]["name"], "calculator")
        self.assertEqual(result["tool_use"]["input"]["operation"], "add")
        self.assertEqual(result["tools"]["name"], "calculator")
        self.assertEqual(result["tools"]["description"], "A simple calculator")

    def testMultipleContentTypes(self):
        """Test handling multiple content types in one message."""
        request = UnifiedRequest(
            messages=[
                Message(
                    role=Role.USER,
                    content=[
                        ContentBlock(text="Here's an image and document:"),
                        ContentBlock(
                            image=ImageBlock(format="jpeg", source=ImageSource(bytes=b"image_data"))
                        ),
                        ContentBlock(
                            document=DocumentBlock(name="report.txt", content="Report content")
                        ),
                    ],
                )
            ]
        )

        # Test that all mappers can work together
        imageMapper = ImageMapper()
        docMapper = DocumentMapper()

        imageMapper.mapRequest(request, self.mockConfig, self.builder)
        docMapper.mapRequest(request, self.mockConfig, self.builder)

        result = self.builder.getResult()

        # Should have both image and document data
        self.assertIn("image", result)
        self.assertIn("docs", result)
        self.assertEqual(result["image"]["format"], "image/jpeg")
        self.assertEqual(result["docs"]["name"], "report.txt")

    def testMapperResponseMethods(self):
        """Test mapper response methods that return None."""
        response_data = {"test": "data"}
        config = self.mockConfig
        reader = DocReader(response_data)

        # Test that response methods return None for mappers that don't handle responses
        imageMapper = ImageMapper()
        videoMapper = VideoMapper()
        docMapper = DocumentMapper()
        toolMapper = ToolMapper()

        self.assertIsNone(imageMapper.mapResponse(response_data, config, reader))
        self.assertIsNone(videoMapper.mapResponse(response_data, config, reader))
        self.assertIsNone(docMapper.mapResponse(response_data, config, reader))
        self.assertIsNone(toolMapper.mapResponse(response_data, config, reader))


if __name__ == "__main__":
    unittest.main()
