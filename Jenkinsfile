pipeline {
    agent any

    environment {
        DOCKER_USERNAME = "fa23bai0045"
        DOCKER_IMAGE_UNSTABLE = "${DOCKER_USERNAME}/sentiment-api:unstable"
        DOCKER_IMAGE_STABLE = "${DOCKER_USERNAME}/sentiment-api:stable"
        DOCKER_CREDENTIALS = credentials('dockerhub')
        KUBECONFIG = "/home/ubuntu/.kube/config"
    }

    stages {
        stage('Fetch') {
            steps {
                script {
                    checkout scm
                    echo "Repository fetched successfully"
                }
            }
        }

        stage('Build and Run') {
            steps {
                script {
                    echo "Building Docker image for unstable app..."
                    sh '''
                        docker build -t ${DOCKER_IMAGE_UNSTABLE} .
                        echo "Docker image built: ${DOCKER_IMAGE_UNSTABLE}"
                    '''
                    echo "Running containerized unstable app..."
                    sh '''
                        docker run -d --name sentiment-unstable-test \
                            -p 5000:5000 \
                            -v /app/logs:/app/logs \
                            ${DOCKER_IMAGE_UNSTABLE}
                        sleep 30
                        curl -s http://localhost:5000/health || echo "Health check pending..."
                        
                    '''
                }
            }
        }

        stage('Unit Test') {
            steps {
                script {
                    echo "Running PyTest unit tests..."
                    sh '''
                        docker run --rm \
                            -v ${WORKSPACE}:/app \
                            ${DOCKER_IMAGE_UNSTABLE} \
                            pytest tests/test_api.py -v --tb=short
                    '''
                }
            }
        }

        stage('UI Test') {
            steps {
                script {
                    echo "Running Selenium UI tests..."
                    sh '''
                        docker run --rm \
                            -v ${WORKSPACE}:/app \
                            ${DOCKER_IMAGE_UNSTABLE} \
                            pytest tests/test_ui.py -v --tb=short
                    '''
                }
            }
        }

        stage('Build and Push') {
            steps {
                script {
                    echo "Building and pushing unstable image..."
                    sh '''
                        docker login -u ${DOCKER_USERNAME} -p ${DOCKER_CREDENTIALS_PSW}
                        docker push ${DOCKER_IMAGE_UNSTABLE}
                        docker logout
                    '''
                    echo "Checking out stable-fallback branch for stable image..."
                    sh '''
                        git checkout stable-fallback || git checkout -b stable-fallback origin/stable-fallback
                        docker build -t ${DOCKER_IMAGE_STABLE} .
                        docker login -u ${DOCKER_USERNAME} -p ${DOCKER_CREDENTIALS_PSW}
                        docker push ${DOCKER_IMAGE_STABLE}
                        docker logout
                        git checkout main
                    '''
                }
            }
        }

        stage('Deploy to Minikube') {
            steps {
                script {
                    echo "Deploying to Minikube..."
                    sh '''
                        # Check if minikube is running, start if not
                        if ! minikube status | grep -q "Running"; then
                            minikube start --driver=docker
                        fi
                        kubectl apply -f k8s/pvc.yaml
                        kubectl apply -f k8s/blue-deployment.yaml
                        kubectl apply -f k8s/green-deployment.yaml
                        kubectl apply -f k8s/service.yaml
                        echo "Waiting for deployments to be ready..."
                        kubectl rollout status deployment/sentiment-blue-deployment -n default --timeout=2m
                        kubectl rollout status deployment/sentiment-green-deployment -n default --timeout=
                        docker rm -f sentiment-app || true
                        echo "Deployments ready!"
                    '''
                }
            }
        }
    }

}
