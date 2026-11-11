#!/usr/bin/env bash
# The scans shown in the video (no server needed). Needs: pip install semgrep
cd "$(dirname "$0")"
echo "== PR 42, as first submitted =="
semgrep --metrics=off --disable-version-check --config rules/ pr42/before
echo
echo "== PR 42, after the fixes =="
semgrep --metrics=off --disable-version-check --config rules/ pr42/after
