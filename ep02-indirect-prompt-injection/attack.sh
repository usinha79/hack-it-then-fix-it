#!/usr/bin/env bash
# The exact requests shown in the video, in order. Start one of the apps first (see README).
set -e
cd "$(dirname "$0")"
URL=${URL:-http://localhost:5000}
echo "\$ python chat.py --reset \"Summarise this page: $URL/web/release-notes.html\""
python3 chat.py --reset "Summarise this page: $URL/web/release-notes.html"
echo
echo "\$ python chat.py --reset \"Summarise this page: $URL/web/ai-tools-roundup.html\""
python3 chat.py --reset "Summarise this page: $URL/web/ai-tools-roundup.html"
