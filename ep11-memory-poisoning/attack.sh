#!/usr/bin/env bash
# The exact requests shown in the video, in order. Start one of the apps first (see README).
set -e
cd "$(dirname "$0")"
echo '$ python chat.py --wipe "Summarise this page: http://localhost:5000/web/festive-sale-tips.html"'
python3 chat.py --wipe "Summarise this page: http://localhost:5000/web/festive-sale-tips.html"
echo
echo '# ...a new chat, days later. The conversation is gone. The memory is not.'
echo '$ python chat.py --new "How do I get a refund for my order PK-2077?"'
python3 chat.py --new "How do I get a refund for my order PK-2077?"
