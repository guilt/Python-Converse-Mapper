# Converse Mapper

🚀 **Simple, readable AI model interface transformer for Amazon Bedrock**

Transform between unified conversation format and provider-specific APIs with zero complexity.

## Why This Exists

AI model providers (Anthropic, Meta, AI21, etc.) all have different API formats. This library provides a **unified conversation interface** that automatically transforms to/from any provider format.

**Before**: Wrestling with different schemas for each model  
**After**: One simple format that works everywhere

## Quick Start

```bash
# Install with AWS support
pip install 'converse-mapper[aws]'
```

**Verify installation:**
```bash
python -c "from converse_mapper import ModelTransformer; print('✅ Installation successful!')"
```

### Simple Example

```python
from converse_mapper import BedrockConverseClient, UnifiedRequest, Message, ContentBlock, Role

# Create client
client = BedrockConverseClient(region="us-east-1")

# Simple conversation
request = UnifiedRequest(
    messages=[
        Message(role=Role.USER, content=[ContentBlock(text="What is AI?")])
    ]
)

# Works with any Bedrock model
response = client.invoke("ai21.j2-mid-v1", request)
print(response.message.content[0].text)
```

## More Examples

### Transform Between Providers

```python
from converse_mapper import ModelTransformer, UnifiedRequest, Message, ContentBlock, Role

transformer = ModelTransformer()
request = UnifiedRequest(
    messages=[Message(role=Role.USER, content=[ContentBlock(text="Hello!")])]
)

# Transform to different provider formats
ai21_request = transformer.transformRequest(request, "ai21")
anthropic_request = transformer.transformRequest(request, "anthropic")
```

### With Configuration

```python
from converse_mapper import InferenceConfig

request = UnifiedRequest(
    messages=[Message(role=Role.USER, content=[ContentBlock(text="Write a poem")])],
    inferenceConfig=InferenceConfig(maxTokens=100, temperature=0.7)
)
```

### HTTP Client (Non-Bedrock)

```python
from converse_mapper import SimpleHttpClient

client = SimpleHttpClient()
response = client.post(
    url="https://api.anthropic.com/v1/messages",
    provider="anthropic",
    request=request,
    headers={"x-api-key": "your-key"}
)
```

## Supported Providers

| Provider | Models | Status |
|----------|--------|--------|
| **AI21** | Jamba - Large, Mini | ✅ |
| **Anthropic** | Claude 3.5, Claude 3 - Sonnet, Opus, Haiku | ✅ |
| **Meta** | Llama 3.3, Llama 3.2, Llama 3.1 | ✅ |
| **Cohere** | Command - R+, R Light | ✅ |
| **Amazon** | Titan Text G1, Premier, Nova - Pro, Premier, Micro, Lite | ✅ |
| **Mistral** | Mistral 7B, Mixtral 8x7B, Mistral Large | ✅ |
| **DeepSeek** | DeepSeek R1 | ✅ |
| **Writer** | Palmyra X4, Palmyra X5 | ✅ |
| **Qwen** | Qwen 3 | ✅ |
| **JumpStart** | Various third-party models | ✅ |

## Features

✅ **Works with 10+ model providers** out of the box  
✅ **Configuration-driven** - add new providers with simple YAML files  
✅ **Type-safe** with full IDE support  
✅ **Easy testing** with focused, isolated components  
✅ **Minimal dependencies** - only PyYAML core, optional boto3/requests for clients

## Adding New Providers

1. Drop a YAML config file in `converse_mapper/config/{provider}/v{version}.yml`
2. That's it! No code changes needed.

See [Converse Specification](docs/CONVERSE-SPEC.md) and [Provider Specific Configuration Specification](docs/PROVIDER-CONFIG.md) for details.

## Complete Examples

See the [examples/](examples/) directory for working examples:

- [`examples/quickstart.py`](examples/quickstart.py) - 30-second introduction
- [`examples/multi_provider_demo.py`](examples/multi_provider_demo.py) - Provider format comparison
- [`examples/comprehensive_demo.py`](examples/comprehensive_demo.py) - All content types showcase
- [`examples/bedrock_demo.py`](examples/bedrock_demo.py) - AWS Bedrock integration

## Development

```bash
# Clone and install
git clone https://github.com/guilt/Python-Converse-Mapper
cd Python-Converse-Mapper
pip install -e ".[dev]"

# Run tests
python -m unittest discover tests/ -v
```

## License

MIT License. See [License](LICENSE.md) for details.

## Feedback

Made with ❤️ by [Vibe coding](https://en.wikipedia.org/wiki/Vibe_coding).

* Authors: [Claude Code](https://anthropic.com/) and [Karthik Kumar Viswanathan](https://github.com/guilt)
* Web   : http://karthikkumar.org
* Email : me@karthikkumar.org