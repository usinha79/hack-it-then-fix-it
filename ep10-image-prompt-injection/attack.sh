#!/usr/bin/env bash
# The exact requests shown in the video, in order. Start one of the apps first (see README).
set -e
cd "$(dirname "$0")"
echo '$ python chat.py --reset "Review Anita'"'"'s expense claim."'
python3 chat.py --reset "Review Anita's expense claim."
echo
echo '$ python chat.py --reset "Review Ravi'"'"'s expense claim."'
python3 chat.py --reset "Review Ravi's expense claim."
