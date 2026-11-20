pipeline {
    agent any

    parameters {
        string(name: 'REPO_URL', defaultValue: 'https://github.com/Ваш_Логин/cicd-demo-app.git', description: 'URL репозитория (Fork)')
        string(name: 'GIT_BRANCH', defaultValue: 'master', description: 'Ветка для сборки')
        booleanParam(name: 'RUN_TESTS', defaultValue: true, description: 'Запускать unit-тесты?')
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: "${params.GIT_BRANCH}", url: "${params.REPO_URL}"
                script {
                    def commitSha = sh(script: 'git rev-parse HEAD', returnStdout: true).trim()
                    echo "Branch: ${params.GIT_BRANCH}"
                    echo "Commit SHA: ${commitSha}"
                }
            }
        }

        stage('Validate') {
            steps {
                script {
                    def required = ['README.md', 'requirements.txt', 'src', 'tests']
                    for (item in required) {
                        if (!fileExists(item)) {
                            error "Validation failed: missing ${item}"
                        }
                    }
                    echo 'Validation passed.'
                }
            }
        }

        stage('Test') {
            when {
                expression { params.RUN_TESTS == true }
            }
            steps {
                sh 'python3 -m unittest discover -s tests -v'
            }
        }

        stage('Build') {
            steps {
                script {
                    def commitSha = sh(script: 'git rev-parse HEAD', returnStdout: true).trim()
                    sh "echo 'Build Number: ${env.BUILD_NUMBER}' > build-info.txt"
                    sh "echo 'Commit SHA: ${commitSha}' >> build-info.txt"
                    sh 'tar -czf app.tar.gz src tests requirements.txt README.md build-info.txt'
                }
            }
        }

        stage('Archive') {
            steps {
                archiveArtifacts artifacts: 'app.tar.gz', fingerprint: true
            }
        }
    }

    post {
        success {
            echo 'Pipeline completed successfully.'
        }
        failure {
            echo 'Pipeline failed. See logs above.'
        }
    }
}
