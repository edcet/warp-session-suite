#!/usr/bin/env python3
"""
Code Quality Plugin for Unified Terminal Automation System
Integrates trunk, lefthook, formatters, parsers, and linters for comprehensive code quality management
"""

import json
import subprocess
import sys
from datetime import datetime
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


class CodeQualityPlugin(BasePlugin):
    """Code quality plugin integrating trunk, lefthook, formatters, parsers, and linters."""

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("code_quality", "1.0.0", config or {})
        self.capabilities = [
            "trunk_integration",
            "lefthook_management",
            "formatting",
            "linting",
            "parsing",
            "git_hooks",
        ]
        self.base_dir = Path(__file__).parent.parent.parent.parent
        self.tools_status = {}

    def initialize(self) -> bool:
        """Initialize Code Quality plugin."""
        self._detect_available_tools()
        self._ensure_configuration_files()
        return True

    def _detect_available_tools(self):
        """Detect which code quality tools are available."""
        tools_to_check = {
            "trunk": ["trunk", "--version"],
            "lefthook": ["lefthook", "version"],
            "prettier": ["prettier", "--version"],
            "black": ["black", "--version"],
            "ruff": ["ruff", "--version"],
            "eslint": ["eslint", "--version"],
            "pylint": ["pylint", "--version"],
            "rustfmt": ["rustfmt", "--version"],
            "go fmt": ["gofmt", "-h"],
            "shfmt": ["shfmt", "--version"],
            "yamllint": ["yamllint", "--version"],
            "markdownlint": ["markdownlint", "--version"],
            "shellcheck": ["shellcheck", "--version"],
        }

        for tool_name, command in tools_to_check.items():
            try:
                result = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    timeout=5,
                    cwd=self.base_dir,
                )
                self.tools_status[tool_name] = {
                    "available": result.returncode == 0,
                    "version": (
                        result.stdout.strip() if result.returncode == 0 else None
                    ),
                    "path": subprocess.run(
                        ["which", command[0]], capture_output=True, text=True
                    ).stdout.strip(),
                }
            except (subprocess.TimeoutExpired, FileNotFoundError):
                self.tools_status[tool_name] = {
                    "available": False,
                    "version": None,
                    "path": None,
                }

    def _ensure_configuration_files(self):
        """Ensure all necessary configuration files exist."""
        # Create .trunk directory and configuration
        trunk_dir = self.base_dir / ".trunk"
        trunk_dir.mkdir(exist_ok=True)

        trunk_config = trunk_dir / "trunk.yaml"
        if not trunk_config.exists():
            trunk_config_content = """# Trunk configuration for Unified Terminal Automation System
version: 0.1
cli:
  version: 1.22.2

plugins:
  sources:
    - id: trunk
      ref: v1.6.2
      uri: https://github.com/trunk-io/plugins

lint:
  enabled:
    - actionlint@1.7.1
    - bandit@1.7.5
    - black@24.4.2
    - checkov@3.2.252
    - eslint@8.57.0
    - flake8@7.1.1
    - git-diff-check
    - gitleaks@8.18.4
    - hadolint@2.12.0
    - isort@5.13.2
    - markdownlint@0.41.0
    - mypy@1.11.2
    - oxipng@9.1.2
    - prettier@3.3.3
    - pylint@3.2.7
    - ruff@0.6.4
    - shellcheck@0.10.0
    - shfmt@3.7.0
    - sqlfluff@3.1.1
    - taplo@0.9.3
    - terrascan@1.19.1
    - trivy@0.55.0
    - trufflehog@3.82.6
    - yamllint@1.35.1

actions:
  enabled:
    - trunk-announce
    - trunk-check-pre-push
    - trunk-fmt-pre-commit
    - trunk-upgrade-available

runtimes:
  enabled:
    - go@1.21.0
    - node@18.12.1
    - python@3.10.8
"""
            with open(trunk_config, "w") as f:
                f.write(trunk_config_content)

        # Create lefthook configuration
        lefthook_config = self.base_dir / "lefthook.yml"
        if not lefthook_config.exists():
            lefthook_config_content = r"""# Lefthook configuration for Unified Terminal Automation System
pre-commit:
  parallel: true
  commands:
    trunk-check:
      glob: "*.{py,js,ts,yaml,yml,json,md,sh}"
      run: trunk fmt {staged_files} && trunk check {staged_files}
    plugin-tests:
      glob: "plugins/**/*.py"
      run: python3 {staged_files} test
    security-scan:
      run: trunk check --filter=bandit,gitleaks,trufflehog
      
pre-push:
  parallel: true
  commands:
    full-quality-check:
      run: trunk check --all
    plugin-validation:
      run: python3 unified_cli.py system status
    advanced-automation-test:
      run: python3 advanced_automation.py
      
commit-msg:
  commands:
    conventional-commits:
      run: |
        if ! grep -qE "^(feat|fix|docs|style|refactor|test|chore|ci|perf|build|revert)(\(.+\))?: .+" "$1"; then
          echo "❌ Commit message must follow conventional commit format"
          echo "Examples: feat: add new feature, fix: resolve bug, docs: update readme"
          exit 1
        fi
"""
            with open(lefthook_config, "w") as f:
                f.write(lefthook_config_content)

        # Create .prettierrc configuration
        prettier_config = self.base_dir / ".prettierrc"
        if not prettier_config.exists():
            prettier_config_content = """{
  "printWidth": 100,
  "tabWidth": 2,
  "useTabs": false,
  "semi": true,
  "singleQuote": true,
  "quoteProps": "as-needed",
  "trailingComma": "es5",
  "bracketSpacing": true,
  "arrowParens": "avoid",
  "endOfLine": "lf",
  "overrides": [
    {
      "files": "*.py",
      "options": {
        "parser": "python"
      }
    },
    {
      "files": "*.md",
      "options": {
        "proseWrap": "always"
      }
    }
  ]
}"""
            with open(prettier_config, "w") as f:
                f.write(prettier_config_content)

        # Create pyproject.toml for Python tools
        pyproject_config = self.base_dir / "pyproject.toml"
        if not pyproject_config.exists():
            pyproject_content = """[tool.black]
line-length = 100
target-version = ['py312']
include = '\\.pyi?$'
extend-exclude = '''
/(
  # directories
  \\.eggs
  | \\.git
  | \\.hg
  | \\.mypy_cache
  | \\.tox
  | \\.venv
  | build
  | dist
)/
'''

[tool.isort]
profile = "black"
line_length = 100
multi_line_output = 3

[tool.pylint.messages_control]
disable = "C0330, C0326"

[tool.pylint.format]
max-line-length = "100"

[tool.mypy]
python_version = "3.12"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true

[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "W", "C", "N", "UP", "S", "B", "I"]
ignore = ["E501"]

[tool.bandit]
exclude_dirs = ["tests", "venv", ".venv"]
skips = ["B101", "B601"]
"""
            with open(pyproject_config, "w") as f:
                f.write(pyproject_content)

    def get_session_state(self, **kwargs) -> Dict[str, Any]:
        """Get Code Quality plugin session state."""
        return {
            "plugin_name": self.name,
            "plugin_version": self.version,
            "capabilities": self.capabilities,
            "tools_status": self.tools_status,
            "available_tools": len(
                [t for t in self.tools_status.values() if t["available"]]
            ),
            "total_tools": len(self.tools_status),
            "session_timestamp": datetime.now().isoformat(),
        }

    def install_tools(self) -> Dict[str, Any]:
        """Install missing code quality tools."""
        installation_results = {
            "timestamp": datetime.now().isoformat(),
            "installations": [],
        }

        # Install trunk if not available
        if not self.tools_status.get("trunk", {}).get("available", False):
            try:
                print("📦 Installing trunk...")
                result = subprocess.run(
                    [
                        "curl",
                        "-fsSL",
                        "https://get.trunk.io",
                        "-o",
                        "/tmp/install_trunk.sh",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )

                if result.returncode == 0:
                    result = subprocess.run(
                        ["bash", "/tmp/install_trunk.sh"],
                        capture_output=True,
                        text=True,
                        timeout=60,
                    )

                    installation_results["installations"].append(
                        {
                            "tool": "trunk",
                            "success": result.returncode == 0,
                            "method": "curl_install",
                        }
                    )
            except Exception as e:
                installation_results["installations"].append(
                    {"tool": "trunk", "success": False, "error": str(e)}
                )

        # Install lefthook if not available
        if not self.tools_status.get("lefthook", {}).get("available", False):
            try:
                print("📦 Installing lefthook...")
                result = subprocess.run(
                    ["npm", "install", "-g", "@arkweid/lefthook"],
                    capture_output=True,
                    text=True,
                    timeout=60,
                )

                installation_results["installations"].append(
                    {
                        "tool": "lefthook",
                        "success": result.returncode == 0,
                        "method": "npm",
                    }
                )
            except Exception as e:
                installation_results["installations"].append(
                    {"tool": "lefthook", "success": False, "error": str(e)}
                )

        # Install Python tools via pip
        python_tools = ["black", "ruff", "pylint", "mypy", "bandit", "isort"]
        for tool in python_tools:
            if not self.tools_status.get(tool, {}).get("available", False):
                try:
                    print(f"📦 Installing {tool}...")
                    result = subprocess.run(
                        ["pip3", "install", "--user", tool],
                        capture_output=True,
                        text=True,
                        timeout=60,
                    )

                    installation_results["installations"].append(
                        {
                            "tool": tool,
                            "success": result.returncode == 0,
                            "method": "pip",
                        }
                    )
                except Exception as e:
                    installation_results["installations"].append(
                        {"tool": tool, "success": False, "error": str(e)}
                    )

        return installation_results

    def run_trunk_check(
        self, files: List[str] = None, fix: bool = False
    ) -> Dict[str, Any]:
        """Run trunk check on specified files or all files."""
        command = ["trunk", "check"]

        if fix:
            command.append("--fix")

        if files:
            command.extend(files)
        else:
            command.append("--all")

        try:
            result = subprocess.run(
                command, capture_output=True, text=True, timeout=120, cwd=self.base_dir
            )

            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "command": " ".join(command),
                "files_checked": files or "all",
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "command": " ".join(command),
                "timestamp": datetime.now().isoformat(),
            }

    def run_formatting(
        self, language: str = None, files: List[str] = None
    ) -> Dict[str, Any]:
        """Run appropriate formatters based on language or file extensions."""
        formatting_results = {"timestamp": datetime.now().isoformat(), "results": []}

        if language == "python" or (files and any(f.endswith(".py") for f in files)):
            # Format Python files
            python_files = files if files else []
            if not files:
                python_files = list(self.base_dir.glob("**/*.py"))

            # Run black
            if self.tools_status.get("black", {}).get("available", False):
                try:
                    result = subprocess.run(
                        ["black", "--line-length", "100"]
                        + [str(f) for f in python_files],
                        capture_output=True,
                        text=True,
                        timeout=60,
                        cwd=self.base_dir,
                    )

                    formatting_results["results"].append(
                        {
                            "tool": "black",
                            "success": result.returncode == 0,
                            "files": len(python_files),
                            "output": result.stdout,
                        }
                    )
                except Exception as e:
                    formatting_results["results"].append(
                        {"tool": "black", "success": False, "error": str(e)}
                    )

            # Run isort
            if self.tools_status.get("isort", {}).get("available", False):
                try:
                    result = subprocess.run(
                        ["isort", "--profile", "black"]
                        + [str(f) for f in python_files],
                        capture_output=True,
                        text=True,
                        timeout=60,
                        cwd=self.base_dir,
                    )

                    formatting_results["results"].append(
                        {
                            "tool": "isort",
                            "success": result.returncode == 0,
                            "files": len(python_files),
                            "output": result.stdout,
                        }
                    )
                except Exception as e:
                    formatting_results["results"].append(
                        {"tool": "isort", "success": False, "error": str(e)}
                    )

        if language == "javascript" or (
            files and any(f.endswith((".js", ".ts", ".json")) for f in files)
        ):
            # Format JavaScript/TypeScript files
            js_files = files if files else list(self.base_dir.glob("**/*.{js,ts,json}"))

            if self.tools_status.get("prettier", {}).get("available", False):
                try:
                    result = subprocess.run(
                        ["prettier", "--write"] + [str(f) for f in js_files],
                        capture_output=True,
                        text=True,
                        timeout=60,
                        cwd=self.base_dir,
                    )

                    formatting_results["results"].append(
                        {
                            "tool": "prettier",
                            "success": result.returncode == 0,
                            "files": len(js_files),
                            "output": result.stdout,
                        }
                    )
                except Exception as e:
                    formatting_results["results"].append(
                        {"tool": "prettier", "success": False, "error": str(e)}
                    )

        return formatting_results

    def setup_git_hooks(self) -> Dict[str, Any]:
        """Setup git hooks using lefthook."""
        setup_result = {
            "timestamp": datetime.now().isoformat(),
            "lefthook_available": self.tools_status.get("lefthook", {}).get(
                "available", False
            ),
        }

        if not setup_result["lefthook_available"]:
            setup_result["error"] = "Lefthook not available"
            return setup_result

        try:
            # Install lefthook hooks
            result = subprocess.run(
                ["lefthook", "install"],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=self.base_dir,
            )

            setup_result["install_success"] = result.returncode == 0
            setup_result["install_output"] = result.stdout

            if result.returncode != 0:
                setup_result["install_error"] = result.stderr

            # Verify hooks are installed
            git_hooks_dir = self.base_dir / ".git" / "hooks"
            hooks_installed = []

            for hook_file in git_hooks_dir.glob("*"):
                if hook_file.is_file() and hook_file.name != ".sample":
                    hooks_installed.append(hook_file.name)

            setup_result["hooks_installed"] = hooks_installed
            setup_result["hooks_count"] = len(hooks_installed)

        except Exception as e:
            setup_result["error"] = str(e)

        return setup_result

    def run_security_scan(self) -> Dict[str, Any]:
        """Run security scanning tools."""
        security_results = {"timestamp": datetime.now().isoformat(), "scans": []}

        # Run bandit for Python security
        if self.tools_status.get("bandit", {}).get("available", False):
            try:
                result = subprocess.run(
                    ["bandit", "-r", ".", "-f", "json"],
                    capture_output=True,
                    text=True,
                    timeout=60,
                    cwd=self.base_dir,
                )

                bandit_results = json.loads(result.stdout) if result.stdout else {}

                security_results["scans"].append(
                    {
                        "tool": "bandit",
                        "success": result.returncode == 0,
                        "issues_found": len(bandit_results.get("results", [])),
                        "confidence_high": len(
                            [
                                r
                                for r in bandit_results.get("results", [])
                                if r.get("issue_confidence") == "HIGH"
                            ]
                        ),
                        "severity_high": len(
                            [
                                r
                                for r in bandit_results.get("results", [])
                                if r.get("issue_severity") == "HIGH"
                            ]
                        ),
                    }
                )
            except Exception as e:
                security_results["scans"].append(
                    {"tool": "bandit", "success": False, "error": str(e)}
                )

        # Run trunk security checks if available
        if self.tools_status.get("trunk", {}).get("available", False):
            try:
                result = subprocess.run(
                    ["trunk", "check", "--filter=bandit,gitleaks,trufflehog,checkov"],
                    capture_output=True,
                    text=True,
                    timeout=120,
                    cwd=self.base_dir,
                )

                security_results["scans"].append(
                    {
                        "tool": "trunk_security",
                        "success": result.returncode == 0,
                        "output": result.stdout,
                        "issues_detected": "issues found" in result.stdout.lower(),
                    }
                )
            except Exception as e:
                security_results["scans"].append(
                    {"tool": "trunk_security", "success": False, "error": str(e)}
                )

        return security_results

    def cleanup(self) -> None:
        """Clean up plugin resources."""
        pass


