pipeline {
    agent any

    options {
        skipDefaultCheckout(true)
        disableConcurrentBuilds()
    }

    parameters {
        string(name: 'REPO_URL', defaultValue: 'https://github.com/Ghost-3451/cicd-demo-app.git')
        string(name: 'GIT_BRANCH', defaultValue: 'master')
        booleanParam(name: 'RUN_TESTS', defaultValue: true)
        booleanParam(name: 'DEPLOY', defaultValue: false)
        string(name: 'APP_PORT', defaultValue: '18080')
    }

    environment {
        DOCKER_HOST = 'unix:///var/run/docker.sock'
        ANSIBLE_COLLECTIONS_PATH = '/opt/jenkins-ansible/collections'
    }

    stages {
        stage('Checkout') {
            steps {
                deleteDir()
                script {
                    env.COMMIT_SHA = 'not-checked-out'
                    env.SHORT_SHA = 'unknown'
                    env.APP_IMAGE = 'not-built'
                    env.IMAGE_BUILT = 'false'
                    env.PREVIOUS_IMAGE = 'none'
                    echo "Branch: ${params.GIT_BRANCH}"
                    echo "BUILD_NUMBER: ${env.BUILD_NUMBER}"
                    if (params.REPO_URL.trim() && params.GIT_BRANCH.trim()) {
                        git branch: params.GIT_BRANCH.trim(), url: params.REPO_URL.trim()
                        env.COMMIT_SHA = sh(script: 'git rev-parse HEAD', returnStdout: true).trim()
                        env.SHORT_SHA = sh(script: 'git rev-parse --short=12 HEAD', returnStdout: true).trim()
                        echo "Commit SHA: ${env.COMMIT_SHA}"
                    } else {
                        echo 'Checkout skipped: empty source parameters; see Validate.'
                    }
                }
            }
        }

        stage('Validate') {
            steps {
                script {
                    if (!params.REPO_URL.trim() || !params.GIT_BRANCH.trim()) {
                        error 'REPO_URL and GIT_BRANCH must not be empty.'
                    }
                    def port = params.APP_PORT.trim()
                    if (!(port ==~ /[0-9]{1,5}/) || port.toInteger() < 1024 || port.toInteger() > 65535) {
                        error 'APP_PORT must be an integer between 1024 and 65535.'
                    }
                    env.SERVICE_PORT = port.toInteger().toString()
                    if (params.DEPLOY && !params.RUN_TESTS) {
                        error 'DEPLOY=true requires RUN_TESTS=true. Deployment is blocked.'
                    }
                    def required = [
                        'README.md', 'requirements.txt', 'src', 'tests',
                        'src/calculator.py', 'src/http_server.py',
                        'tests/test_calculator.py', 'tests/test_http_server.py',
                        'Dockerfile', '.dockerignore', 'Jenkinsfile',
                        'ansible/deploy.yml', 'ansible/requirements.yml',
                        'scripts/run-ansible.sh', 'scripts/verify.sh'
                    ]
                    for (item in required) {
                        if (!fileExists(item)) {
                            error "Validation failed: missing ${item}"
                        }
                    }
                    echo "Validation passed. APP_PORT=${env.SERVICE_PORT}"
                }
            }
        }

        stage('Lint') {
            steps {
                sh '''#!/usr/bin/env bash
set -euo pipefail
python3 -m venv .venv
.venv/bin/python -m pip install --disable-pip-version-check -r requirements.txt
.venv/bin/flake8 src tests 2>&1 | tee lint.log
'''
            }
        }

        stage('Test') {
            when {
                expression { params.RUN_TESTS }
            }
            steps {
                sh '''#!/usr/bin/env bash
set -uo pipefail
.venv/bin/coverage erase
.venv/bin/coverage run -m unittest discover -s tests -v 2>&1 | tee unit-tests.log
test_status=$?
.venv/bin/coverage xml -o coverage.xml
coverage_status=$?
if [ "$test_status" -ne 0 ]; then
    exit "$test_status"
fi
exit "$coverage_status"
'''
            }
        }

        stage('Build Image') {
            steps {
                script {
                    env.APP_IMAGE = "student-app:${env.BUILD_NUMBER}-${env.SHORT_SHA}"
                    sh 'docker build --tag "$APP_IMAGE" .'
                    env.IMAGE_BUILT = 'true'
                    echo "Docker image: ${env.APP_IMAGE}"
                }
            }
        }

        stage('Deploy') {
            when {
                expression { params.DEPLOY }
            }
            steps {
                script {
                    env.PREVIOUS_IMAGE = sh(
                        script: "docker inspect --format='{{.Config.Image}}' student-app 2>/dev/null || true",
                        returnStdout: true
                    ).trim()
                    writeFile file: 'deploy-vars.json', text: """{
  "app_image": "${env.APP_IMAGE}",
  "app_port": ${env.SERVICE_PORT}
}
"""
                }
                sh '''#!/usr/bin/env bash
set -euo pipefail
bash scripts/run-ansible.sh ansible/deploy.yml --extra-vars @deploy-vars.json 2>&1 | tee deploy.log
'''
            }
        }

        stage('Verify') {
            when {
                expression { params.DEPLOY }
            }
            steps {
                sh '''#!/usr/bin/env bash
set -euo pipefail
bash scripts/verify.sh "$SERVICE_PORT" 2>&1 | tee verify.log
'''
            }
        }
    }

    post {
        always {
            script {
                def result = currentBuild.currentResult
                writeFile file: 'build-info.txt', text: """Build Number: ${env.BUILD_NUMBER}
Branch: ${params.GIT_BRANCH}
Commit SHA: ${env.COMMIT_SHA}
Docker image: ${env.APP_IMAGE}
Image built: ${env.IMAGE_BUILT}
RUN_TESTS: ${params.RUN_TESTS}
DEPLOY: ${params.DEPLOY}
APP_PORT: ${params.APP_PORT}
Previous image: ${env.PREVIOUS_IMAGE}
Result: ${result}
"""
                echo "Pipeline result: ${result}"
            }
            archiveArtifacts artifacts: 'build-info.txt,coverage.xml,lint.log,unit-tests.log,deploy.log,verify.log', allowEmptyArchive: true, fingerprint: true
        }
        success {
            echo 'Pipeline completed successfully.'
        }
        failure {
            echo 'Pipeline failed. See the failed stage and its log.'
        }
    }
}
