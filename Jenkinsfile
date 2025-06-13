pipeline {
    agent any

    environment {
        APP_NAME = "todo-app"
        IMAGE_NAME = "todo-app-image"
        CONTAINER_NAME = "todo-test-container"
        TEST_URL = "http://localhost:5000"
    }

    stages {
        stage('Build Docker Image') {
            steps {
                echo '📦 Building Docker image'
                sh '''
                    docker build -t ${IMAGE_NAME}:latest .
                '''
            }
        }

        stage('Run Unit Tests') {
            steps {
                echo '🧪 Running pytest inside container'
                sh '''
                    docker run --rm ${IMAGE_NAME}:latest pytest tests/
                '''
            }
        }

        stage('SAST Scan (Bandit)') {
            steps {
                echo '🔒 Running Bandit inside container'
                sh '''
                    docker run --rm ${IMAGE_NAME}:latest bandit -r . -ll -iii -f json -o bandit_report.json || true

                    CRITICALS=$(docker run --rm ${IMAGE_NAME}:latest bash -c "jq '.results[] | select(.issue_severity==\\"HIGH\\")' bandit_report.json | wc -l")

                    if [ "$CRITICALS" -gt 0 ]; then
                        echo "❌ Found $CRITICALS HIGH severity vulnerabilities!"
                        exit 1
                    fi
                '''
            }
        }

        stage('Deploy to Test Environment') {
            steps {
                echo '🚀 Running Flask app in Docker container'
                sh '''
                    docker rm -f ${CONTAINER_NAME} || true
                    docker run -d --name ${CONTAINER_NAME} -p 5000:5000 ${IMAGE_NAME}:latest
                    sleep 10
                '''
            }
        }

        stage('DAST Scan (ZAP)') {
            steps {
                echo '🛡️ Running ZAP scan'
                sh '''
                    docker rm -f zap || true
                    docker run --name zap -u root -v $(pwd):/zap/wrk/:rw -d -p 8091:8090 ghcr.io/zaproxy/zaproxy:stable zap.sh -daemon -port 8090 -host 0.0.0.0
                    sleep 15
                    # Tambahkan perintah ZAP scan aktif sesuai kebutuhan
                '''
            }
        }

        stage('Deploy to Staging') {
            steps {
                echo '📦 (Optional) Push Docker image to registry'
                sh '''
                    docker tag ${IMAGE_NAME}:latest your-dockerhub-user/${APP_NAME}:latest
                    # docker push your-dockerhub-user/${APP_NAME}:latest
                '''
            }
        }

        stage('Log Review') {
            steps {
                echo '📄 Menampilkan 10 baris terakhir dari container log'
                sh "docker logs ${CONTAINER_NAME} | tail -n 10"
            }
        }
    }

    post {
        always {
            echo '🧹 Cleanup: stop containers'
            sh '''
                docker rm -f ${CONTAINER_NAME} || true
                docker rm -f zap || true
            '''
        }

        failure {
            echo '❌ Build failed. Please check the logs above.'
        }
    }
}
