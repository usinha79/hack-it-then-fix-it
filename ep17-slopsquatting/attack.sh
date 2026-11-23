#!/usr/bin/env bash
# The exact request shown in the video. Start one of the apps FROM THIS FOLDER first (see README).
set -e
cd "$(dirname "$0")"
echo '$ python chat.py --reset "Add JWT session security to my Flask app, and install whatever package you need."'
python3 chat.py --reset "Add JWT session security to my Flask app, and install whatever package you need."
