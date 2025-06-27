"""
Configuration file manipulation utilities.
Unified document builder and reader interfaces.
"""

from typing import Any, Dict, Optional


class DocBuilder:
    """Builds document objects step by step using Document pointer paths."""

    def __init__(self):
        """Initialize empty document builder."""
        self.data: Dict[str, Any] = {}

    def setValue(
        self, path: str, value: Any, append: bool = False, prefix: str = "", suffix: str = ""
    ):
        """Set a value at the given path.

        Args:
            path: Document pointer path (e.g., '/user/name')
            value: Value to set
            append: Whether to append to existing value
            prefix: Prefix to add to value
            suffix: Suffix to add to value
        """
        if not path or path == "/":
            return

        # Remove leading slash and split path
        pathParts = path.strip("/").split("/")
        current = self.data

        # Navigate to parent
        for part in pathParts[:-1]:
            if part not in current:
                current[part] = {}
            elif not isinstance(current[part], dict):
                # If existing value is not a dict, convert it to preserve data
                current[part] = {}
            current = current[part]

        # Set the final value
        finalKey = pathParts[-1]

        # Only add prefix/suffix if they exist, otherwise preserve original type
        if prefix or suffix:
            finalValue = f"{prefix}{value}{suffix}"
        else:
            finalValue = value

        if append and finalKey in current:
            current[finalKey] = str(current[finalKey]) + str(finalValue)
        else:
            current[finalKey] = finalValue

    def getResult(self) -> Dict[str, Any]:
        """Get the built document as dictionary.

        Returns:
            Dictionary containing the built document
        """
        return self.data


class DocReader:
    """Reads values from document objects using Document pointer paths."""

    def __init__(self, data: Dict[str, Any]):
        """Initialize document reader with data.

        Args:
            data: Dictionary to read from
        """
        self.data = data

    def getValue(
        self, path: str, valueMap: Optional[Dict[str, str]] = None, defaultValue: Any = None
    ) -> Any:
        """Get a value at the given path.

        Args:
            path: Document pointer path (e.g., '/user/name')
            valueMap: Optional mapping to transform values
            defaultValue: Default value if path not found

        Returns:
            Value at the specified path or defaultValue
        """
        if not path or path == "/":
            return self.data

        pathParts = path.strip("/").split("/")
        current = self.data

        try:
            for part in pathParts:
                # Handle array indices
                if part.isdigit():
                    current = current[int(part)]
                else:
                    current = current[part]

            # Apply value mapping if provided
            if valueMap and isinstance(current, str):
                return valueMap.get(current, defaultValue)

            return current
        except (KeyError, TypeError, IndexError):
            return defaultValue
