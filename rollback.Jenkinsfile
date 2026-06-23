pipeline {
    agent any

    stages {
        stage('Switch Traffic to Stable (Green)') {
            steps {
                script {
                    echo "Patching service to route to stable (green) deployment..."
                    sh '''
                        kubectl patch service sentiment-api-service -p '{"spec":{"selector":{"slot":"green"}}}'
                        echo "Service patched successfully - traffic now routing to green (stable) deployment"
                        
                        # Verify the patch
                        kubectl get service sentiment-api-service -o jsonpath='{.spec.selector.slot}'
                    '''
                }
            }
        }
    }

    post {
        success {
            echo "Rollback to stable completed successfully"
        }
        failure {
            echo "Rollback failed - check logs"
        }
    }
}
