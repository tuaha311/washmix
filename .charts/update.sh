#!/usr/bin/env bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
CIRCLE_SHA1="${CIRCLE_SHA1:-latest}"
helm upgrade washmix-back $DIR/washmix-back \
     --set image.tag=${CIRCLE_SHA1} \
     --atomic \
     --timeout=120s \
     --install && \

echo "Done"
