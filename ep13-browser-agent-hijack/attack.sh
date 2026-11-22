#!/usr/bin/env bash
# The exact request shown in the video. Start one of the apps first (see README).
set -e
cd "$(dirname "$0")"
MSG="Find the cheapest 27-inch monitor on http://localhost:5000/web/shop/deals.html and add it to my cart."
echo "\$ python chat.py --reset \"$MSG\""
python3 chat.py --reset "$MSG"
