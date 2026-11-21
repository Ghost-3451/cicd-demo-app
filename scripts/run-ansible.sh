#!/usr/bin/env bash
set -euo pipefail
export DOCKER_HOST=unix:///var/run/docker.sock
export ANSIBLE_COLLECTIONS_PATH=/opt/jenkins-ansible/collections
exec /opt/jenkins-ansible/bin/ansible-playbook -i localhost, "$@"
