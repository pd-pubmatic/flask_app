pipeline {
    agent any
    
    environment {
        DOCKER_REGISTRY = 'your-registry.com'
        DOCKER_CREDS = credentials('docker-credentials')
        KUBE_CONFIG = credentials('kubernetes-config')
        AWS_CREDS = credentials('aws-credentials')
        OPENAI_CREDS = credentials('openai-credentials')
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Test') {
            steps {
                sh '''
                    python -m pip install --upgrade pip
                    pip install -r requirements.txt
                    python -m pytest tests/
                '''
            }
        }
        
        stage('Build Docker Image') {
            steps {
                sh '''
                    docker build -t ${DOCKER_REGISTRY}/adwise-tagging:${BUILD_TAG} .
                    docker login -u ${DOCKER_CREDS_USR} -p ${DOCKER_CREDS_PSW} ${DOCKER_REGISTRY}
                    docker push ${DOCKER_REGISTRY}/adwise-tagging:${BUILD_TAG}
                '''
            }
        }
        
        stage('Deploy to Kubernetes') {
            steps {
                sh '''
                    # Create base64 encoded secrets
                    export FLASK_SECRET_KEY_BASE64=$(echo -n "$FLASK_SECRET_KEY" | base64)
                    export AWS_ACCESS_KEY_ID_BASE64=$(echo -n "$AWS_CREDS_USR" | base64)
                    export AWS_SECRET_ACCESS_KEY_BASE64=$(echo -n "$AWS_CREDS_PSW" | base64)
                    export OPENAI_API_KEY_BASE64=$(echo -n "$OPENAI_CREDS_PSW" | base64)
                    
                    # Apply Kubernetes configurations
                    envsubst < k8s/secrets.yaml.template > k8s/secrets.yaml
                    kubectl --kubeconfig=$KUBE_CONFIG apply -f k8s/secrets.yaml
                    
                    envsubst < k8s/deployment.yaml | kubectl --kubeconfig=$KUBE_CONFIG apply -f -
                    kubectl --kubeconfig=$KUBE_CONFIG apply -f k8s/service.yaml
                '''
            }
        }
    }
    
    post {
        always {
            cleanWs()
        }
    }
} 