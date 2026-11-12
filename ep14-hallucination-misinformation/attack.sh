#!/usr/bin/env bash
# The exact questions shown in the video, in order. Start one of the apps first (see README).
set -e
cd "$(dirname "$0")"
for Q in "Do you price match Amazon?" \
         "I bought headphones 45 days ago, order PK-4410, and I've opened them. Can I return them for a full refund?" \
         "Do you offer free installation for TVs?"; do
  echo "\$ python chat.py --reset \"$Q\""
  python3 chat.py --reset "$Q"
  echo
done
