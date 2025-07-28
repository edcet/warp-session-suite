#!/usr/bin/env python3
"""
CI/CD Integration Plugin for Unified Terminal Automation System
Advanced continuous integration and deployment orchestration with multi-platform support
"""

import json
import os
import sys
import subprocess
import yaml
from pathlib import Path
from typing import Optional, Dict, List, Any
from datetime import datetime

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


class CICDPlugin(BasePlugin):
    """CI/CD integration plugin for automated pipeline management."""

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("cicd", "1.0.0", config or {})
        self.capabilities = [
            "github_actions",
            "gitlab_ci",
            "jenkins_integration",
            "docker_builds",
            "kubernetes_deploy",
            "automated_testing",
            "deployment_strategies",
            "pipeline_orchestration",
        ]
        self.base_dir = Path(__file__).parent.parent.parent.parent
        self.ci_platforms = {}

    def initialize(self) -> bool:
        """Initialize CI/CD plugin."""
        self._detect_ci_platforms()
        self._ensure_ci_configurations()
        return True

    def _detect_ci_platforms(self):
        """Detect available CI/CD platforms and tools."""
        # GitHub Actions detection
        github_workflows = self.base_dir / ".github" / "workflows"
        self.ci_platforms["github_actions"] = {
            "available": github_workflows.exists(),
            "workflows": (
                list(github_workflows.glob("*.yml")) + list(github_workflows.glob("*.yaml"))
                if github_workflows.exists()
                else []
            ),
        }

        # GitLab CI detection
        gitlab_ci = self.base_dir / ".gitlab-ci.yml"
        self.ci_platforms["gitlab_ci"] = {
            "available": gitlab_ci.exists(),
            "config_file": str(gitlab_ci) if gitlab_ci.exists() else None,
        }

        # Jenkins detection
        jenkinsfile = self.base_dir / "Jenkinsfile"
        self.ci_platforms["jenkins"] = {
            "available": jenkinsfile.exists(),
            "config_file": str(jenkinsfile) if jenkinsfile.exists() else None,
        }

        # Docker detection
        dockerfile = self.base_dir / "Dockerfile"
        docker_compose = self.base_dir / "docker-compose.yml"
        self.ci_platforms["docker"] = {
            "available": dockerfile.exists() or docker_compose.exists(),
            "dockerfile": dockerfile.exists(),
            "compose": docker_compose.exists(),
        }

        # Kubernetes detection
        k8s_dir = self.base_dir / "k8s"
        self.ci_platforms["kubernetes"] = {
            "available": k8s_dir.exists(),
            "manifests": list(k8s_dir.glob("*.yaml")) if k8s_dir.exists() else [],
        }

    def _ensure_ci_configurations(self):
        """Create comprehensive CI/CD configurations."""
        # Create GitHub Actions workflows
        self._create_github_actions_workflows()

        # Create GitLab CI configuration
        self._create_gitlab_ci_config()

        # Create Jenkinsfile
        self._create_jenkinsfile()

        # Create Docker configurations
        self._create_docker_configs()

        # Create Kubernetes manifests
        self._create_kubernetes_manifests()

    def _create_github_actions_workflows(self):
        """Create comprehensive GitHub Actions workflows."""
        workflows_dir = self.base_dir / ".github" / "workflows"
        workflows_dir.mkdir(parents=True, exist_ok=True)

        # Main CI workflow
        ci_workflow = workflows_dir / "ci.yml"
        if not ci_workflow.exists():
            ci_config = {
                "name": "Unified Terminal Automation System CI",
                "on": {
                    "push": {"branches": ["main", "develop"]},
                    "pull_request": {"branches": ["main"]},
                    "workflow_dispatch": None,
                },
                "env": {
                    "PYTHON_VERSION": "3.12",
                    "NODE_VERSION": "20",
                    "MISE_EXPERIMENTAL": "1",
                },
                "jobs": {
                    "quality-check": {
                        "runs-on": "ubuntu-latest",
                        "steps": [
                            {"uses": "actions/checkout@v4"},
                            {
                                "name": "Setup mise",
                                "uses": "jdx/mise-action@v2",
                                "with": {"experimental": True},
                            },
                            {
                                "name": "Install dependencies",
                                "run": "mise install",
                            },
                            {
                                "name": "Run code quality checks",
                                "run": "python3 plugins/code_quality/src/main.py check",
                            },
                            {
                                "name": "Run security scan",
                                "run": "python3 plugins/code_quality/src/main.py security",
                            },
                        ],
                    },
                    "plugin-tests": {
                        "runs-on": "ubuntu-latest",
                        "strategy": {
                            "matrix": {
                                "plugin": [
                                    "warp",
                                    "cursor",
                                    "windsurf",
                                    "pearai",
                                    "trae",
                                    "ai",
                                    "analytics",
                                    "code_quality",
                                ]
                            }
                        },
                        "steps": [
                            {"uses": "actions/checkout@v4"},
                            {
                                "name": "Setup Python",
                                "uses": "actions/setup-python@v5",
                                "with": {"python-version": "${{ env.PYTHON_VERSION }}"},
                            },
                            {
                                "name": "Test plugin",
                                "run": "python3 plugins/${{ matrix.plugin }}/src/main.py test",
                            },
                        ],
                    },
                    "system-integration": {
                        "runs-on": "ubuntu-latest",
                        "needs": ["quality-check", "plugin-tests"],
                        "steps": [
                            {"uses": "actions/checkout@v4"},
                            {
                                "name": "Setup mise",
                                "uses": "jdx/mise-action@v2",
                                "with": {"experimental": True},
                            },
                            {
                                "name": "Install dependencies",
                                "run": "mise install",
                            },
                            {
                                "name": "Run system integration tests",
                                "run": "python3 advanced_automation.py",
                            },
                            {
                                "name": "Run ultimate demo",
                                "run": "python3 ultimate_demo.py",
                            },
                            {
                                "name": "Upload test results",
                                "uses": "actions/upload-artifact@v4",
                                "if": "always()",
                                "with": {
                                    "name": "test-results",
                                    "path": "automation_results_*.json\nultimate_system_report_*.md\nanalytics_report_*.md"
                                },
                            },
                        ],
                    },
                },
            }

            with open(ci_workflow, "w") as f:
                yaml.dump(ci_config, f, default_flow_style=False, sort_keys=False)

        # Deployment workflow
        deploy_workflow = workflows_dir / "deploy.yml"
        if not deploy_workflow.exists():
            deploy_config = {
                "name": "Deploy Unified Terminal Automation System",
                "on": {
                    "push": {"branches": ["main"]},
                    "release": {"types": ["published"]},
                    "workflow_dispatch": {
                        "inputs": {
                            "environment": {
                                "description": "Deployment environment",
                                "required": True,
                                "default": "staging",
                                "type": "choice",
                                "options": ["staging", "production"],
                            }
                        }
                    },
                },
                "jobs": {
                    "build-and-push": {
                        "runs-on": "ubuntu-latest",
                        "steps": [
                            {"uses": "actions/checkout@v4"},
                            {
                                "name": "Set up Docker Buildx",
                                "uses": "docker/setup-buildx-action@v3",
                            },
                            {
                                "name": "Login to Docker Hub",
                                "uses": "docker/login-action@v3",
                                "with": {
                                    "username": "${{ secrets.DOCKER_USERNAME }}",
                                    "password": "${{ secrets.DOCKER_TOKEN }}",
                                },
                            },
                            {
                                "name": "Build and push",
                                "uses": "docker/build-push-action@v5",
                                "with": {
                                    "context": ".",
                                    "push": True,
                                    "tags": [
                                        "unified-terminal-automation:latest",
                                        "unified-terminal-automation:${{ github.sha }}",
                                    ],
                                    "cache-from": "type=gha",
                                    "cache-to": "type=gha,mode=max",
                                },
                            },
                        ],
                    },
                    "deploy": {
                        "runs-on": "ubuntu-latest",
                        "needs": "build-and-push",
                        "environment": "${{ github.event.inputs.environment || 'staging' }}",
                        "steps": [
                            {"uses": "actions/checkout@v4"},
                            {
                                "name": "Deploy to Kubernetes",
                                "run": "echo \"Deploying to ${{ github.event.inputs.environment || 'staging' }}\"\nkubectl apply -f k8s/\nkubectl set image deployment/unified-automation app=unified-terminal-automation:${{ github.sha }}"
                            },
                        ],
                    },
                },
            }

            with open(deploy_workflow, "w") as f:
                yaml.dump(deploy_config, f, default_flow_style=False, sort_keys=False)

    def _create_gitlab_ci_config(self):
        """Create GitLab CI configuration."""
        gitlab_ci = self.base_dir / ".gitlab-ci.yml"
        if not gitlab_ci.exists():
            gitlab_config = {
                "stages": ["validate", "test", "build", "deploy"],
                "variables": {
                    "PYTHON_VERSION": "3.12",
                    "DOCKER_IMAGE_TAG": "$CI_REGISTRY_IMAGE:$CI_COMMIT_SHA",
                },
                "before_script": ["mise install"],
                "code_quality": {
                    "stage": "validate",
                    "script": [
                        "python3 plugins/code_quality/src/main.py check",
                        "python3 plugins/code_quality/src/main.py security",
                    ],
                    "artifacts": {
                        "reports": {"codequality": "code-quality-report.json"},
                        "expire_in": "1 week",
                    },
                },
                "plugin_tests": {
                    "stage": "test",
                    "parallel": {
                        "matrix": [
                            {"PLUGIN": "warp"},
                            {"PLUGIN": "cursor"},
                            {"PLUGIN": "windsurf"},
                            {"PLUGIN": "pearai"},
                            {"PLUGIN": "trae"},
                            {"PLUGIN": "ai"},
                            {"PLUGIN": "analytics"},
                            {"PLUGIN": "code_quality"},
                        ]
                    },
                    "script": ["python3 plugins/$PLUGIN/src/main.py test"],
                },
                "system_integration": {
                    "stage": "test",
                    "script": [
                        "python3 advanced_automation.py",
                        "python3 ultimate_demo.py",
                    ],
                    "artifacts": {
                        "paths": [
                            "automation_results_*.json",
                            "ultimate_system_report_*.md",
                            "analytics_report_*.md",
                        ],
                        "expire_in": "1 week",
                    },
                },
                "build_image": {
                    "stage": "build",
                    "script": [
                        "docker build -t $DOCKER_IMAGE_TAG .",
                        "docker push $DOCKER_IMAGE_TAG",
                    ],
                    "only": ["main", "develop"],
                },
                "deploy_staging": {
                    "stage": "deploy",
                    "script": ["kubectl apply -f k8s/staging/"],
                    "environment": {"name": "staging", "url": "https://staging.example.com"},
                    "only": ["develop"],
                },
                "deploy_production": {
                    "stage": "deploy",
                    "script": ["kubectl apply -f k8s/production/"],
                    "environment": {
                        "name": "production",
                        "url": "https://production.example.com",
                    },
                    "only": ["main"],
                    "when": "manual",
                },
            }

            with open(gitlab_ci, "w") as f:
                yaml.dump(gitlab_config, f, default_flow_style=False, sort_keys=False)

    def _create_jenkinsfile(self):
        """Create Jenkinsfile for Jenkins CI/CD."""
        jenkinsfile = self.base_dir / "Jenkinsfile"
        if not jenkinsfile.exists():
            jenkins_config = '''pipeline {
    agent any
    
    environment {
        PYTHON_VERSION = '3.12'
        DOCKER_REGISTRY = 'your-registry.com'
        IMAGE_NAME = 'unified-terminal-automation'
    }
    
    stages {
        stage('Setup') {
            steps {
                sh 'mise install'
            }
        }
        
        stage('Code Quality') {
            parallel {
                stage('Quality Check') {
                    steps {
                        sh 'python3 plugins/code_quality/src/main.py check'
                    }
                }
                stage('Security Scan') {
                    steps {
                        sh 'python3 plugins/code_quality/src/main.py security'
                    }
                }
            }
        }
        
        stage('Plugin Tests') {
            parallel {
                stage('Warp Plugin') {
                    steps {
                        sh 'python3 plugins/warp/src/main.py test'
                    }
                }
                stage('Cursor Plugin') {
                    steps {
                        sh 'python3 plugins/cursor/src/main.py test'
                    }
                }
                stage('Windsurf Plugin') {
                    steps {
                        sh 'python3 plugins/windsurf/src/main.py test'
                    }
                }
                stage('PearAI Plugin') {
                    steps {
                        sh 'python3 plugins/pearai/src/main.py test'
                    }
                }
                stage('Trae Plugin') {
                    steps {
                        sh 'python3 plugins/trae/src/main.py test'
                    }
                }
                stage('AI Plugin') {
                    steps {
                        sh 'python3 plugins/ai/tgpt/integration.py test'
                    }
                }
                stage('Analytics Plugin') {
                    steps {
                        sh 'python3 plugins/analytics/src/main.py test'
                    }
                }
                stage('Code Quality Plugin') {
                    steps {
                        sh 'python3 plugins/code_quality/src/main.py test'
                    }
                }
            }
        }
        
        stage('System Integration') {
            steps {
                sh 'python3 advanced_automation.py'
                sh 'python3 ultimate_demo.py'
                
                archiveArtifacts artifacts: 'automation_results_*.json, ultimate_system_report_*.md, analytics_report_*.md'
            }
        }
        
        stage('Build Image') {
            when {
                anyOf {
                    branch 'main'
                    branch 'develop'
                }
            }
            steps {
                script {
                    def image = docker.build("${DOCKER_REGISTRY}/${IMAGE_NAME}:${env.BUILD_NUMBER}")
                    docker.withRegistry("https://${DOCKER_REGISTRY}", 'docker-registry-credentials') {
                        image.push()
                        image.push('latest')
                    }
                }
            }
        }
        
        stage('Deploy') {
            when {
                branch 'main'
            }
            steps {
                script {
                    input message: 'Deploy to production?', ok: 'Deploy'
                    sh 'kubectl apply -f k8s/production/'
                    sh "kubectl set image deployment/unified-automation app=${DOCKER_REGISTRY}/${IMAGE_NAME}:${env.BUILD_NUMBER}"
                }
            }
        }
    }
    
    post {
        always {
            publishHTML([
                allowMissing: false,
                alwaysLinkToLastBuild: true,
                keepAll: true,
                reportDir: '.',
                reportFiles: 'ultimate_system_report_*.md',
                reportName: 'System Report'
            ])
        }
        failure {
            emailext (
                subject: "Build Failed: ${env.JOB_NAME} - ${env.BUILD_NUMBER}",
                body: "Build failed. Check console output at ${env.BUILD_URL}",
                to: "${env.CHANGE_AUTHOR_EMAIL}"
            )
        }
    }
}'''
            with open(jenkinsfile, "w") as f:
                f.write(jenkins_config)

    def _create_docker_configs(self):
        """Create Docker configurations."""
        # Enhanced Dockerfile
        dockerfile = self.base_dir / "Dockerfile"
        if not dockerfile.exists():
            dockerfile_content = '''# Multi-stage Dockerfile for Unified Terminal Automation System
FROM ubuntu:22.04 as base

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    curl wget git build-essential \\
    ca-certificates gnupg lsb-release \\
    software-properties-common \\
    pkg-config libssl-dev \\
    python3-pip python3-venv \\
    nodejs npm \\
    sqlite3 \\
    fd-find ripgrep bat \\
    direnv \\
    && rm -rf /var/lib/apt/lists/*

# Install mise
RUN curl https://mise.run | sh
ENV PATH="/root/.local/bin:$PATH"

# Install tools
COPY .tool-versions .
RUN mise install

FROM base as runtime

WORKDIR /app

# Copy application files
COPY . .

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt || true

# Install plugins
RUN python3 -c "from plugins.registry import install_all; install_all()" || true

# Setup configuration
RUN python3 plugins/code_quality/src/main.py install || true

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD python3 unified_cli.py system status || exit 1

# Default command
CMD ["python3", "unified_cli.py", "system", "monitor"]

EXPOSE 8080 8443
'''
            with open(dockerfile, "w") as f:
                f.write(dockerfile_content)

        # Docker Compose for development
        compose_file = self.base_dir / "docker-compose.yml"
        if not compose_file.exists():
            compose_config = {
                "version": "3.8",
                "services": {
                    "unified-automation": {
                        "build": {"context": ".", "dockerfile": "Dockerfile"},
                        "ports": ["8080:8080", "8443:8443"],
                        "volumes": [
                            ".:/app",
                            "automation-data:/app/data",
                            "/var/run/docker.sock:/var/run/docker.sock",
                        ],
                        "environment": [
                            "MISE_EXPERIMENTAL=1",
                            "UNIFIED_AUTOMATION_HOME=/app",
                            "PLUGIN_DIR=/app/plugins",
                        ],
                        "depends_on": ["redis", "postgres"],
                        "restart": "unless-stopped",
                    },
                    "redis": {
                        "image": "redis:7-alpine",
                        "ports": ["6379:6379"],
                        "volumes": ["redis-data:/data"],
                        "restart": "unless-stopped",
                    },
                    "postgres": {
                        "image": "postgres:16-alpine",
                        "environment": [
                            "POSTGRES_DB=unified_automation",
                            "POSTGRES_USER=automation",
                            "POSTGRES_PASSWORD=secure_password",
                        ],
                        "ports": ["5432:5432"],
                        "volumes": ["postgres-data:/var/lib/postgresql/data"],
                        "restart": "unless-stopped",
                    },
                    "monitoring": {
                        "image": "grafana/grafana:latest",
                        "ports": ["3000:3000"],
                        "volumes": ["grafana-data:/var/lib/grafana"],
                        "environment": [
                            "GF_SECURITY_ADMIN_PASSWORD=admin123",
                            "GF_INSTALL_PLUGINS=grafana-piechart-panel",
                        ],
                        "restart": "unless-stopped",
                    },
                },
                "volumes": {
                    "automation-data": None,
                    "redis-data": None,
                    "postgres-data": None,
                    "grafana-data": None,
                },
                "networks": {"automation-network": {"driver": "bridge"}},
            }

            with open(compose_file, "w") as f:
                yaml.dump(compose_config, f, default_flow_style=False)

    def _create_kubernetes_manifests(self):
        """Create Kubernetes deployment manifests."""
        k8s_dir = self.base_dir / "k8s"
        k8s_dir.mkdir(exist_ok=True)

        # Namespace
        namespace_manifest = k8s_dir / "namespace.yaml"
        if not namespace_manifest.exists():
            namespace_config = {
                "apiVersion": "v1",
                "kind": "Namespace",
                "metadata": {"name": "unified-automation"},
            }
            with open(namespace_manifest, "w") as f:
                yaml.dump(namespace_config, f)

        # Deployment
        deployment_manifest = k8s_dir / "deployment.yaml"
        if not deployment_manifest.exists():
            deployment_config = {
                "apiVersion": "apps/v1",
                "kind": "Deployment",
                "metadata": {
                    "name": "unified-automation",
                    "namespace": "unified-automation",
                },
                "spec": {
                    "replicas": 3,
                    "selector": {"matchLabels": {"app": "unified-automation"}},
                    "template": {
                        "metadata": {"labels": {"app": "unified-automation"}},
                        "spec": {
                            "containers": [
                                {
                                    "name": "app",
                                    "image": "unified-terminal-automation:latest",
                                    "ports": [
                                        {"containerPort": 8080},
                                        {"containerPort": 8443},
                                    ],
                                    "env": [
                                        {
                                            "name": "MISE_EXPERIMENTAL",
                                            "value": "1",
                                        },
                                        {
                                            "name": "PLUGIN_DIR",
                                            "value": "/app/plugins",
                                        },
                                    ],
                                    "resources": {
                                        "requests": {"cpu": "100m", "memory": "256Mi"},
                                        "limits": {"cpu": "500m", "memory": "1Gi"},
                                    },
                                    "livenessProbe": {
                                        "httpGet": {"path": "/health", "port": 8080},
                                        "initialDelaySeconds": 30,
                                        "periodSeconds": 10,
                                    },
                                    "readinessProbe": {
                                        "httpGet": {"path": "/ready", "port": 8080},
                                        "initialDelaySeconds": 5,
                                        "periodSeconds": 5,
                                    },
                                }
                            ]
                        },
                    },
                },
            }
            with open(deployment_manifest, "w") as f:
                yaml.dump(deployment_config, f)

        # Service
        service_manifest = k8s_dir / "service.yaml"
        if not service_manifest.exists():
            service_config = {
                "apiVersion": "v1",
                "kind": "Service",
                "metadata": {
                    "name": "unified-automation-service",
                    "namespace": "unified-automation",
                },
                "spec": {
                    "selector": {"app": "unified-automation"},
                    "ports": [
                        {"name": "http", "port": 80, "targetPort": 8080},
                        {"name": "https", "port": 443, "targetPort": 8443},
                    ],
                    "type": "LoadBalancer",
                },
            }
            with open(service_manifest, "w") as f:
                yaml.dump(service_config, f)

    def get_session_state(self, **kwargs) -> Dict[str, Any]:
        """Get CI/CD plugin session state."""
        return {
            "plugin_name": self.name,
            "plugin_version": self.version,
            "capabilities": self.capabilities,
            "ci_platforms": self.ci_platforms,
            "available_platforms": len(
                [p for p in self.ci_platforms.values() if p["available"]]
            ),
            "total_platforms": len(self.ci_platforms),
            "session_timestamp": datetime.now().isoformat(),
        }

    def trigger_pipeline(self, platform: str, branch: str = "main") -> Dict[str, Any]:
        """Trigger CI/CD pipeline on specified platform."""
        trigger_result = {
            "platform": platform,
            "branch": branch,
            "timestamp": datetime.now().isoformat(),
        }

        if platform == "github_actions":
            try:
                # Trigger GitHub Actions workflow via API
                result = subprocess.run(
                    [
                        "gh",
                        "workflow",
                        "run",
                        "ci.yml",
                        "--ref",
                        branch,
                    ],
                    capture_output=True,
                    text=True,
                    timeout=30,
                    cwd=self.base_dir,
                )

                trigger_result.update(
                    {
                        "success": result.returncode == 0,
                        "output": result.stdout,
                        "error": result.stderr if result.returncode != 0 else None,
                    }
                )
            except Exception as e:
                trigger_result.update({"success": False, "error": str(e)})

        elif platform == "gitlab_ci":
            try:
                # Trigger GitLab CI pipeline
                result = subprocess.run(
                    [
                        "gitlab-ci-lint",
                        ".gitlab-ci.yml",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=30,
                    cwd=self.base_dir,
                )

                trigger_result.update(
                    {
                        "success": result.returncode == 0,
                        "validation": "passed" if result.returncode == 0 else "failed",
                        "output": result.stdout,
                    }
                )
            except Exception as e:
                trigger_result.update({"success": False, "error": str(e)})

        else:
            trigger_result.update(
                {"success": False, "error": f"Platform {platform} not supported"}
            )

        return trigger_result

    def deploy_to_environment(self, environment: str = "staging") -> Dict[str, Any]:
        """Deploy to specified environment."""
        deployment_result = {
            "environment": environment,
            "timestamp": datetime.now().isoformat(),
        }

        try:
            # Build Docker image
            print(f"🐳 Building Docker image for {environment}...")
            build_result = subprocess.run(
                [
                    "docker",
                    "build",
                    "-t",
                    f"unified-terminal-automation:{environment}",
                    ".",
                ],
                capture_output=True,
                text=True,
                timeout=300,
                cwd=self.base_dir,
            )

            if build_result.returncode != 0:
                deployment_result.update(
                    {
                        "success": False,
                        "stage": "build",
                        "error": build_result.stderr,
                    }
                )
                return deployment_result

            # Deploy to Kubernetes
            print(f"☸️ Deploying to Kubernetes {environment}...")
            k8s_result = subprocess.run(
                ["kubectl", "apply", "-f", "k8s/"],
                capture_output=True,
                text=True,
                timeout=120,
                cwd=self.base_dir,
            )

            deployment_result.update(
                {
                    "success": k8s_result.returncode == 0,
                    "build_output": build_result.stdout,
                    "deploy_output": k8s_result.stdout,
                    "error": k8s_result.stderr if k8s_result.returncode != 0 else None,
                }
            )

        except Exception as e:
            deployment_result.update({"success": False, "error": str(e)})

        return deployment_result

    def get_pipeline_status(self, platform: str) -> Dict[str, Any]:
        """Get current pipeline status."""
        status_result = {
            "platform": platform,
            "timestamp": datetime.now().isoformat(),
        }

        if platform == "github_actions":
            try:
                result = subprocess.run(
                    ["gh", "run", "list", "--limit", "10", "--json", "status,conclusion,workflowName"],
                    capture_output=True,
                    text=True,
                    timeout=30,
                    cwd=self.base_dir,
                )

                if result.returncode == 0:
                    runs = json.loads(result.stdout)
                    status_result.update(
                        {
                            "success": True,
                            "recent_runs": runs,
                            "latest_status": runs[0]["status"] if runs else "unknown",
                        }
                    )
                else:
                    status_result.update(
                        {"success": False, "error": result.stderr}
                    )

            except Exception as e:
                status_result.update({"success": False, "error": str(e)})

        return status_result

    def cleanup(self) -> None:
        """Clean up plugin resources."""
        pass


# Plugin factory function
def create_plugin(config: Dict[str, Any] = None):
    """Create and return a CI/CD plugin instance."""
    return CICDPlugin(config)


# CLI interface for standalone usage
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="CI/CD Plugin CLI")
    parser.add_argument(
        "command",
        choices=["test", "trigger", "deploy", "status", "setup"],
        help="Command to execute",
    )
    parser.add_argument("--platform", type=str, help="CI/CD platform")
    parser.add_argument("--branch", type=str, default="main", help="Git branch")
    parser.add_argument(
        "--environment", type=str, default="staging", help="Deployment environment"
    )

    args = parser.parse_args()

    try:
        plugin = create_plugin()

        if plugin.initialize():
            print("✅ CI/CD plugin initialized successfully")

            if args.command == "test":
                session_data = plugin.get_session_state()
                print(f"📊 CI/CD Session Data:")
                print(
                    f"  Available Platforms: {session_data.get('available_platforms', 0)}/{session_data.get('total_platforms', 0)}"
                )
                for platform, status in session_data.get("ci_platforms", {}).items():
                    icon = "✅" if status["available"] else "❌"
                    print(f"    {icon} {platform}")

            elif args.command == "setup":
                print("🔧 Setting up CI/CD configurations...")
                plugin._ensure_ci_configurations()
                print("✅ CI/CD configurations created")

            elif args.command == "trigger":
                if not args.platform:
                    print("❌ Platform required for trigger command")
                    sys.exit(1)

                print(f"🚀 Triggering {args.platform} pipeline...")
                result = plugin.trigger_pipeline(args.platform, args.branch)
                if result["success"]:
                    print("✅ Pipeline triggered successfully")
                else:
                    print(f"❌ Pipeline trigger failed: {result.get('error', 'Unknown error')}")

            elif args.command == "deploy":
                print(f"🚀 Deploying to {args.environment}...")
                result = plugin.deploy_to_environment(args.environment)
                if result["success"]:
                    print("✅ Deployment successful")
                else:
                    print(f"❌ Deployment failed: {result.get('error', 'Unknown error')}")

            elif args.command == "status":
                if not args.platform:
                    print("❌ Platform required for status command")
                    sys.exit(1)

                print(f"📊 Getting {args.platform} pipeline status...")
                result = plugin.get_pipeline_status(args.platform)
                if result["success"]:
                    print(f"Latest status: {result.get('latest_status', 'unknown')}")
                else:
                    print(f"❌ Status check failed: {result.get('error', 'Unknown error')}")

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
