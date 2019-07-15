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
    stage('Deployment in Integration') {
      parallel {
        stage('Deployment in Integration') {
          steps {
            echo 'Deploying in integration...'
          }
        }
        stage('Deploying') {
          steps {
            sh 'rm -rf tng-devops || true'
            sh 'git clone https://github.com/sonata-nfv/tng-devops.git'
            dir(path: 'tng-devops') {
              sh 'ansible-playbook roles/sp.yml -i environments -e "target=pre-int-sp component=infrastructure-abstraction"'
            }
          }
        }
      }
    }
    stage('Promoting containers to integration env') {
      when {
         branch 'master'
      }
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
	   stage('Promoting to integration') {
		  when{
			  branch 'master'
		  }      
		  steps {
        sh 'docker tag registry.sonata-nfv.eu:5000/tng-sp-ia-emu:latest registry.sonata-nfv.eu:5000/tng-sp-ia-emu:int'
        sh 'docker push registry.sonata-nfv.eu:5000/tng-sp-ia-emu:int'
        sh 'rm -rf tng-devops || true'
        sh 'git clone https://github.com/sonata-nfv/tng-devops.git'
        dir(path: 'tng-devops') {
          sh 'ansible-playbook roles/sp.yml -i environments -e "target=int-sp component=infrastructure-abstraction"'
			  }
		  }
		}
		
      }        
    }
  }
  post {
    always {
      echo 'TODO'
    }
  }
}
