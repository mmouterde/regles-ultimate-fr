#!/usr/bin/env bash

set -eux

JSON_DIR=../src/_data/facts

# pick a random fact
one_fact=$(ls ${JSON_DIR}/fact*.json | sort -R | head -n1)

# post it
curl -i -X POST -H 'Content-Type: application/json' -d @${one_fact} https://framateam.org/hooks/$MM_WEBHOOK_TOKEN
