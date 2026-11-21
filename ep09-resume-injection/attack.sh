#!/usr/bin/env bash
# The exact request shown in the video. Start one of the apps first (see README).
set -e
cd "$(dirname "$0")"
echo '$ python chat.py --reset "Screen the applicants for the Backend Engineer role."'
python3 chat.py --reset "Screen the applicants for the Backend Engineer role."
