#!/usr/bin/env bash
# The detection runs shown in the video (no server needed).
cd "$(dirname "$0")"
python3 detect.py logs/access.log
echo
python3 detect.py logs/security.jsonl
