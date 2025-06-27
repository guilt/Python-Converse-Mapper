"""
Simple HTTP client for Amazon Bedrock with automatic transformation.
"""

import json
from typing import Dict, Optional

from .models import ModelProvider, ProviderResponse, UnifiedRequest, UnifiedResponse
from .transformer import ModelTransformer

try:
    import boto3

    HAS_BOTO3 = True
except ImportError:
    HAS_BOTO3 = False

try:
    import requests

    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


class BedrockConverseClient:
    """
    Easy-to-use Bedrock client with automatic Converse format transformation.
    """

    def __init__(self, region: str = "us-east-1"):
        if not HAS_BOTO3:
            raise ImportError(
                "boto3 is required for BedrockConverseClient. Install with: pip install boto3"
            )
        self.bedrock = boto3.client("bedrock-runtime", region_name=region)
        self.transformer = ModelTransformer()

    def invoke(self, modelId: str, request: UnifiedRequest) -> UnifiedResponse:
        """
        Invoke a Bedrock model with automatic format transformation.

        Args:
            modelId: Bedrock model ID (e.g., "ai21.j2-mid-v1")
            request: Unified request format

        Returns:
            Unified response format
        """
        # Parse provider and version from model ID
        modelProvider = ModelProvider.fromModelId(modelId)

        # Transform request to provider format
        providerRequest = self.transformer.transformRequestForModel(request, modelProvider)

        # Call Bedrock
        response = self.bedrock.invoke_model(
            modelId=modelId, body=json.dumps(providerRequest.body), contentType="application/json"
        )

        # Parse response
        responseBody = json.loads(response["body"].read())
        providerResponse = ProviderResponse(body=responseBody)

        # Transform back to unified format
        return self.transformer.transformResponseForModel(providerResponse, modelProvider)


class SimpleHttpClient:
    """
    Generic HTTP client for any AI API with transformation.
    """

    def __init__(self):
        if not HAS_REQUESTS:
            raise ImportError(
                "requests is required for SimpleHttpClient. Install with: pip install requests"
            )
        self.transformer = ModelTransformer()

    def post(
        self,
        url: str,
        provider: str,
        version: int,
        request: UnifiedRequest,
        headers: Optional[Dict[str, str]] = None,
    ) -> UnifiedResponse:
        """
        POST request with automatic transformation.
        """
        # Transform request
        providerRequest = self.transformer.transformRequest(request, provider, version)

        # Make HTTP request
        response = requests.post(
            url, json=providerRequest.body, headers=headers or {"Content-Type": "application/json"}
        )
        response.raise_for_status()

        # Transform response
        providerResponse = ProviderResponse(body=response.json())
        return self.transformer.transformResponse(providerResponse, provider, version)

    def postForModel(
        self,
        url: str,
        modelProvider: ModelProvider,
        request: UnifiedRequest,
        headers: Optional[Dict[str, str]] = None,
    ) -> UnifiedResponse:
        """
        POST request with ModelProvider and automatic transformation.
        """
        return self.post(url, modelProvider.provider, modelProvider.version, request, headers)
