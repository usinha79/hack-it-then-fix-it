#!/usr/bin/env bash
# What the video shows: the check on both designs. (The chat version: python vulnerable/app.py or fixed/app.py.)
cd "$(dirname "$0")"
echo '$ python threatmodel.py apps/pixelkart-assist.yaml'
python3 threatmodel.py apps/pixelkart-assist.yaml; echo "exit code: $?"
echo
echo '$ python threatmodel.py apps/pixelkart-assist.fixed.yaml'
python3 threatmodel.py apps/pixelkart-assist.fixed.yaml; echo "exit code: $?"
