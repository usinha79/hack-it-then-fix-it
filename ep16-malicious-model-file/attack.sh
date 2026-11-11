#!/usr/bin/env bash
# The exact requests shown in the video. Start one of the apps FROM THIS FOLDER first (see README).
set -e
cd "$(dirname "$0")"
echo "\$ python chat.py --reset \"Load sentiment-base and score this review: 'Delivery was late and the box was damaged.'\""
python3 chat.py --reset "Load sentiment-base and score this review: 'Delivery was late and the box was damaged.'"
echo
echo "\$ python chat.py --reset \"Load the community model sentiment-pro and score this review: 'Delivery was quick and the box was intact.'\""
python3 chat.py --reset "Load the community model sentiment-pro and score this review: 'Delivery was quick and the box was intact.'"
