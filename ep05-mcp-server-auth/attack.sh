#!/usr/bin/env bash
# The exact requests shown in the video, in order. Start one of the apps first (see README).
set -e
cd "$(dirname "$0")"
echo '$ python chat.py --reset "Where is my order PK-1042?"'
python3 chat.py --reset "Where is my order PK-1042?"
echo
echo '$ python attack.py          # the attacker, straight to the MCP server, no token'
python3 attack.py
if [ -n "$ASSISTANT_TOKEN" ]; then
  echo
  echo '$ python attack.py $ASSISTANT_TOKEN   # what if the assistant token leaked?'
  python3 attack.py "$ASSISTANT_TOKEN"
fi
