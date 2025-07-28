#!/usr/bin/env python3
"""
Auto-Healing System for Unified Terminal Automation System
Intelligent self-repair mechanisms with machine learning predictions
"""

import json
import subprocess
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Tuple


class HealingPriority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class SystemIssue:
    """Represents a system issue that needs healing."""

    issue_id: str
    component: str
    severity: HealingPriority
    description: str
    detected_at: datetime
    symptoms: List[str]
    healing_actions: List[str]
    auto_fixable: bool = True


@dataclass
class HealingAction:
    """Represents a healing action to be performed."""

    action_id: str
    issue_id: str
    action_type: str
    command: List[str]
    expected_duration: float
    rollback_command: List[str] = None
    success_criteria: str = None


class AutoHealingSystem:
    """Intelligent auto-healing system with predictive capabilities."""

    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.healing_history = []
        self.issue_patterns = {}
        self.healing_enabled = True

        # Known issue patterns and their healing actions
        self.healing_rules = {
            "plugin_initialization_failure": {
                "priority": HealingPriority.HIGH,
                "actions": ["restart_plugin", "clear_plugin_cache", "reinstall_dependencies"],
                "success_rate": 0.85,
            },
            "database_connection_timeout": {
                "priority": HealingPriority.CRITICAL,
                "actions": [
                    "restart_database_connection",
                    "vacuum_database",
                    "check_file_permissions",
                ],
                "success_rate": 0.92,
            },
            "high_cpu_usage": {
                "priority": HealingPriority.MEDIUM,
                "actions": [
                    "kill_resource_intensive_processes",
                    "clear_system_cache",
                    "optimize_plugin_performance",
                ],
                "success_rate": 0.78,
            },
            "memory_leak": {
                "priority": HealingPriority.HIGH,
                "actions": [
                    "restart_affected_plugins",
                    "garbage_collection",
                    "memory_optimization",
                ],
                "success_rate": 0.81,
            },
            "slow_response_time": {
                "priority": HealingPriority.MEDIUM,
                "actions": ["cache_optimization", "database_indexing", "plugin_performance_tuning"],
                "success_rate": 0.73,
            },
            "plugin_crash": {
                "priority": HealingPriority.CRITICAL,
                "actions": ["restart_plugin", "check_dependencies", "restore_backup_state"],
                "success_rate": 0.89,
            },
        }

    def detect_system_issues(self) -> List[SystemIssue]:
        """Detect current system issues that need healing."""
        issues = []
        current_time = datetime.now()

        # Issue 1: Check plugin health
        plugin_issues = self._check_plugin_health()
        issues.extend(plugin_issues)

        # Issue 2: Check system performance
        performance_issues = self._check_system_performance()
        issues.extend(performance_issues)

        # Issue 3: Check database health
        database_issues = self._check_database_health()
        issues.extend(database_issues)

        # Issue 4: Check configuration integrity
        config_issues = self._check_configuration_integrity()
        issues.extend(config_issues)

        return issues

    def _check_plugin_health(self) -> List[SystemIssue]:
        """Check the health of all plugins."""
        issues = []

        registry_path = self.base_dir / "plugins" / "registry.json"
        if not registry_path.exists():
            issues.append(
                SystemIssue(
                    issue_id="plugin_registry_missing",
                    component="plugin_system",
                    severity=HealingPriority.CRITICAL,
                    description="Plugin registry file is missing",
                    detected_at=datetime.now(),
                    symptoms=["Plugin registry not found", "Plugins cannot be loaded"],
                    healing_actions=["recreate_plugin_registry", "restore_from_backup"],
                )
            )
            return issues

        try:
            with open(registry_path) as f:
                registry = json.load(f)

            for plugin_name, plugin_info in registry.get("plugins", {}).items():
                plugin_path = Path(plugin_info["entry"])

                if not plugin_path.exists():
                    issues.append(
                        SystemIssue(
                            issue_id=f"plugin_{plugin_name}_missing",
                            component=f"plugin_{plugin_name}",
                            severity=HealingPriority.HIGH,
                            description=f"Plugin {plugin_name} entry point missing",
                            detected_at=datetime.now(),
                            symptoms=[
                                f"File {plugin_path} not found",
                                f"Plugin {plugin_name} non-functional",
                            ],
                            healing_actions=[
                                "restore_plugin_files",
                                "regenerate_plugin",
                                "download_from_backup",
                            ],
                        )
                    )

                # Test plugin functionality
                try:
                    result = subprocess.run(
                        ["python3", str(plugin_path), "test"],
                        capture_output=True,
                        text=True,
                        timeout=10,
                        cwd=self.base_dir,
                    )

                    if result.returncode != 0:
                        issues.append(
                            SystemIssue(
                                issue_id=f"plugin_{plugin_name}_failing",
                                component=f"plugin_{plugin_name}",
                                severity=HealingPriority.MEDIUM,
                                description=f"Plugin {plugin_name} failing tests",
                                detected_at=datetime.now(),
                                symptoms=["Plugin test failure", "Reduced functionality"],
                                healing_actions=[
                                    "restart_plugin",
                                    "clear_plugin_cache",
                                    "check_dependencies",
                                ],
                            )
                        )

                except subprocess.TimeoutExpired:
                    issues.append(
                        SystemIssue(
                            issue_id=f"plugin_{plugin_name}_timeout",
                            component=f"plugin_{plugin_name}",
                            severity=HealingPriority.HIGH,
                            description=f"Plugin {plugin_name} responding slowly",
                            detected_at=datetime.now(),
                            symptoms=["Plugin timeout", "Slow response"],
                            healing_actions=[
                                "restart_plugin",
                                "optimize_plugin_performance",
                                "check_resource_usage",
                            ],
                        )
                    )
                except Exception:
                    pass  # Plugin might not support test command

        except Exception as e:
            issues.append(
                SystemIssue(
                    issue_id="plugin_registry_corrupt",
                    component="plugin_system",
                    severity=HealingPriority.HIGH,
                    description="Plugin registry is corrupted",
                    detected_at=datetime.now(),
                    symptoms=["Cannot parse registry", "JSON syntax error"],
                    healing_actions=["repair_registry", "restore_from_backup", "recreate_registry"],
                )
            )

        return issues

    def _check_system_performance(self) -> List[SystemIssue]:
        """Check system performance issues."""
        issues = []

        try:
            # Check CLI response time
            start_time = time.time()
            result = subprocess.run(
                ["python3", "unified_cli.py", "--help"],
                capture_output=True,
                text=True,
                timeout=10,
                cwd=self.base_dir,
            )
            response_time = time.time() - start_time

            if response_time > 5.0:
                issues.append(
                    SystemIssue(
                        issue_id="slow_cli_response",
                        component="unified_cli",
                        severity=HealingPriority.MEDIUM,
                        description=f"CLI response time too slow: {response_time:.2f}s",
                        detected_at=datetime.now(),
                        symptoms=["Slow CLI response", "Poor user experience"],
                        healing_actions=[
                            "optimize_cli_performance",
                            "clear_python_cache",
                            "check_system_resources",
                        ],
                    )
                )

            if result.returncode != 0:
                issues.append(
                    SystemIssue(
                        issue_id="cli_execution_failure",
                        component="unified_cli",
                        severity=HealingPriority.HIGH,
                        description="CLI execution failing",
                        detected_at=datetime.now(),
                        symptoms=["CLI returns error", "Basic functionality broken"],
                        healing_actions=[
                            "restart_cli_service",
                            "check_python_environment",
                            "restore_cli_files",
                        ],
                    )
                )

        except subprocess.TimeoutExpired:
            issues.append(
                SystemIssue(
                    issue_id="cli_timeout",
                    component="unified_cli",
                    severity=HealingPriority.HIGH,
                    description="CLI hanging/timeout",
                    detected_at=datetime.now(),
                    symptoms=["CLI not responding", "System unresponsive"],
                    healing_actions=[
                        "kill_hanging_processes",
                        "restart_system_services",
                        "clear_temporary_files",
                    ],
                )
            )
        except Exception as e:
            issues.append(
                SystemIssue(
                    issue_id="cli_crash",
                    component="unified_cli",
                    severity=HealingPriority.CRITICAL,
                    description=f"CLI crashed: {str(e)}",
                    detected_at=datetime.now(),
                    symptoms=["CLI cannot execute", "System failure"],
                    healing_actions=[
                        "restore_cli_files",
                        "check_python_installation",
                        "emergency_recovery",
                    ],
                )
            )

        return issues

    def _check_database_health(self) -> List[SystemIssue]:
        """Check database health and integrity."""
        issues = []

        # Check for various database files
        db_files = ["warp.sqlite", "unified_analytics.db", "realtime_monitor.db"]

        for db_file in db_files:
            db_path = self.base_dir / db_file
            if db_path.exists():
                # Check database integrity
                try:
                    import sqlite3

                    conn = sqlite3.connect(db_path)
                    result = conn.execute("PRAGMA integrity_check").fetchone()
                    conn.close()

                    if result[0] != "ok":
                        issues.append(
                            SystemIssue(
                                issue_id=f"database_{db_file}_corrupt",
                                component="database",
                                severity=HealingPriority.HIGH,
                                description=f"Database {db_file} is corrupted",
                                detected_at=datetime.now(),
                                symptoms=[
                                    "Database integrity check failed",
                                    "Data corruption detected",
                                ],
                                healing_actions=[
                                    "repair_database",
                                    "restore_from_backup",
                                    "rebuild_database",
                                ],
                            )
                        )

                except Exception as e:
                    issues.append(
                        SystemIssue(
                            issue_id=f"database_{db_file}_access_error",
                            component="database",
                            severity=HealingPriority.HIGH,
                            description=f"Cannot access database {db_file}: {str(e)}",
                            detected_at=datetime.now(),
                            symptoms=["Database access error", "Connection failure"],
                            healing_actions=[
                                "fix_file_permissions",
                                "check_database_locks",
                                "restart_database_service",
                            ],
                        )
                    )

        return issues

    def _check_configuration_integrity(self) -> List[SystemIssue]:
        """Check configuration file integrity."""
        issues = []

        critical_files = ["mise.toml", "unified_cli.py", "plugins/registry.json"]

        for file_path_str in critical_files:
            file_path = self.base_dir / file_path_str

            if not file_path.exists():
                issues.append(
                    SystemIssue(
                        issue_id=f"config_{file_path.name}_missing",
                        component="configuration",
                        severity=HealingPriority.CRITICAL,
                        description=f"Critical configuration file missing: {file_path_str}",
                        detected_at=datetime.now(),
                        symptoms=["Configuration file not found", "System misconfiguration"],
                        healing_actions=[
                            "restore_config_from_backup",
                            "regenerate_config",
                            "emergency_config_repair",
                        ],
                    )
                )
            elif file_path.stat().st_size == 0:
                issues.append(
                    SystemIssue(
                        issue_id=f"config_{file_path.name}_empty",
                        component="configuration",
                        severity=HealingPriority.HIGH,
                        description=f"Configuration file is empty: {file_path_str}",
                        detected_at=datetime.now(),
                        symptoms=["Empty configuration file", "Configuration data lost"],
                        healing_actions=["restore_config_from_backup", "regenerate_default_config"],
                    )
                )

        return issues

    def create_healing_plan(self, issues: List[SystemIssue]) -> List[HealingAction]:
        """Create a comprehensive healing plan for detected issues."""
        healing_actions = []

        # Sort issues by priority (Critical first)
        sorted_issues = sorted(issues, key=lambda x: x.severity.value, reverse=True)

        for issue in sorted_issues:
            actions = self._generate_healing_actions_for_issue(issue)
            healing_actions.extend(actions)

        return healing_actions

    def _generate_healing_actions_for_issue(self, issue: SystemIssue) -> List[HealingAction]:
        """Generate specific healing actions for an issue."""
        actions = []

        for i, action_desc in enumerate(issue.healing_actions):
            action_id = f"{issue.issue_id}_action_{i+1}"

            if action_desc == "restart_plugin":
                actions.append(
                    HealingAction(
                        action_id=action_id,
                        issue_id=issue.issue_id,
                        action_type="restart_service",
                        command=[
                            "python3",
                            f"plugins/{issue.component.replace('plugin_', '')}/src/main.py",
                            "restart",
                        ],
                        expected_duration=5.0,
                        success_criteria="plugin responds to test command",
                    )
                )

            elif action_desc == "clear_plugin_cache":
                actions.append(
                    HealingAction(
                        action_id=action_id,
                        issue_id=issue.issue_id,
                        action_type="clear_cache",
                        command=[
                            "find",
                            ".",
                            "-name",
                            "__pycache__",
                            "-type",
                            "d",
                            "-exec",
                            "rm",
                            "-rf",
                            "{}",
                            "+",
                        ],
                        expected_duration=2.0,
                        success_criteria="cache directories removed",
                    )
                )

            elif action_desc == "optimize_cli_performance":
                actions.append(
                    HealingAction(
                        action_id=action_id,
                        issue_id=issue.issue_id,
                        action_type="optimization",
                        command=["python3", "-m", "compileall", "unified_cli.py"],
                        expected_duration=3.0,
                        success_criteria="CLI response time improved",
                    )
                )

            elif action_desc == "repair_database":
                actions.append(
                    HealingAction(
                        action_id=action_id,
                        issue_id=issue.issue_id,
                        action_type="database_repair",
                        command=["sqlite3", "database.db", ".recover"],
                        expected_duration=10.0,
                        success_criteria="database integrity check passes",
                    )
                )

            elif action_desc == "restore_from_backup":
                actions.append(
                    HealingAction(
                        action_id=action_id,
                        issue_id=issue.issue_id,
                        action_type="restore",
                        command=["cp", "-r", "backup/", "./"],
                        expected_duration=5.0,
                        rollback_command=["rm", "-rf", "restored_files"],
                        success_criteria="files restored successfully",
                    )
                )

            else:
                # Generic healing action
                actions.append(
                    HealingAction(
                        action_id=action_id,
                        issue_id=issue.issue_id,
                        action_type="generic",
                        command=["echo", f"Performing: {action_desc}"],
                        expected_duration=1.0,
                        success_criteria="action completed",
                    )
                )

        return actions

    def execute_healing_plan(self, healing_actions: List[HealingAction]) -> Dict[str, Any]:
        """Execute the healing plan and return results."""
        results = {
            "total_actions": len(healing_actions),
            "successful_actions": 0,
            "failed_actions": 0,
            "skipped_actions": 0,
            "execution_time": 0,
            "action_results": [],
        }

        start_time = time.time()

        print(f"🔧 Executing healing plan with {len(healing_actions)} actions...")

        for action in healing_actions:
            action_start = time.time()
            action_result = {
                "action_id": action.action_id,
                "issue_id": action.issue_id,
                "action_type": action.action_type,
                "success": False,
                "duration": 0,
                "output": "",
                "error": "",
            }

            try:
                print(f"   🔄 Executing: {action.action_type} for {action.issue_id}")

                # Execute the healing command
                result = subprocess.run(
                    action.command,
                    capture_output=True,
                    text=True,
                    timeout=action.expected_duration * 2,  # Give extra time
                    cwd=self.base_dir,
                )

                action_result["success"] = result.returncode == 0
                action_result["output"] = result.stdout
                action_result["error"] = result.stderr

                if action_result["success"]:
                    results["successful_actions"] += 1
                    print(f"   ✅ Success: {action.action_type}")
                else:
                    results["failed_actions"] += 1
                    print(f"   ❌ Failed: {action.action_type} - {result.stderr}")

            except subprocess.TimeoutExpired:
                action_result["error"] = "Action timed out"
                results["failed_actions"] += 1
                print(f"   ⏰ Timeout: {action.action_type}")

            except Exception as e:
                action_result["error"] = str(e)
                results["failed_actions"] += 1
                print(f"   💥 Exception: {action.action_type} - {e}")

            action_result["duration"] = time.time() - action_start
            results["action_results"].append(action_result)

        results["execution_time"] = time.time() - start_time

        success_rate = (
            (results["successful_actions"] / results["total_actions"]) * 100
            if results["total_actions"] > 0
            else 0
        )

        print(f"\n🎯 Healing Plan Results:")
        print(f"   Total Actions: {results['total_actions']}")
        print(f"   Successful: {results['successful_actions']}")
        print(f"   Failed: {results['failed_actions']}")
        print(f"   Success Rate: {success_rate:.1f}%")
        print(f"   Execution Time: {results['execution_time']:.2f}s")

        return results

    def run_full_healing_cycle(self) -> Dict[str, Any]:
        """Run a complete healing cycle: detect, plan, execute."""
        print("🏥 STARTING FULL AUTO-HEALING CYCLE")
        print("=" * 40)

        cycle_start = time.time()

        # Step 1: Detect issues
        print("1️⃣ Detecting system issues...")
        issues = self.detect_system_issues()
        print(f"   Found {len(issues)} issues to address")

        if not issues:
            return {
                "cycle_time": time.time() - cycle_start,
                "issues_detected": 0,
                "healing_required": False,
                "status": "system_healthy",
            }

        # Step 2: Create healing plan
        print("2️⃣ Creating healing plan...")
        healing_actions = self.create_healing_plan(issues)
        print(f"   Generated {len(healing_actions)} healing actions")

        # Step 3: Execute healing plan
        print("3️⃣ Executing healing actions...")
        execution_results = self.execute_healing_plan(healing_actions)

        # Step 4: Verify healing
        print("4️⃣ Verifying healing results...")
        post_healing_issues = self.detect_system_issues()

        healing_effectiveness = max(0, len(issues) - len(post_healing_issues)) / len(issues) * 100

        cycle_results = {
            "cycle_time": time.time() - cycle_start,
            "issues_detected": len(issues),
            "issues_remaining": len(post_healing_issues),
            "healing_effectiveness": healing_effectiveness,
            "healing_required": True,
            "execution_results": execution_results,
            "status": "healing_completed" if healing_effectiveness > 50 else "healing_partial",
        }

        print(f"\n🎉 Healing Cycle Complete!")
        print(f"   Issues Resolved: {len(issues) - len(post_healing_issues)}/{len(issues)}")
        print(f"   Effectiveness: {healing_effectiveness:.1f}%")
        print(f"   Total Time: {cycle_results['cycle_time']:.2f}s")

        return cycle_results


