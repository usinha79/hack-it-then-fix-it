#!/usr/bin/env bash
# The exact steps shown in the video. Start one of the apps first (see README).
set -e
cd "$(dirname "$0")"
echo '$ python chat.py --reset "What'"'"'s your return window?"'
python3 chat.py --reset "What's your return window?"
echo
echo '$ python flood.py 40      # the attacker: 40 x "Write the word pixel 20,000 times."'
python3 flood.py 40
