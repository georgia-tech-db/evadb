def buildNumber = BUILD_NUMBER as int; if (buildNumber > 1) milestone(buildNumber - 1); milestone(buildNumber) // JENKINS-43353 / JENKINS-58625

pipeline {
  agent {
      dockerfile {
        filename 'docker/jenkins.Dockerfile'
        args '--gpus all'
      }
    }
  
  options{
     buildDiscarder(logRotator(numToKeepStr: '8', daysToKeepStr: '20'))
  }
  
  
  stages {
  
    stage('Setup and Install Packages') {
      parallel {
        stage('Setup Virtual Environment') {
          
          steps {
            sh '''python3 -m venv env37
                  . env37/bin/activate
                  pip install --upgrade pip
                  pip install scikit-build
                  pip install cython
                  pip install -e ."[dev]"
              '''
          }
        }
      }
    }

    stage('CUDA GPU Check') {
    
      steps {
          sh '''. env37/bin/activate
                python3 -c "import torch; torch.cuda.current_device()"
             '''
      }
    }

    stage('Run Tests') {
    
      steps {
        sh '''. env37/bin/activate
              sh script/test/test.sh
           '''
       }
     }

    stage('Coverage Check') {
    
      steps {
        sh '''. env37/bin/activate
          coveralls'''
      }
    }
  }
}
