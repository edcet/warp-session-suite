#!/usr/bin/env python3
"""Base plugin interface for unified terminal automation system."""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict


class BasePlugin(ABC):
    """Base class for all terminal automation plugins."""

    def __init__(self, name: str, version: str, config: Dict[str, Any]):
        self.name = name
        self.version = version
        self.config = config
        self.logger = logging.getLogger(f"plugin.{name}")

    @abstractmethod
    def initialize(self) -> bool:
        """Initialize the plugin. Return True if successful."""
        pass

    @abstractmethod
    def get_session_state(self, **kwargs) -> Dict[str, Any]:
        """Get current session state from this tool."""
        pass

    def cleanup(self) -> None:
        """Clean up plugin resources."""
        pass

    def get_capabilities(self) -> list:
        """Return list of plugin capabilities."""
        return getattr(self, "capabilities", [])

    def supports_capability(self, capability: str) -> bool:
        """Check if plugin supports a specific capability."""
        return capability in self.get_capabilities()
