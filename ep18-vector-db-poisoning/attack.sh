#!/usr/bin/env bash
# The exact steps shown in the video. Start one of the apps first (see README).
set -e
cd "$(dirname "$0")"
echo '$ python chat.py --reset "How do I reset my password?"'
python3 chat.py --reset "How do I reset my password?"
echo
echo '# The attacker posts a "community answer". It is embedded automatically.'
echo '$ python post_attack.py'
python3 post_attack.py
echo
echo '$ python chat.py "How do I reset my password?"'
python3 chat.py "How do I reset my password?"
