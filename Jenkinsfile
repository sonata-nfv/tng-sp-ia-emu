pipeline {
  agent any
  stages {
    stage('Container Build') {
      parallel {
        stage('Container Build') {
          steps {
            echo 'Building...'
          }
        }
        stage('Building tng-sp-ia-emu') {
          steps {
            sh 'docker build -t registry.sonata-nfv.eu:5000/tng-sp-ia-emu .'
          }
        }
      }
    }
    stage('Unit Test') {
      parallel {
        stage('Unit Tests') {
          steps {
            echo 'Performing Unit Tests'
          }
        }
        stage('Running Unit Tests') {
          steps {
            echo 'TODO'
          }
        }
      }
    }
    stage('Containers Publication') {
      parallel {
        stage('Containers Publication') {
          steps {
            echo 'Publication of containers in local registry....'
          }
        }
        stage('Publishing tng-sp-ia-emu') {
          steps {
            sh 'docker push registry.sonata-nfv.eu:5000/tng-sp-ia-emu'
          }
        }
      }
    }
    stage('Promoting containers to integration env') {
      parallel {
        stage('Publishing containers to int') {
          steps {
            echo 'Promoting containers to integration'
          }
        }
        stage('tng-sp-ia-emu') {
          steps {
            sh 'docker tag registry.sonata-nfv.eu:5000/tng-sp-ia-emu:latest registry.sonata-nfv.eu:5000/tng-sp-ia-emu:int'
            sh 'docker push registry.sonata-nfv.eu:5000/tng-sp-ia-emu:int'
          }
        }
	   	}
    }        
    stage('Promoting release v5.1') {
      when {
        branch 'v5.1'
      }
      steps {
        sh 'docker tag registry.sonata-nfv.eu:5000/tng-sp-ia-emu:latest registry.sonata-nfv.eu:5000/tng-sp-ia-emu:v5.1'
        sh 'docker push registry.sonata-nfv.eu:5000/tng-sp-ia-emu:v5.1'
      }
    }
  }
  post {
    always {
      echo 'TODO'
    }
  }
}
