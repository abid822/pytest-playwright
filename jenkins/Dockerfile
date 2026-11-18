FROM jenkins/jenkins:lts

USER root

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates curl gnupg git \
    && install -m 0755 -d /etc/apt/keyrings \
    && curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc \
    && chmod a+r /etc/apt/keyrings/docker.asc \
    && . /etc/os-release \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/debian ${VERSION_CODENAME} stable" > /etc/apt/sources.list.d/docker.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends docker-ce-cli \
    && rm -rf /var/lib/apt/lists/*

COPY plugins.txt /usr/share/jenkins/ref/plugins.txt
RUN jenkins-plugin-cli --plugin-file /usr/share/jenkins/ref/plugins.txt

COPY jenkins.yaml /usr/share/jenkins/casc/jenkins.yaml
COPY job-dsl-security.xml /usr/share/jenkins/ref/javaposse.jobdsl.plugin.GlobalJobDslSecurityConfiguration.xml
COPY entrypoint.sh /usr/local/bin/jenkins-entrypoint.sh
RUN chmod 755 /usr/local/bin/jenkins-entrypoint.sh

ENV CASC_JENKINS_CONFIG=/usr/share/jenkins/casc/jenkins.yaml \
    JAVA_OPTS="-Djenkins.install.runSetupWizard=false" \
    JENKINS_ADMIN_ID=admin \
    JENKINS_ADMIN_PASSWORD=admin

USER root
ENTRYPOINT ["/usr/local/bin/jenkins-entrypoint.sh"]
