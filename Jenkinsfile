pipeline {
  agent any
  environment {
    DOCKER_USER = 'fa23bai0045'
  }
  stages {
    stage('Fetch') {
      steps { checkout scm }
    }
    stage('Build and Run') {
      steps {
        sh 'docker build -t sentiment-test .'
        sh 'docker run -d --name sentiment-app -p 5000:5000 sentiment-test'
        sh 'sleep 15'
      }
    }
    stage('Unit Test') {
      steps {
        sh 'docker run --rm --network host sentiment-test pytest tests/test_api.py -v'
      }
    }
    stage('UI Test') {
      steps {
        sh 'docker run --rm --network host sentiment-test pytest tests/test_ui.py -v'
      }
    }
    stage('Build and Push') {
      steps {
        withCredentials([usernamePassword(credentialsId:'dockerhub', usernameVariable:'DHUSER', passwordVariable:'DHPASS')]) {
          sh 'echo "$DHPASS" | docker login -u "$DHUSER" --password-stdin'
          sh 'docker build -t $DOCKER_USER/sentiment-api:unstable .'
          sh 'git stash; git checkout stable-fallback; docker build -t $DOCKER_USER/sentiment-api:stable .; git checkout main; git stash pop || true'
          sh 'docker push $DOCKER_USER/sentiment-api:unstable'
          sh 'docker push $DOCKER_USER/sentiment-api:stable'
        }
      }
    }
    stage('Deploy to Minikube') {
      steps {
        sh '''
            # Check if minikube is running, start if not
            if ! minikube status | grep -q "Running"; then
                minikube start --driver=docker
            fi

            # Always apply kubectl regardless
            eval $(minikube docker-env)
            kubectl apply -f k8s/pvc.yaml
            kubectl apply -f k8s/blue-deployment.yaml
            kubectl apply -f k8s/green-deployment.yaml
            kubectl apply -f k8s/service.yaml
            
        '''
        sh 'docker rm -f sentiment-app || true'
      }
    }
  }
}
