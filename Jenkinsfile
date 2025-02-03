pipeline {
    agent any

    parameters {
        string(name: 'DOCKER_TAG', defaultValue: 'latest', description: 'Docker Image Tag')
    }

    environment {
        DOCKER_IMAGE = "harendrabarot/cloud-project"
        SONARQUBE_SCANNER_HOME = tool 'sonar'
        TAG = "${params.DOCKER_TAG}" 
    }

    stages {

        stages {
        stage('Checkout') {
            steps {
                git branch: 'main', credentialsId: 'git-cred', url: 'https://github.com/Sudoharry/Cloud-Projects.git'
            }
        }        

        stage("Workspace cleanup") {
            steps {
                script {
                    cleanWs()
                }
            }
        }

        stage('Compile Python Code') {
            steps {
                script {
                    sh 'python3 -m compileall .'
                }
            }
        }

        stage('Setup & Test') {
            steps {
                script {
                    // Create virtual environment
                    sh 'python3 -m venv venv'
                    
                    // Install dependencies
                    sh 'venv/bin/pip install --upgrade pip'
                    sh 'venv/bin/pip install -r requirements.txt'
                    
                    // Run tests
                    sh 'venv/bin/python -m pytest tests/ --junitxml=test-results.xml'
                }
            }
        }

        stage('Trivy FS Scan') {
            steps {
                script {
                    // Debugging: Check if Trivy is available in the environment
                    sh 'which trivy || echo "Trivy is not installed"'
                    
                    // Debugging: Run Trivy with verbose output
                    sh 'trivy fs --format table -o fs.html . || echo "Trivy FS scan failed"'
                }
            }
        }

        stage('SonarQube Analysis') {
            steps {
                withSonarQubeEnv('sonar') {
                    sh "$SONARQUBE_SCANNER_HOME/bin/sonar-scanner -Dsonar.projectKey=pythonapp -Dsonar.projectName=cloudproject"
                }
            }
        }

        stage('Quality Gate Check') {
            steps {
                timeout(time: 1, unit: 'HOURS') {
                    waitForQualityGate abortPipeline: false
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    withDockerRegistry(credentialsId: 'docker-cred') {
                        sh "docker build -t ${DOCKER_IMAGE}:${TAG} ."
                    }
                }
            }
        }
        
        stage('Trivy Image Scan') {
            steps {
                script {
                    sh "trivy image --format table -o image.html ${DOCKER_IMAGE}:${TAG}"
                }
            }
        }
        
        stage('Deploy to Staging') {
            when {
                branch 'main'
            }
            steps {
                script {
                    sh 'docker run -d --name cloud-project -p 5000:5000 ${DOCKER_IMAGE}:${TAG}'
                }
            }
        }
    }

    post {
        always {
            junit '**/test-results.xml'
            cleanWs()
        }
        success {
            emailext (
                subject: "Build ${env.BUILD_NUMBER} Succeeded!",
                body: "Great news! The build ${env.BUILD_NUMBER} has succeeded. 🎉\n\nCheck out the results here: ${BUILD_URL}",
                to: 'harendrabarot19@gmail.com',
                from: 'harendrabarot19@gmail.com'
            )
        }
        failure {
            emailext (
                subject: "Build ${env.BUILD_NUMBER} Failed!",
                body: "Oops! The build ${env.BUILD_NUMBER} has failed. ❌\n\nCheck the logs here: ${BUILD_URL}",
                to: 'harendrabarot19@gmail.com',
                from: 'harendrabarot19@gmail.com'
            )
        }
    }
}
