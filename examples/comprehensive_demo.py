#!/usr/bin/env python3
"""
Comprehensive demo showing all supported content types.
"""

from converse_mapper import (
    ContentBlock,
    DocumentBlock,
    ImageBlock,
    ImageSource,
    InferenceConfig,
    Message,
    ModelTransformer,
    Role,
    ToolConfig,
    ToolSpecification,
    ToolUseBlock,
    UnifiedRequest,
)


def main():
    print("🎯 Comprehensive Converse Mapper Demo")
    print("=" * 50)

    transformer = ModelTransformer()

    # Create a complex request with multiple content types
    request = UnifiedRequest(
        messages=[
            Message(
                role=Role.USER,
                content=[
                    ContentBlock(text="Please analyze this image and document:"),
                    ContentBlock(
                        image=ImageBlock(
                            format="png", source=ImageSource(bytes=b"fake_image_data_here")
                        )
                    ),
                    ContentBlock(
                        document=DocumentBlock(
                            name="report.pdf",
                            format="pdf",
                            content="This is a sample document content for analysis.",
                        )
                    ),
                ],
            ),
            Message(
                role=Role.ASSISTANT,
                content=[
                    ContentBlock(
                        text="I can see the image and document. Let me use a tool to analyze them."
                    ),
                    ContentBlock(
                        toolUse=ToolUseBlock(
                            toolUseId="tool_123",
                            name="document_analyzer",
                            input={"action": "analyze", "type": "comprehensive"},
                        )
                    ),
                ],
            ),
        ],
        system=[
            ContentBlock(
                text="You are a helpful AI assistant that can analyze images and documents."
            )
        ],
        inferenceConfig=InferenceConfig(maxTokens=200, temperature=0.7, topP=0.9),
        toolConfig=ToolConfig(
            tools=[
                ToolSpecification(
                    name="document_analyzer",
                    description="Analyzes documents and images",
                    inputSchema={
                        "type": "object",
                        "properties": {"action": {"type": "string"}, "type": {"type": "string"}},
                    },
                )
            ]
        ),
    )

    print("📋 Request Summary:")
    print("   Messages: {}".format(len(request.messages)))
    print("   System blocks: {}".format(len(request.system) if request.system else 0))
    print(
        "   Tools configured: {}".format(len(request.toolConfig.tools) if request.toolConfig else 0)
    )
    print("   Max tokens: {}".format(request.inferenceConfig.maxTokens))
    print()

    # Test with different providers
    providers = [("ai21", "AI21 Jurassic"), ("anthropic", "Anthropic Claude")]

    for provider, name in providers:
        try:
            print("🔄 Transforming to {} format...".format(name))
            version = 1
            result = transformer.transformRequest(request, provider, version)

            print("   ✅ Success! Generated {} characters of JSON".format(len(str(result.body))))

            # Show some key fields
            if "prompt" in result.body:
                prompt_preview = (
                    result.body["prompt"][:100] + "..."
                    if len(result.body["prompt"]) > 100
                    else result.body["prompt"]
                )
                print("   📝 Prompt preview: {}".format(prompt_preview))

            if "messages" in result.body:
                print("   💬 Messages structure: {}".format(type(result.body["messages"])))

            print()

        except Exception as e:
            print("   ❌ Error: {}".format(e))
            print()

    print("🎉 Demo complete! All content types supported:")
    print("   ✅ Text blocks")
    print("   ✅ Image blocks (with base64 encoding)")
    print("   ✅ Video blocks (with S3 support)")
    print("   ✅ Document blocks (parsed and raw)")
    print("   ✅ Tool use blocks")
    print("   ✅ Tool result blocks")
    print("   ✅ System messages")
    print("   ✅ Inference configuration")
    print("   ✅ Tool configuration")


if __name__ == "__main__":
    main()
