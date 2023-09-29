#!/bin/sh -ex

ENVIRONMENT=$1

if [ -z "$ENVIRONMENT" ]
then
      echo "Usage: ./deploy.sh staging|production"
      exit 1
fi

pushd playbooks
source .venv/bin/activate
./ansible.sh -i environments/$ENVIRONMENT deploy.yaml
deactivate
popd
