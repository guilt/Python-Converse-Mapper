"""
Converse Mapper - Simple AI model interface transformer
"""

from .models import (
    AudioBlock,
    ContentBlock,
    DocumentBlock,
    ImageBlock,
    ImageSource,
    InferenceConfig,
    Message,
    ModelProvider,
    ProviderRequest,
    ProviderResponse,
    Role,
    StopReason,
    ToolChoice,
    ToolConfig,
    ToolResultBlock,
    ToolResultContentBlock,
    ToolSpecification,
    ToolUseBlock,
    UnifiedRequest,
    UnifiedResponse,
    VideoBlock,
)
from .transformer import ModelTransformer

__version__ = "1.0.0"
__all__ = [
    "UnifiedRequest",
    "UnifiedResponse",
    "ProviderRequest",
    "ProviderResponse",
    "Message",
    "ContentBlock",
    "InferenceConfig",
    "Role",
    "StopReason",
    "ImageBlock",
    "ImageSource",
    "VideoBlock",
    "AudioBlock",
    "DocumentBlock",
    "ToolUseBlock",
    "ToolResultBlock",
    "ToolResultContentBlock",
    "ToolSpecification",
    "ToolChoice",
    "ToolConfig",
    "ModelTransformer",
    "ModelProvider",
]

# Optional imports
try:
    from .bedrock_client import BedrockConverseClient, SimpleHttpClient  # noqa: F401

    __all__.extend(["BedrockConverseClient", "SimpleHttpClient"])
except ImportError:
    pass