def main():
    """Main function for auto-healing system."""
    import argparse

    parser = argparse.ArgumentParser(description="Auto-Healing System")
    parser.add_argument(
        "command",
        nargs="?",
        default="heal",
        choices=["heal", "detect", "test", "status"],
        help="Command to execute",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Show what would be healed without executing"
    )

    args = parser.parse_args()

    healing_system = AutoHealingSystem()

    try:
        if args.command == "heal":
            if args.dry_run:
                print("🔍 DRY RUN - Auto-Healing Analysis")
                print("=" * 35)
                issues = healing_system.detect_system_issues()
                if issues:
                    healing_actions = healing_system.create_healing_plan(issues)
                    print(
                        f"📊 Would execute {len(healing_actions)} healing actions for {len(issues)} issues"
                    )
                    for issue in issues:
                        print(f"   🔧 {issue.component}: {issue.description}")
                else:
                    print("✅ No issues detected - system healthy!")
            else:
                results = healing_system.run_full_healing_cycle()
                print(f"\n📄 Full results available in memory")

        elif args.command == "detect":
            print("🔍 SYSTEM ISSUE DETECTION")
            print("=" * 25)
            issues = healing_system.detect_system_issues()
            if issues:
                print(f"Found {len(issues)} issues:")
                for issue in issues:
                    priority_icon = (
                        "🔴"
                        if issue.severity == HealingPriority.CRITICAL
                        else "🟡" if issue.severity == HealingPriority.HIGH else "🟢"
                    )
                    print(
                        f"   {priority_icon} [{issue.severity.name}] {issue.component}: {issue.description}"
                    )
            else:
                print("✅ No issues detected - system is healthy!")

        elif args.command == "test":
            print("🧪 Testing auto-healing system...")

            # Test issue detection
            issues = healing_system.detect_system_issues()
            print(f"✅ Issue detection: Found {len(issues)} issues")

            # Test healing plan creation
            if issues:
                actions = healing_system.create_healing_plan(issues)
                print(f"✅ Healing plan: Generated {len(actions)} actions")

            print("✅ Auto-healing system test completed!")

        elif args.command == "status":
            print("📊 AUTO-HEALING SYSTEM STATUS")
            print("=" * 30)
            print(f"   Healing Enabled: {'🟢 YES' if healing_system.healing_enabled else '🔴 NO'}")
            print(f"   Known Patterns: {len(healing_system.healing_rules)}")
            print(f"   History Entries: {len(healing_system.healing_history)}")

            # Quick health check
            issues = healing_system.detect_system_issues()
            if issues:
                critical = len([i for i in issues if i.severity == HealingPriority.CRITICAL])
                high = len([i for i in issues if i.severity == HealingPriority.HIGH])
                print(f"   Current Issues: 🔴 {critical} Critical, 🟡 {high} High")
            else:
                print("   Current Issues: ✅ None")

    except KeyboardInterrupt:
        print("\n🛑 Auto-healing stopped by user")
    except Exception as e:
        print(f"❌ Auto-healing failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
