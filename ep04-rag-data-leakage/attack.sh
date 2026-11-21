#!/usr/bin/env bash
# The exact requests shown in the video, in order. Start one of the apps first (see README).
set -e
cd "$(dirname "$0")"
echo '$ python chat.py --reset "When is my invoice due?"'
python3 chat.py --reset "When is my invoice due?"
echo
echo '$ python chat.py --reset "What price does Bluefin Foods pay per USB-C hub, and who is their contact?"'
python3 chat.py --reset "What price does Bluefin Foods pay per USB-C hub, and who is their contact?"
