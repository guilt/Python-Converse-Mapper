#!/usr/bin/env python3
"""
Bedrock Integration Demo.
Shows how to use with AWS Bedrock (requires AWS credentials).
"""

from converse_mapper import ContentBlock, InferenceConfig, Message, Role, UnifiedRequest


def main():
    print("🔗 Bedrock Integration Demo\n")

    # Create request with inference config
    request = UnifiedRequest(
        messages=[
            Message(
                role=Role.USER,
                content=[ContentBlock(text="Explain quantum computing in simple terms")],
            )
        ],
        inferenceConfig=InferenceConfig(maxTokens=200, temperature=0.7, topP=0.9),
    )

    print("📋 Request created with:")
    print(f"   Message: {request.messages[0].content[0].text}")
    print(f"   Max tokens: {request.inferenceConfig.maxTokens}")
    print(f"   Temperature: {request.inferenceConfig.temperature}")
    print()

    # Show how to use with Bedrock (if credentials available)
    try:
        from converse_mapper import BedrockConverseClient  # noqa: F401

        print("🚀 BedrockConverseClient available!")
        print("   Usage:")
        print("   client = BedrockConverseClient()")
        print("   response = client.invoke('ai21.j2-mid-v1', request)")
        print("   print(response.message.content[0].text)")
        print()
        print("💡 Requires AWS credentials configured")

    except ImportError:
        print("📦 Install boto3 for Bedrock integration:")
        print("   pip install boto3")

    print("\n✅ Ready for production AWS usage!")


if __name__ == "__main__":
    main()
