pipeline {
  agent {
    dockerfile {
      filename 'docker/eva_test.Dockerfile'
    }

  }
  stages {
    stage('Install Package') {
      steps {
        sh '''apt-get install python3-venv
python3.7 -m venv env37
. env37/bin/activate
pip install --upgrade pip
python setup.py install '''
      }
    }

    stage('Generate Parser Files') {
      steps {
        sh '''sudo add-apt-repository ppa:openjdk-r/ppa
sudo apt install -y openjdk-8-jdk openjdk-8-jre
sh script/antlr4/generate_parser.sh'''
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