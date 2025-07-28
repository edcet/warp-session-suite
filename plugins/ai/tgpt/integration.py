#!/usr/bin/env python3
"""
TGPT AI Integration Plugin for Unified Terminal Automation System
Provides AI-powered code generation, analysis, and automation capabilities
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List

# Add core plugin path
sys.path.append(str(Path(__file__).parent.parent.parent))

try:
    from core.session.base_plugin import BasePlugin
except ImportError:
    # Fallback minimal implementation
    class BasePlugin:
        def __init__(self, name, version, config):
            self.name = name
            self.version = version
            self.config = config


class TGPTPlugin(BasePlugin):
    """TGPT AI integration plugin for intelligent automation."""

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("tgpt", "1.0.0", config or {})
        self.capabilities = ["code_generation", "analysis", "automation", "chat"]

    def initialize(self) -> bool:
        """Initialize TGPT plugin."""
        # Check if tgpt is available
        try:
            result = subprocess.run(
                ["tgpt", "--version"], capture_output=True, text=True, timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def get_session_state(self, **kwargs) -> Dict[str, Any]:
        """Get AI integration session state."""
        return {
            "plugin_name": self.name,
            "plugin_version": self.version,
            "capabilities": self.capabilities,
            "tgpt_available": self.initialize(),
            "session_timestamp": subprocess.check_output(["date", "-Iseconds"])
            .decode()
            .strip(),
        }

    def generate_code(self, prompt: str, language: str = "python") -> str:
        """Generate code using TGPT."""
        try:
            full_prompt = f"Generate {language} code for: {prompt}"
            result = subprocess.run(
                ["tgpt", "--code", full_prompt],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                return result.stdout.strip()
            else:
                return f"Error generating code: {result.stderr}"
        except Exception as e:
            return f"Failed to generate code: {e}"

    def analyze_code(self, code: str, focus: str = "general") -> str:
        """Analyze code using TGPT."""
        try:
            prompt = f"Analyze this code focusing on {focus}:\n\n{code}"
            result = subprocess.run(
                ["tgpt", "--markdown", prompt],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                return result.stdout.strip()
            else:
                return f"Error analyzing code: {result.stderr}"
        except Exception as e:
            return f"Failed to analyze code: {e}"

    def chat(self, message: str) -> str:
        """Interactive chat with TGPT."""
        try:
            result = subprocess.run(
                ["tgpt", message], capture_output=True, text=True, timeout=30
            )

            if result.returncode == 0:
                return result.stdout.strip()
            else:
                return f"Error in chat: {result.stderr}"
        except Exception as e:
            return f"Failed to chat: {e}"

    def generate_plugin_template(self, tool_name: str, capabilities: List[str]) -> str:
        """Generate a plugin template for a new tool."""
        capabilities_str = ", ".join(capabilities)
        prompt = f"""
        Create a Python plugin template for a tool called '{tool_name}' with capabilities: {capabilities_str}
        
        The plugin should:
        1. Inherit from BasePlugin class
        2. Implement initialize(), get_session_state(), and cleanup() methods
        3. Include proper error handling and logging
        4. Follow the same pattern as other plugins in the system
        
        Generate complete, production-ready code.
        """

        return self.generate_code(prompt, "python")

    def suggest_command(self, description: str) -> str:
        """Suggest shell commands based on description."""
        try:
            prompt = f"Suggest shell commands for: {description}"
            result = subprocess.run(
                ["tgpt", "--shell", prompt], capture_output=True, text=True, timeout=20
            )

            if result.returncode == 0:
                return result.stdout.strip()
            else:
                return f"Error suggesting command: {result.stderr}"
        except Exception as e:
            return f"Failed to suggest command: {e}"


# Plugin factory function
def create_plugin(config: Dict[str, Any] = None) -> TGPTPlugin:
    """Create and return a TGPT plugin instance."""
    return TGPTPlugin(config)


# CLI interface for standalone usage
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="TGPT AI Plugin CLI")
    parser.add_argument(
        "command",
        choices=["test", "generate", "analyze", "chat"],
        help="Command to execute",
    )
    parser.add_argument("--prompt", type=str, help="Prompt for generation or chat")
    parser.add_argument(
        "--language", type=str, default="python", help="Programming language"
    )
    parser.add_argument("--code", type=str, help="Code to analyze")

    args = parser.parse_args()

    try:
        plugin = create_plugin()

        if plugin.initialize():
            print("✅ TGPT plugin initialized successfully")

            if args.command == "test":
                state = plugin.get_session_state()
                print(f"📊 Plugin State: {json.dumps(state, indent=2)}")

            elif args.command == "generate":
                if not args.prompt:
                    args.prompt = input("Enter generation prompt: ")
                code = plugin.generate_code(args.prompt, args.language)
                print("🤖 Generated Code:")
                print(code)

            elif args.command == "analyze":
                if not args.code:
                    args.code = input("Enter code to analyze: ")
                analysis = plugin.analyze_code(args.code)
                print("📊 Code Analysis:")
                print(analysis)

            elif args.command == "chat":
                if not args.prompt:
                    args.prompt = input("Enter chat message: ")
                response = plugin.chat(args.prompt)
                print("💬 AI Response:")
                print(response)

            print("✅ All operations completed successfully!")
        else:
            print("❌ TGPT plugin initialization failed - is tgpt installed?")
            sys.exit(1)

    except Exception as e:
        print(f"❌ Plugin operation failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
