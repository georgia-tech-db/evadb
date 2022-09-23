pipeline {
  agent {
    dockerfile {
      filename 'docker/eva_jenkins.Dockerfile'
    }

  }
  stages {
    stage('Setup and Build') {
      parallel {
        stage('Setup Virtual Environment') {
          steps {
            sh '''python3 -m venv eva_dev_env
. eva_dev_env/bin/activate
pip install --upgrade pip
pip install ".[dev]"
pip install scikit-build
pip install cython
pip install flake8==3.9.0 pytest==6.1.2 pytest-cov==2.11.1 mock==4.0.3 coveralls==3.0.1
python setup.py install '''
          }
        }

        stage('Generate Parser, Test and Coverage') {
          steps {
            sh '''. eva_dev_env/bin/activate
sh script/antlr4/generate_parser.sh
sh script/test/test.sh
coveralls'''
          }
        }
      }
    }
  }
}