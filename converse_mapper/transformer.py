"""
Main transformer class - clean and simple.
Uses composition instead of complex inheritance.
"""

from typing import List

from .config import ConfigLoader
from .content_mappers import DocumentMapper, ImageMapper, ToolMapper, VideoMapper
from .doc import DocBuilder, DocReader
from .mappers import ContentMapper, InferenceConfigMapper, SystemMessageMapper, TextMapper
from .models import (
    ModelProvider,
    ProviderRequest,
    ProviderResponse,
    UnifiedRequest,
    UnifiedResponse,
)


class ModelTransformer:
    """Main transformation service for converting between unified and provider formats."""

    def __init__(self, configRoot: str = None):
        """Initialize transformer with content mappers.

        Args:
            configRoot: Optional custom config directory path
        """
        self.configLoader = ConfigLoader(configRoot)
        self.requestMappers: List[ContentMapper] = [
            SystemMessageMapper(),
            TextMapper(),
            ImageMapper(),
            VideoMapper(),
            DocumentMapper(),
            ToolMapper(),
            InferenceConfigMapper(),
        ]
        self.responseMappers: List[ContentMapper] = [TextMapper()]

    def transformRequest(
        self, request: UnifiedRequest, provider: str, version: int = 1, builder: DocBuilder = None
    ) -> ProviderRequest:
        """Transform unified request to provider-specific format.

        Args:
            request: Unified request object
            provider: Provider name (e.g., 'ai21', 'anthropic')
            version: Provider API version
            builder: Optional custom document builder

        Returns:
            ProviderRequest with transformed body
        """
        config = self.configLoader.loadConfig(provider, version)
        if builder is None:
            builder = DocBuilder()

        # Apply all request mappers
        for mapper in self.requestMappers:
            mapper.mapRequest(request, config, builder)

        return ProviderRequest(body=builder.getResult())

    def transformRequestForModel(
        self, request: UnifiedRequest, modelProvider: ModelProvider, builder: DocBuilder = None
    ) -> ProviderRequest:
        """Transform unified request using ModelProvider enum."""
        return self.transformRequest(
            request, modelProvider.provider, modelProvider.version, builder
        )

    def transformResponse(
        self, response: ProviderResponse, provider: str, version: int = 1, reader: DocReader = None
    ) -> UnifiedResponse:
        """Transform provider response to unified format.

        Args:
            response: Provider response object
            provider: Provider name (e.g., 'ai21', 'anthropic')
            version: Provider API version
            reader: Optional custom document reader

        Returns:
            UnifiedResponse with transformed message and metadata
        """
        config = self.configLoader.loadConfig(provider, version)
        if reader is None:
            reader = DocReader(response.body)

        # Use the first mapper that can handle the response
        for mapper in self.responseMappers:
            try:
                result = mapper.mapResponse(response.body, config, reader)
                if result:
                    return result
            except Exception:
                continue

        # Fallback response
        from .models import Message, Role, StopReason

        return UnifiedResponse(
            message=Message(role=Role.ASSISTANT, content=[]), stopReason=StopReason.UNKNOWN
        )

    def transformResponseForModel(
        self, response: ProviderResponse, modelProvider: ModelProvider, reader: DocReader = None
    ) -> UnifiedResponse:
        """Transform provider response using ModelProvider enum."""
        return self.transformResponse(
            response, modelProvider.provider, modelProvider.version, reader
        )
