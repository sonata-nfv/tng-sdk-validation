pipeline {
  agent any
  stages {
    stage('Container Build') {
      steps {
        echo 'Building..'
        sh 'docker build -f ./Dockerfile -t registry.sonata-nfv.eu:5000/tng-sdk-validation .'
      }
    }
    stage('Unit Tests') {
      steps {
        echo 'Unit Testing..'
        sh 'docker run -d --name redis_server -p 6379:6379 --network my_network redis'
        sh 'docker run --network my_network -e VAPI_REDIS_HOST='redis_server' -i --rm registry.sonata-nfv.eu:5000/tng-sdk-validation pytest -v'
      }
    }
    stage('Code Style check') {
      steps {
        echo 'Checking code style....'
        sh "pipeline/checkstyle/check.sh"
      }
    }
    stage('Containers Publication') {
      steps {
        echo 'Publication of containers in local registry....'
      }
    }
    stage('Deployment in Integration') {
      steps {
        echo 'Deploying in integration...'
      }
    }
    stage('Smoke Tests') {
      steps {
        echo 'Performing Smoke Tests....'
      }
    }
    stage('Publish Results') {
      steps {
        echo 'Publish Results...'
      }
    }
  }
}
