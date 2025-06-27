#!/usr/bin/env python3
"""
Quickstart: 30-second introduction to Converse Mapper.
Simplest possible usage - transform one request to multiple providers.
"""

from converse_mapper import ContentBlock, Message, ModelTransformer, Role, UnifiedRequest


def main():
    print("🚀 Converse Mapper - 30 Second Demo\n")

    # Step 1: Create unified request
    request = UnifiedRequest(
        messages=[Message(role=Role.USER, content=[ContentBlock(text="Hello AI!")])]
    )

    # Step 2: Transform to any provider
    transformer = ModelTransformer()

    print("📝 Input: 'Hello AI!'\n")
    print("🔄 Transformations:")

    # AI21 format
    ai21 = transformer.transformRequest(request, "ai21")
    print(f"   AI21: {ai21.body}")

    # Anthropic format
    anthropic = transformer.transformRequest(request, "anthropic")
    print(f"   Anthropic: {len(str(anthropic.body))} chars of JSON")

    print("\n✅ Same input → Multiple provider formats!")
    print("📖 See other examples/ for advanced features.")


if __name__ == "__main__":
    main()
