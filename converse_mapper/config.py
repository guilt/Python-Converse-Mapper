"""
Configuration loading and management.
Loads YAML configs from resources directory.
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict

import yaml

from .models import ModelProvider


@dataclass
class TransformationConfig:
    provider: str
    version: int
    requestMapping: Dict[str, Any]
    responseMapping: Dict[str, Any]


class ConfigLoader:
    """Loads and caches provider transformation configurations."""

    def __init__(self, configRoot: str = None):
        """Initialize config loader.

        Args:
            configRoot: Root directory for config files. Defaults to package config directory.
        """
        if configRoot is None:
            import os

            packageDir = os.path.dirname(__file__)
            configRoot = os.path.join(packageDir, "config")
        self.configRoot = Path(configRoot)
        self._cache: Dict[str, TransformationConfig] = {}

    def loadConfig(self, provider: str, version: int = 1) -> TransformationConfig:
        """Load transformation configuration for provider and version.

        Args:
            provider: Provider name (e.g., 'ai21', 'anthropic')
            version: Configuration version number

        Returns:
            TransformationConfig object with request/response mappings
        """
        cacheKey = f"{provider}_v{version}"
        if cacheKey in self._cache:
            return self._cache[cacheKey]

        data = self._loadConfigFor(provider, version)

        config = TransformationConfig(
            provider=data["provider"],
            version=data["version"],
            requestMapping=data["requestMapping"],
            responseMapping=data["responseMapping"],
        )

        self._cache[cacheKey] = config
        return config

    def loadConfigForModelProvider(self, modelProvider: ModelProvider) -> TransformationConfig:
        """Load configuration using ModelProvider enum."""
        return self.loadConfig(modelProvider.provider, modelProvider.version)

    def _loadConfigFor(self, provider: str, version: int) -> Dict[str, Any]:
        """Load configuration data for provider/version (tries YAML first, then JSON)."""
        basePath = self.configRoot / provider / f"v{version}"

        # Try YAML first
        yamlPath = basePath.with_suffix(".yml")
        if yamlPath.exists():
            return self._loadYaml(str(yamlPath))

        # Try JSON as fallback
        jsonPath = basePath.with_suffix(".json")
        if jsonPath.exists():
            return self._loadJson(str(jsonPath))

        raise FileNotFoundError(
            f"Config not found for {provider} v{version} (tried .yml and .json)"
        )

    def _loadYaml(self, filePath: str) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        with open(filePath, "r") as f:
            return yaml.safe_load(f)

    def _loadJson(self, filePath: str) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        with open(filePath, "r") as f:
            return json.load(f)
