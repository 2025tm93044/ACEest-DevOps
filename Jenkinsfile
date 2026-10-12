pipeline {
    agent any

    environment {
        IMAGE_NAME = 'aceest-fitness:jenkins'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Set up Python and dependencies') {
            steps {
                sh '''
                    python3 -m venv .venv
                    . .venv/bin/activate
                    python -m pip install --upgrade pip
                    pip install -r requirements-dev.txt
                '''
            }
        }

        stage('Syntax and lint') {
            steps {
                sh '''
                    . .venv/bin/activate
                    python -m compileall -q app.py tests
                    ruff check --select F app.py tests
                '''
            }
        }

        stage('Pytest') {
            steps {
                sh '''
                    . .venv/bin/activate
                    pytest -q
                '''
            }
        }

        stage('Docker build') {
            steps {
                sh 'docker build -t $IMAGE_NAME .'
            }
        }
    }

    post {
        always {
            cleanWs()
        }
    }
}
