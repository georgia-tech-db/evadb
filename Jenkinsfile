pipeline {
  agent {
    dockerfile {
      filename 'docker/eva_test_ubuntu.Dockerfile'
    }

  }
  stages {
    stage('Install Package') {
      steps {
        sh '''python3 -m venv env37
. env37/bin/activate
pip3 install --upgrade pip
pip3 install numpy==1.20.1
python3 setup.py install '''
      }
    }

    stage('Generate Parser Files') {
      steps {
        sh 'sh script/antlr4/generate_parser.sh'
      }
    }

    stage('Install Test Dependencies') {
      steps {
        sh '''. env37/bin/activate
pip install flake8==3.9.0 pytest==6.1.2 pytest-cov==2.11.1 mock==4.0.3 coveralls==3.0.1'''
      }
    }

    stage('Test') {
      steps {
        sh '''. env37/bin/activate
sh script/test/test.sh
coveralls'''
      }
    }

  }
}