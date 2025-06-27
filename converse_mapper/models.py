"""
Data models for the transformation service.
Simple dataclasses instead of complex inheritance hierarchies.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class Role(Enum):
    USER = "user"
    ASSISTANT = "assistant"


class StopReason(Enum):
    TURN_END = "TURN_END"
    TOKEN_LIMIT = "TOKEN_LIMIT"
    STOP_SEQUENCE = "STOP_SEQUENCE"
    TOOL_USE = "TOOL_USE"
    UNKNOWN = "UNKNOWN"


class ModelProvider(Enum):
    AI21 = "ai21"
    AMAZON = "amazon"
    ANTHROPIC = "anthropic"
    COHERE = "cohere"
    DEEPSEEK = "deepseek"
    JUMPSTART = "jumpstart"
    META = "meta"
    MISTRAL = "mistral"
    QWEN = "qwen"
    WRITER = "writer"

    def __init__(self, provider: str, version: int = 1):
        self.provider = provider
        self.version = version

    def __str__(self) -> str:
        return self.provider

    @classmethod
    def fromName(cls, name: str) -> "ModelProvider":
        """Get provider by name."""
        for provider in cls:
            if provider.provider == name.lower():
                return provider
        raise ValueError(f"Unknown provider name: {name}")

    @classmethod
    def fromModelId(cls, modelId: str) -> "ModelProvider":
        """Parse provider from Bedrock model ID."""
        for provider in cls:
            if modelId.startswith(provider.provider):
                return provider
        raise ValueError(f"Unknown model ID: {modelId}")


@dataclass
class ImageSource:
    bytes: Optional[bytes] = None
    s3Uri: Optional[str] = None
    s3BucketOwner: Optional[str] = None


@dataclass
class ImageBlock:
    format: str  # e.g., "png", "jpeg"
    source: ImageSource


@dataclass
class VideoBlock:
    format: str  # e.g., "mp4", "webm"
    source: ImageSource  # Reuse same source structure


@dataclass
class AudioBlock:
    format: str  # e.g., "mp3", "wav"
    source: ImageSource  # Reuse same source structure


@dataclass
class DocumentBlock:
    name: str
    format: Optional[str] = None
    content: Optional[str] = None  # For parsed documents
    source: Optional[ImageSource] = None  # For raw documents


@dataclass
class ToolUseBlock:
    toolUseId: str
    name: str
    input: Dict[str, Any]


@dataclass
class ToolResultBlock:
    toolUseId: str
    content: List["ToolResultContentBlock"]
    status: Optional[str] = "success"


@dataclass
class ToolResultContentBlock:
    text: Optional[str] = None
    json: Optional[Dict[str, Any]] = None
    image: Optional[ImageBlock] = None
    video: Optional[VideoBlock] = None
    document: Optional[DocumentBlock] = None


@dataclass
class ContentBlock:
    text: Optional[str] = None
    image: Optional[ImageBlock] = None
    video: Optional[VideoBlock] = None
    audio: Optional[AudioBlock] = None
    document: Optional[DocumentBlock] = None
    toolUse: Optional[ToolUseBlock] = None
    toolResult: Optional[ToolResultBlock] = None


@dataclass
class Message:
    role: Role
    content: List[ContentBlock]


@dataclass
class InferenceConfig:
    maxTokens: Optional[int] = None
    temperature: Optional[float] = None
    topP: Optional[float] = None
    stopSequences: Optional[List[str]] = None


@dataclass
class ToolSpecification:
    name: str
    description: Optional[str] = None
    inputSchema: Optional[Dict[str, Any]] = None


@dataclass
class ToolChoice:
    auto: Optional[bool] = None
    any: Optional[bool] = None
    tool: Optional[str] = None  # Specific tool name


@dataclass
class ToolConfig:
    tools: List[ToolSpecification]
    toolChoice: Optional[ToolChoice] = None


@dataclass
class UnifiedRequest:
    messages: List[Message]
    system: Optional[List[ContentBlock]] = None
    inferenceConfig: Optional[InferenceConfig] = None
    toolConfig: Optional[ToolConfig] = None


@dataclass
class UnifiedResponse:
    message: Message
    stopReason: StopReason
    additionalFields: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProviderRequest:
    body: Dict[str, Any]


@dataclass
class ProviderResponse:
    body: Dict[str, Any]
