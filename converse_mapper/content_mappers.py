"""
Comprehensive content mappers for all supported content types.
Each mapper handles a specific type of content block.
"""

from typing import Any, Dict, List

from .config import TransformationConfig
from .doc import DocBuilder, DocReader
from .mappers import ContentMapper
from .models import (
    DocumentBlock,
    ImageBlock,
    ToolResultBlock,
    ToolUseBlock,
    UnifiedRequest,
    UnifiedResponse,
    VideoBlock,
)


class ImageMapper(ContentMapper):
    """Maps image content blocks."""

    def mapRequest(
        self, request: UnifiedRequest, config: TransformationConfig, builder: DocBuilder
    ):
        messageMappings = config.requestMapping.get("messageMappings", {})

        for message in request.messages:
            roleMapping = messageMappings.get(message.role.value, {})
            imageMapping = roleMapping.get("imageBlockMapping", {})

            if not imageMapping:
                continue

            for block in message.content:
                if block.image:
                    self._mapImageBlock(builder, imageMapping, block.image)

    def mapResponse(
        self, response: Dict[str, Any], config: TransformationConfig, reader: DocReader
    ) -> UnifiedResponse:
        # Images typically don't appear in responses, but could be extended
        pass

    def _mapImageBlock(self, builder: DocBuilder, mapping: Dict[str, Any], image: ImageBlock):
        formatMapping = mapping.get("formatMapping", {})
        if formatMapping.get("pointer"):
            builder.setValue(
                formatMapping["pointer"],
                image.format,
                prefix=formatMapping.get("prefix", ""),
                suffix=formatMapping.get("suffix", ""),
            )

        bytesMapping = mapping.get("bytesMapping", {})
        if bytesMapping.get("pointer") and image.source.bytes:
            import base64

            encodedBytes = base64.b64encode(image.source.bytes).decode("utf-8")
            builder.setValue(bytesMapping["pointer"], encodedBytes)


class VideoMapper(ContentMapper):
    """Maps video content blocks."""

    def mapRequest(
        self, request: UnifiedRequest, config: TransformationConfig, builder: DocBuilder
    ):
        messageMappings = config.requestMapping.get("messageMappings", {})

        for message in request.messages:
            roleMapping = messageMappings.get(message.role.value, {})
            videoMapping = roleMapping.get("videoBlockMapping", {})

            if not videoMapping:
                continue

            for block in message.content:
                if block.video:
                    self._mapVideoBlock(builder, videoMapping, block.video)

    def mapResponse(
        self, response: Dict[str, Any], config: TransformationConfig, reader: DocReader
    ) -> UnifiedResponse:
        pass

    def _mapVideoBlock(self, builder: DocBuilder, mapping: Dict[str, Any], video: VideoBlock):
        formatMapping = mapping.get("formatMapping", {})
        if formatMapping.get("pointer"):
            builder.setValue(formatMapping["pointer"], video.format)

        if video.source.s3Uri:
            s3Mapping = mapping.get("s3UriMapping", {})
            if s3Mapping.get("pointer"):
                builder.setValue(s3Mapping["pointer"], video.source.s3Uri)


class DocumentMapper(ContentMapper):
    """Maps document content blocks."""

    def mapRequest(
        self, request: UnifiedRequest, config: TransformationConfig, builder: DocBuilder
    ):
        messageMappings = config.requestMapping.get("messageMappings", {})

        for message in request.messages:
            roleMapping = messageMappings.get(message.role.value, {})
            documentsMapping = roleMapping.get("documentsMapping", {})

            if not documentsMapping:
                continue

            documents = [block.document for block in message.content if block.document]
            if documents:
                self._mapDocuments(builder, documentsMapping, documents)

    def mapResponse(
        self, response: Dict[str, Any], config: TransformationConfig, reader: DocReader
    ) -> UnifiedResponse:
        pass

    def _mapDocuments(
        self, builder: DocBuilder, mapping: Dict[str, Any], documents: List[DocumentBlock]
    ):
        documentBlockMapping = mapping.get("documentBlockMapping", {})

        # Add start attributes (like <documents> tag)
        startAttrs = mapping.get("startAttributes", [])
        for attr in startAttrs:
            if attr.get("pointer"):
                builder.setValue(
                    attr["pointer"], attr.get("overrideValue", ""), append=attr.get("append", False)
                )

        # Map each document
        for i, doc in enumerate(documents):
            # Document index
            indexMapping = documentBlockMapping.get("indexMapping", {})
            if indexMapping.get("pointer"):
                builder.setValue(
                    indexMapping["pointer"],
                    str(i),
                    append=indexMapping.get("append", False),
                    prefix=indexMapping.get("prefix", ""),
                    suffix=indexMapping.get("suffix", ""),
                )

            # Document name
            nameMapping = documentBlockMapping.get("nameMapping", {})
            if nameMapping.get("pointer") and doc.name:
                builder.setValue(
                    nameMapping["pointer"],
                    doc.name,
                    append=nameMapping.get("append", False),
                    prefix=nameMapping.get("prefix", ""),
                    suffix=nameMapping.get("suffix", ""),
                )

            # Document content
            contentMapping = documentBlockMapping.get("contentMapping", {})
            if contentMapping.get("pointer") and doc.content:
                builder.setValue(
                    contentMapping["pointer"],
                    doc.content,
                    append=contentMapping.get("append", False),
                    prefix=contentMapping.get("prefix", ""),
                    suffix=contentMapping.get("suffix", ""),
                )

        # Add end attributes (like </documents> tag)
        endAttrs = mapping.get("endAttributes", [])
        for attr in endAttrs:
            if attr.get("pointer"):
                builder.setValue(
                    attr["pointer"], attr.get("overrideValue", ""), append=attr.get("append", False)
                )


