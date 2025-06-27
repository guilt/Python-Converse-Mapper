"""
Tests for base mappers functionality.
"""

import unittest

from converse_mapper.config import TransformationConfig
from converse_mapper.doc import DocBuilder, DocReader
from converse_mapper.mappers import InferenceConfigMapper, SystemMessageMapper, TextMapper
from converse_mapper.models import ContentBlock, InferenceConfig, Message, Role, UnifiedRequest


class TestMappers(unittest.TestCase):

    def setUp(self):
        self.builder = DocBuilder()
        self.config = TransformationConfig(
            provider="test",
            version=1,
            requestMapping={
                "messageMappings": {
                    "user": {
                        "textBlockMapping": {
                            "textMapping": {
                                "pointer": "/prompt",
                                "prefix": "User: ",
                                "suffix": "\n",
                            }
                        }
                    },
                    "assistant": {"textBlockMapping": {"textMapping": {"pointer": "/response"}}},
                },
                "systemMapping": {
                    "textBlockMapping": {
                        "textMapping": {"pointer": "/system_prompt", "prefix": "System: "}
                    }
                },
                "inferenceConfigMapping": {
                    "maxTokensMapping": {"pointer": "/max_tokens"},
                    "temperatureMapping": {"pointer": "/temperature"},
                    "topPMapping": {"pointer": "/top_p"},
                    "stopSequencesMapping": {"pointer": "/stop"},
                },
            },
            responseMapping={
                "resultMapping": {
                    "outputMapping": {
                        "messageMapping": {
                            "roleMapping": {"overrideValue": "assistant"},
                            "contentMapping": {"textMapping": {"pointer": "/output/text"}},
                        }
                    },
                    "stopReasonMapping": {
                        "pointer": "/stop_reason",
                        "valueMap": {"end_turn": "TURN_END", "max_tokens": "TOKEN_LIMIT"},
                    },
                }
            },
        )

    def testTextMapper(self):
        """Test text content mapping."""
        request = UnifiedRequest(
            messages=[
                Message(role=Role.USER, content=[ContentBlock(text="Hello AI!")]),
                Message(role=Role.ASSISTANT, content=[ContentBlock(text="Hi there!")]),
            ]
        )

        mapper = TextMapper()
        mapper.mapRequest(request, self.config, self.builder)

        result = self.builder.getResult()
        self.assertEqual(result["prompt"], "User: Hello AI!\n")
        self.assertEqual(result["response"], "Hi there!")

    def testSystemMessageMapper(self):
        """Test system message mapping."""
        request = UnifiedRequest(
            messages=[Message(role=Role.USER, content=[ContentBlock(text="Hello")])],
            system=[ContentBlock(text="You are helpful")],
        )

        mapper = SystemMessageMapper()
        mapper.mapRequest(request, self.config, self.builder)

        result = self.builder.getResult()
        self.assertEqual(result["system_prompt"], "System: You are helpful")

    def testInferenceConfigMapper(self):
        """Test inference config mapping."""
        request = UnifiedRequest(
            messages=[Message(role=Role.USER, content=[ContentBlock(text="Hello")])],
            inferenceConfig=InferenceConfig(
                maxTokens=100, temperature=0.7, topP=0.9, stopSequences=["END", "STOP"]
            ),
        )

        mapper = InferenceConfigMapper()
        mapper.mapRequest(request, self.config, self.builder)

        result = self.builder.getResult()
        self.assertEqual(result["max_tokens"], 100)
        self.assertEqual(result["temperature"], 0.7)
        self.assertEqual(result["top_p"], 0.9)
        self.assertEqual(result["stop"], ["END", "STOP"])

    def testTextMapperResponse(self):
        """Test text mapper response transformation."""
        response_data = {"output": {"text": "Hello from AI"}, "stop_reason": "end_turn"}

        reader = DocReader(response_data)
        mapper = TextMapper()

        result = mapper.mapResponse(response_data, self.config, reader)

        self.assertIsNotNone(result)
        self.assertEqual(result.message.role, Role.ASSISTANT)
        self.assertEqual(result.message.content[0].text, "Hello from AI")
        self.assertEqual(result.stopReason.value, "TURN_END")

    def testResponseWithMissingData(self):
        """Test response mapping with missing data."""
        response_data = {"incomplete": "data"}

        reader = DocReader(response_data)
        mapper = TextMapper()

        result = mapper.mapResponse(response_data, self.config, reader)

        # Should handle missing data gracefully
        self.assertIsNotNone(result)
        self.assertEqual(result.message.role, Role.ASSISTANT)

    def testEmptyContent(self):
        """Test handling of empty content."""
        request = UnifiedRequest(messages=[Message(role=Role.USER, content=[])])

        mapper = TextMapper()
        mapper.mapRequest(request, self.config, self.builder)

        # Should not crash with empty content
        result = self.builder.getResult()
        self.assertIsInstance(result, dict)

    def testMissingMappings(self):
        """Test handling when mappings are missing from config."""
        empty_config = TransformationConfig(
            provider="empty", version=1, requestMapping={}, responseMapping={}
        )

        request = UnifiedRequest(
            messages=[Message(role=Role.USER, content=[ContentBlock(text="Hello")])],
            system=[ContentBlock(text="System message")],
            inferenceConfig=InferenceConfig(maxTokens=100),
        )

        # Should not crash with missing mappings
        text_mapper = TextMapper()
        system_mapper = SystemMessageMapper()
        inference_mapper = InferenceConfigMapper()

        text_mapper.mapRequest(request, empty_config, self.builder)
        system_mapper.mapRequest(request, empty_config, self.builder)
        inference_mapper.mapRequest(request, empty_config, self.builder)

        # Should complete without error
        result = self.builder.getResult()
        self.assertIsInstance(result, dict)


if __name__ == "__main__":
    unittest.main()
