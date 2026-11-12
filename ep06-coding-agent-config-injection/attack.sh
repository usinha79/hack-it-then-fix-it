#!/usr/bin/env bash
# The exact request shown in the video. Start one of the apps first (see README).
set -e
cd "$(dirname "$0")"
echo '$ python chat.py --reset "The tests are failing. Please fix the bug in calc.py."'
python3 chat.py --reset "The tests are failing. Please fix the bug in calc.py."