# Plugin factory function
def create_plugin(config: Dict[str, Any] = None):
    """Create and return a Code Quality plugin instance."""
    return CodeQualityPlugin(config)


# CLI interface for standalone usage
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Code Quality Plugin CLI")
    parser.add_argument(
        "command",
        choices=["test", "install", "check", "format", "hooks", "security"],
        help="Command to execute",
    )
    parser.add_argument(
        "--language", type=str, help="Language to format (python, javascript)"
    )
    parser.add_argument("--files", nargs="*", help="Specific files to process")
    parser.add_argument("--fix", action="store_true", help="Automatically fix issues")

    args = parser.parse_args()

    try:
        plugin = create_plugin()

        if plugin.initialize():
            print("✅ Code Quality plugin initialized successfully")

            if args.command == "test":
                session_data = plugin.get_session_state()
                print("📊 Code Quality Session Data:")
                print(
                    f"  Available Tools: {session_data.get('available_tools', 0)}/{session_data.get('total_tools', 0)}"
                )
                for tool, status in session_data.get("tools_status", {}).items():
                    icon = "✅" if status["available"] else "❌"
                    print(
                        f"    {icon} {tool}: {status.get('version', 'Not available')}"
                    )

            elif args.command == "install":
                print("📦 Installing missing code quality tools...")
                result = plugin.install_tools()
                print("Installation Results:")
                for installation in result.get("installations", []):
                    status = "✅" if installation["success"] else "❌"
                    print(f"  {status} {installation['tool']}")

            elif args.command == "check":
                print("🔍 Running code quality checks...")
                result = plugin.run_trunk_check(args.files, args.fix)
                if result["success"]:
                    print("✅ Code quality check passed")
                else:
                    print("❌ Code quality issues found")
                    print(result.get("stdout", ""))
                    print(result.get("stderr", ""))

            elif args.command == "format":
                print("🎨 Running code formatters...")
                result = plugin.run_formatting(args.language, args.files)
                print("Formatting Results:")
                for fmt_result in result.get("results", []):
                    status = "✅" if fmt_result["success"] else "❌"
                    print(
                        f"  {status} {fmt_result['tool']}: {fmt_result.get('files', 0)} files"
                    )

            elif args.command == "hooks":
                print("🎣 Setting up Git hooks...")
                result = plugin.setup_git_hooks()
                if result.get("install_success", False):
                    print(
                        f"✅ Git hooks installed: {result.get('hooks_count', 0)} hooks"
                    )
                else:
                    print("❌ Failed to install Git hooks")
                    print(result.get("install_error", ""))

            elif args.command == "security":
                print("🔒 Running security scans...")
                result = plugin.run_security_scan()
                print("Security Scan Results:")
                for scan in result.get("scans", []):
                    status = "✅" if scan["success"] else "❌"
                    tool = scan["tool"]
                    if "issues_found" in scan:
                        print(f"  {status} {tool}: {scan['issues_found']} issues found")
                    else:
                        print(f"  {status} {tool}: Scan completed")

            plugin.cleanup()
            print("✅ All operations completed successfully!")
        else:
            print("❌ Plugin initialization failed")
            sys.exit(1)

    except Exception as e:
        print(f"❌ Plugin operation failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
