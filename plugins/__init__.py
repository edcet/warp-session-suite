"""
Unified Terminal Automation System - Plugin Architecture
Modular plugin system for Warp, Cursor, Windsurf, PearAI, and other terminal tools.
"""

from pathlib import Path
import json
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class PluginManager:
    """Manages the unified plugin system."""

    def __init__(self, plugin_dir: Path = None):
        self.plugin_dir = plugin_dir or Path(__file__).parent
        self.registry_file = self.plugin_dir / "registry.json"
        self.loaded_plugins = {}

    def load_registry(self) -> Dict[str, Any]:
        """Load the plugin registry."""
        if self.registry_file.exists():
            with open(self.registry_file) as f:
                return json.load(f)
        return {"plugins": {}}

    def get_available_plugins(self) -> List[str]:
        """Get list of available plugin names."""
        registry = self.load_registry()
        return list(registry.get("plugins", {}).keys())

    def load_plugin(self, plugin_name: str) -> Optional[Any]:
        """Dynamically load a plugin."""
        if plugin_name in self.loaded_plugins:
            return self.loaded_plugins[plugin_name]

        registry = self.load_registry()
        plugin_info = registry.get("plugins", {}).get(plugin_name)

        if not plugin_info:
            logger.error(f"Plugin '{plugin_name}' not found in registry")
            return None

        entry_path = self.plugin_dir.parent / plugin_info["entry"]
        if not entry_path.exists():
            logger.error(f"Plugin entry file not found: {entry_path}")
            return None

        try:
            # Dynamic import would go here
            # For now, return plugin info
            self.loaded_plugins[plugin_name] = plugin_info
            return plugin_info
        except Exception as e:
            logger.error(f"Failed to load plugin '{plugin_name}': {e}")
            return None

    def register_plugin(self, name: str, info: Dict[str, Any]) -> bool:
        """Register a new plugin."""
        try:
            registry = self.load_registry()
            registry["plugins"][name] = info

            with open(self.registry_file, "w") as f:
                json.dump(registry, f, indent=2)

            logger.info(f"Plugin '{name}' registered successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to register plugin '{name}': {e}")
            return False


# Global plugin manager instance
plugin_manager = PluginManager()
