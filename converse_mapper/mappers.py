"""
Content mappers - one focused class per content type.
Much cleaner than the massive 2000-line mapper class.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict

from .config import TransformationConfig
from .doc import DocBuilder, DocReader
from .models import ContentBlock, Message, Role, StopReason, UnifiedRequest, UnifiedResponse


class ContentMapper(ABC):
    """Base class for all content mappers."""

    @abstractmethod
    def mapRequest(
        self, request: UnifiedRequest, config: TransformationConfig, builder: DocBuilder
    ):
        pass

    @abstractmethod
    def mapResponse(
        self, response: Dict[str, Any], config: TransformationConfig, reader: DocReader
    ) -> UnifiedResponse:
        pass


class TextMapper(ContentMapper):
    """Maps text content blocks."""

    def mapRequest(
        self, request: UnifiedRequest, config: TransformationConfig, builder: DocBuilder
    ):
        messageMappings = config.requestMapping.get("messageMappings", {})

        for message in request.messages:
            roleMapping = messageMappings.get(message.role.value, {})
            textMapping = roleMapping.get("textBlockMapping", {}).get("textMapping", {})

            if not textMapping:
                continue

            # Combine all text blocks for this message
            allText = ""
            for block in message.content:
                if block.text:
                    allText += block.text

            if allText:
                self._applyMapping(builder, textMapping, allText)

    def mapResponse(
        self, response: Dict[str, Any], config: TransformationConfig, reader: DocReader
    ) -> UnifiedResponse:
        resultMapping = config.responseMapping.get("resultMapping", {})
        outputMapping = resultMapping.get("outputMapping", {})
        messageMapping = outputMapping.get("messageMapping", {})
        contentMapping = messageMapping.get("contentMapping", {})
        textMapping = contentMapping.get("textMapping", {})

        text = reader.getValue(textMapping.get("pointer", ""))

        # Get role
        roleMapping = messageMapping.get("roleMapping", {})
        role = roleMapping.get("overrideValue", "assistant")

        # Get stop reason
        stopReasonMapping = resultMapping.get("stopReasonMapping", {})
        stopReasonValue = reader.getValue(
            stopReasonMapping.get("pointer", ""),
            stopReasonMapping.get("valueMap"),
            stopReasonMapping.get("valueMapDefault", "UNKNOWN"),
        )

        # Ensure we always have content
        content = [ContentBlock(text=text)] if text else [ContentBlock(text="")]

        return UnifiedResponse(
            message=Message(role=Role(role), content=content),
            stopReason=StopReason(stopReasonValue),
        )

    def _applyMapping(self, builder: DocBuilder, mapping: Dict[str, Any], value: str):
        pointer = mapping.get("pointer")
        if pointer:
            builder.setValue(
                pointer,
                value,
                append=mapping.get("append", False),
                prefix=mapping.get("prefix", ""),
                suffix=mapping.get("suffix", ""),
            )


class InferenceConfigMapper(ContentMapper):
    """Maps inference configuration."""

    def mapRequest(
        self, request: UnifiedRequest, config: TransformationConfig, builder: DocBuilder
    ):
        if not request.inferenceConfig:
            return

        inferenceMapping = config.requestMapping.get("inferenceConfigMapping", {})

        # Map each field
        if request.inferenceConfig.maxTokens:
            maxTokensMapping = inferenceMapping.get("maxTokensMapping", {})
            if maxTokensMapping.get("pointer"):
                builder.setValue(maxTokensMapping["pointer"], request.inferenceConfig.maxTokens)

        if request.inferenceConfig.temperature:
            tempMapping = inferenceMapping.get("temperatureMapping", {})
            if tempMapping.get("pointer"):
                builder.setValue(tempMapping["pointer"], request.inferenceConfig.temperature)

        if request.inferenceConfig.topP:
            topPMapping = inferenceMapping.get("topPMapping", {})
            if topPMapping.get("pointer"):
                builder.setValue(topPMapping["pointer"], request.inferenceConfig.topP)

        if request.inferenceConfig.stopSequences:
            stopMapping = inferenceMapping.get("stopSequencesMapping", {})
            if stopMapping.get("pointer"):
                builder.setValue(stopMapping["pointer"], request.inferenceConfig.stopSequences)

    def mapResponse(
        self, response: Dict[str, Any], config: TransformationConfig, reader: DocReader
    ) -> UnifiedResponse:
        # Inference config doesn't affect response mapping
        pass


class SystemMessageMapper(ContentMapper):
    """Maps system messages."""

    def mapRequest(
        self, request: UnifiedRequest, config: TransformationConfig, builder: DocBuilder
    ):
        if not request.system:
            return

        systemMapping = config.requestMapping.get("systemMapping", {})
        textMapping = systemMapping.get("textBlockMapping", {}).get("textMapping", {})

        if textMapping:
            systemText = ""
            for block in request.system:
                if block.text:
                    systemText += block.text

            if systemText:
                self._applyMapping(builder, textMapping, systemText)

    def mapResponse(
        self, response: Dict[str, Any], config: TransformationConfig, reader: DocReader
    ) -> UnifiedResponse:
        # System messages don't affect response mapping
        pass

    def _applyMapping(self, builder: DocBuilder, mapping: Dict[str, Any], value: str):
        pointer = mapping.get("pointer")
        if pointer:
            builder.setValue(
                pointer,
                value,
                append=mapping.get("append", False),
                prefix=mapping.get("prefix", ""),
                suffix=mapping.get("suffix", ""),
            )
