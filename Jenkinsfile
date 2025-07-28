pipeline {
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
}