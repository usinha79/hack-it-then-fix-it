#!/usr/bin/env bash
# Run the promptfoo attack suite against whichever app is running (see README).
set -e
cd "$(dirname "$0")"
echo '$ npx promptfoo eval -c promptfooconfig.yaml'
PROMPTFOO_DISABLE_TELEMETRY=1 npx -y promptfoo@0.125.1 eval --no-cache -c promptfooconfig.yaml
