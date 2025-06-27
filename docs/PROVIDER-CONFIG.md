# Provider Specific Configuration Specification

## Overview

This document describes all supported AI model providers and their YAML configuration mappings.

## Configuration Structure

Each provider has YAML files in `converse_mapper/config/{provider}/v{version}.yml`:

```yaml
provider: string
version: number
requestMapping:
  messageMappings: {} # role-specific mappings
  systemMapping: {} # system message mapping
  inferenceConfigMapping: {} # inference parameters
  toolConfigMapping: {} # tool configuration
responseMapping:
  resultMapping: {} # response transformation
```

## Content Type Mappings

### Text Blocks
```yaml
textBlockMapping:
  textMapping:
    pointer: /path/to/text
    append: true
    prefix: prefix_
    suffix: _suffix
```

### Image Blocks
```yaml
imageBlockMapping:
  formatMapping:
    pointer: /image/format
    prefix: image/
  bytesMapping:
    pointer: /image/data
  s3UriMapping:
    pointer: /image/s3_uri
```

### Document Blocks
```yaml
documentsMapping:
  documentBlockMapping:
    indexMapping:
      pointer: /docs/index
    nameMapping:
      pointer: /docs/name
    contentMapping:
      pointer: /docs/content
  startAttributes:
  - pointer: /docs/start
    overrideValue: <docs>
  endAttributes:
  - pointer: /docs/end
    overrideValue: </docs>
```

### Tool Blocks
```yaml
toolUseBlockMapping:
  toolUseIdMapping:
    pointer: /tool_use/id
  nameMapping:
    pointer: /tool_use/name
  inputMapping:
    pointer: /tool_use/input
```

## Inference Configuration

All providers support these inference parameters with different Document paths:

- **maxTokens**: Maximum tokens to generate
- **temperature**: Randomness (0.0-1.0)
- **topP**: Nucleus sampling parameter
- **stopSequences**: Array of stop strings

## Response Mapping

Responses are mapped back to unified format:

```yaml
responseMapping:
  resultMapping:
    outputMapping:
      messageMapping:
        roleMapping:
          overrideValue: assistant
        contentMapping:
          textMapping:
            pointer: /response/text
    stopReasonMapping:
      pointer: /stop_reason
      valueMap:
        end_turn: TURN_END
        max_tokens: TOKEN_LIMIT
```

## Adding New Providers

1. Create directory: `converse_mapper/config/{provider}/`
2. Add YAML file: `v1.yml` with mapping configuration
3. Test with existing test suite - no code changes needed!

## Configuration Validation

The package automatically validates:
- Required fields presence
- YAML syntax and structure
- Value mapping completeness
- Provider/version combinations