class ToolMapper(ContentMapper):
    """Maps tool use and tool result blocks."""

    def mapRequest(
        self, request: UnifiedRequest, config: TransformationConfig, builder: DocBuilder
    ):
        # Map tool configuration
        if request.toolConfig:
            self._mapToolConfig(builder, config, request.toolConfig)

        # Map tool use and tool result blocks in messages
        messageMappings = config.requestMapping.get("messageMappings", {})

        for message in request.messages:
            roleMapping = messageMappings.get(message.role.value, {})

            for block in message.content:
                if block.toolUse:
                    toolUseMapping = roleMapping.get("toolUseBlockMapping", {})
                    if toolUseMapping:
                        self._mapToolUse(builder, toolUseMapping, block.toolUse)

                if block.toolResult:
                    toolResultMapping = roleMapping.get("toolResultBlockMapping", {})
                    if toolResultMapping:
                        self._mapToolResult(builder, toolResultMapping, block.toolResult)

    def mapResponse(
        self, response: Dict[str, Any], config: TransformationConfig, reader: DocReader
    ) -> UnifiedResponse:
        # Tool responses would be mapped here
        pass

    def _mapToolConfig(self, builder: DocBuilder, config: TransformationConfig, toolConfig):
        toolConfigMapping = config.requestMapping.get("toolConfigMapping", {})

        # Map tool specifications
        toolSpecMapping = toolConfigMapping.get("toolSpecMapping", {})
        for tool in toolConfig.tools:
            if toolSpecMapping.get("nameMapping", {}).get("pointer"):
                builder.setValue(toolSpecMapping["nameMapping"]["pointer"], tool.name)

            if tool.description and toolSpecMapping.get("descriptionMapping", {}).get("pointer"):
                builder.setValue(toolSpecMapping["descriptionMapping"]["pointer"], tool.description)

            if tool.inputSchema and toolSpecMapping.get("inputSchemaMapping", {}).get("pointer"):
                builder.setValue(toolSpecMapping["inputSchemaMapping"]["pointer"], tool.inputSchema)

    def _mapToolUse(self, builder: DocBuilder, mapping: Dict[str, Any], toolUse: ToolUseBlock):
        if mapping.get("toolUseIdMapping", {}).get("pointer"):
            builder.setValue(mapping["toolUseIdMapping"]["pointer"], toolUse.toolUseId)

        if mapping.get("nameMapping", {}).get("pointer"):
            builder.setValue(mapping["nameMapping"]["pointer"], toolUse.name)

        if mapping.get("inputMapping", {}).get("pointer"):
            builder.setValue(mapping["inputMapping"]["pointer"], toolUse.input)

    def _mapToolResult(
        self, builder: DocBuilder, mapping: Dict[str, Any], toolResult: ToolResultBlock
    ):
        if mapping.get("toolUseIdMapping", {}).get("pointer"):
            builder.setValue(mapping["toolUseIdMapping"]["pointer"], toolResult.toolUseId)

        # Map tool result content
        contentMapping = mapping.get("contentMapping", {})
        for content in toolResult.content:
            if content.text and contentMapping.get("textBlockMapping", {}).get(
                "textMapping", {}
            ).get("pointer"):
                builder.setValue(
                    contentMapping["textBlockMapping"]["textMapping"]["pointer"], content.text
                )

            if content.json and contentMapping.get("jsonBlockMapping", {}).get(
                "jsonMapping", {}
            ).get("pointer"):
                builder.setValue(
                    contentMapping["jsonBlockMapping"]["jsonMapping"]["pointer"], content.json
                )
