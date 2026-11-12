#!/usr/bin/env bash
# The incident-response runs shown in the video (no server needed).
cd "$(dirname "$0")"
echo "== Who got the fake refund link? (fixed app's audit log) =="
python3 ir.py blast-radius https://pixelkart-refunds.example/claim
echo
echo "== Which memory entries came from the forum page? =="
python3 ir.py purge deals-forum.example
