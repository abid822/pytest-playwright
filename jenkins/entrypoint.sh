#!/bin/bash
# The docker agent bind-mounts the workspace path Jenkins sees. A named volume
# lives at a different path on the Docker host, so bind that host path onto
# the same directory and use it as JENKINS_HOME.
set -euo pipefail

if [[ -S /var/run/docker.sock ]]; then
  cid="$(cat /etc/hostname)"
  host_home="$(docker inspect -f '{{ range .Mounts }}{{ if eq .Destination "/var/jenkins_home" }}{{ .Source }}{{ end }}{{ end }}' "${cid}" 2>/dev/null || true)"
  if [[ -n "${host_home}" && "${host_home}" != "/var/jenkins_home" ]]; then
    mkdir -p "${host_home}"
    if ! mountpoint -q "${host_home}"; then
      mount --bind /var/jenkins_home "${host_home}"
    fi
    export JENKINS_HOME="${host_home}"
    echo "Using ${JENKINS_HOME} so the docker agent can see the workspace."
  fi
fi

exec /usr/bin/tini -- /usr/local/bin/jenkins.sh "$@"
