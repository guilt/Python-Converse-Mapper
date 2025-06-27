# Converse Specification

## Overview

The Converse API provides a unified interface for conversational AI models, abstracting away [provider-specific configuration](PROVIDER-CONFIG.md) into a common structure.

## Request Format

```json
{
  "messages": [
    {
      "role": "user|assistant",
      "content": [
        {
          "text": "string"
        }
      ]
    }
  ],
  "system": [
    {
      "text": "string"
    }
  ],
  "inferenceConfig": {
    "maxTokens": 100,
    "temperature": 0.7,
    "topP": 0.9,
    "stopSequences": ["string"]
  }
}
```

## Response Format

```json
{
  "message": {
    "role": "assistant",
    "content": [
      {
        "text": "string"
      }
    ]
  },
  "stopReason": "TURN_END|TOKEN_LIMIT|STOP_SEQUENCE|TOOL_USE|UNKNOWN"
}
```

### Example: AI21 Mapping

**Request**: `{"messages": [{"role": "user", "content": [{"text": "Hello"}]}]}`
**Transforms to**: `{"prompt": "Hello"}`

**Response**: `{"completions": [{"data": {"text": "Hi there!"}}]}`
**Transforms to**: `{"message": {"role": "assistant", "content": [{"text": "Hi there!"}]}}`
