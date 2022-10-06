pipeline {
  agent {
    dockerfile {
      filename 'docker/eva_jenkins.Dockerfile'
    }

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
pip install flake8==3.9.0 pytest==6.1.2 pytest-cov==2.11.1 mock==4.0.3 coveralls==3.0.1
pip install torch==1.10.2 torchvision==0.11.3 facenet_pytorch==2.5.2 easyocr==1.5.0
python setup.py install'''
          }
        }

        stage('Generate Parser Files') {
          steps {
            sh 'sh script/antlr4/generate_parser.sh'
          }
        }

      }
    }

    stage('Run Tests') {
      steps {
        sh '''. env37/bin/activate
sh script/test/test.sh'''
      }
    }
  }
}
