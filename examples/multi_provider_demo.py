#!/usr/bin/env python3
"""
Provider Comparison Demo.
Shows how different providers handle the same request.
"""

from converse_mapper import ContentBlock, Message, ModelTransformer, Role, UnifiedRequest


def main():
    print("🌐 Provider Format Comparison\n")

    # Create request
    request = UnifiedRequest(
        messages=[
            Message(role=Role.USER, content=[ContentBlock(text="Explain AI in one sentence")])
        ]
    )

    transformer = ModelTransformer()

    providers = [
        ("ai21", 1, "Prompt-based"),
        ("anthropic", 1, "Messages array"),
        ("meta", 1, "Chat template"),
    ]

    print("📝 Input: 'Explain AI in one sentence'\n")

    for provider, version, style in providers:
        try:
            result = transformer.transformRequest(request, provider, version)
            print("🔄 {} ({}):".format(provider.upper(), style))

            # Show key differences
            if "prompt" in result.body:
                print("   → Single prompt string")
            elif "messages" in result.body:
                print("   → Structured messages")

            print("   Size: {} chars".format(len(str(result.body))))
            print()

        except Exception as e:
            print("❌ {}: {}\n".format(provider, e))

    print("✅ One format → Multiple provider APIs!")


if __name__ == "__main__":
    main()
