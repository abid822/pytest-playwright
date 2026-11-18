// Declarative pipeline for the same suite as .github/workflows/run-tests.yml.
// The image tag and the playwright pin below stay together: requirements.txt
// allows playwright>=1.49.0, and v1.65.2-noble already contains those browsers.

pipeline {
  agent none

  options {
    timeout(time: 150, unit: 'MINUTES')
    timestamps()
    disableConcurrentBuilds()
    buildDiscarder(logRotator(numToKeepStr: '10'))
  }

  parameters {
    choice(
      name: 'BROWSER',
      choices: ['all', 'chromium', 'firefox', 'webkit'],
      description: 'Browser to test. all runs chromium, firefox, and webkit in parallel.'
    )
  }

  stages {
    stage('Tests') {
      failFast false
      parallel {
        stage('chromium') {
          when {
            beforeAgent true
            expression { return (params.BROWSER ?: 'all') in ['all', 'chromium'] }
          }
          agent {
            docker {
              image 'mcr.microsoft.com/playwright/python:v1.65.2-noble'
              args '-u root:root --ipc=host --shm-size=1gb --init'
            }
          }
          environment {
            BASE_URL = 'https://www.amazon.com/'
            HEADLESS = 'true'
            SLOW_MO = '0'
            BROWSER = 'chromium'
            BROWSER_CHANNEL = ''
            DEFAULT_TIMEOUT_MS = '15000'
            VIEWPORT_WIDTH = '1280'
            VIEWPORT_HEIGHT = '720'
            PIP_ROOT_USER_ACTION = 'ignore'
          }
          steps {
            checkout scm
            runSuite()
          }
          post {
            always {
              publishBrowser('chromium')
            }
          }
        }

        stage('firefox') {
          when {
            beforeAgent true
            expression { return (params.BROWSER ?: 'all') in ['all', 'firefox'] }
          }
          agent {
            docker {
              image 'mcr.microsoft.com/playwright/python:v1.65.2-noble'
              args '-u root:root --ipc=host --shm-size=1gb --init'
            }
          }
          environment {
            BASE_URL = 'https://www.amazon.com/'
            HEADLESS = 'true'
            SLOW_MO = '0'
            BROWSER = 'firefox'
            BROWSER_CHANNEL = ''
            DEFAULT_TIMEOUT_MS = '15000'
            VIEWPORT_WIDTH = '1280'
            VIEWPORT_HEIGHT = '720'
            PIP_ROOT_USER_ACTION = 'ignore'
          }
          steps {
            checkout scm
            runSuite()
          }
          post {
            always {
              publishBrowser('firefox')
            }
          }
        }

        stage('webkit') {
          when {
            beforeAgent true
            expression { return (params.BROWSER ?: 'all') in ['all', 'webkit'] }
          }
          agent {
            docker {
              image 'mcr.microsoft.com/playwright/python:v1.65.2-noble'
              args '-u root:root --ipc=host --shm-size=1gb --init'
            }
          }
          environment {
            BASE_URL = 'https://www.amazon.com/'
            HEADLESS = 'true'
            SLOW_MO = '0'
            BROWSER = 'webkit'
            BROWSER_CHANNEL = ''
            DEFAULT_TIMEOUT_MS = '15000'
            VIEWPORT_WIDTH = '1280'
            VIEWPORT_HEIGHT = '720'
            PIP_ROOT_USER_ACTION = 'ignore'
          }
          steps {
            checkout scm
            runSuite()
          }
          post {
            always {
              publishBrowser('webkit')
            }
          }
        }
      }
    }
  }
}

def runSuite() {
  sh '''
    set -eu
    export BROWSER_CHANNEL=
    python -m pip install --disable-pip-version-check -r requirements.txt "playwright==1.65.2"
    mkdir -p reports test-results/traces
    junit_xml="reports/junit-${BROWSER}.xml"
    if [ -n "${CHANGE_ID:-}" ]; then
      pytest -n auto --reruns 1 --junitxml="${junit_xml}" tests/test_sell.py tests/test_login.py::test_invalid_login
    else
      pytest -n auto -m "not ci_skip" --reruns 1 --junitxml="${junit_xml}"
    fi
  '''
}

def publishBrowser(String browser) {
  junit allowEmptyResults: true, testResults: "reports/junit-${browser}.xml"
  archiveArtifacts artifacts: 'reports/**,test-results/traces/**', allowEmptyArchive: true
}
