#!/bin/bash
# BRTN Transcriber Runner
BASEDIR=$(dirname "$0")
cd "$BASEDIR"

case "$1" in
    "settings")
        echo "Opening BRTN Settings..."
        ./.venv/bin/python brtn_settings_ui.py
        ;;
    "stop")
        echo "Stopping BRTN Transcriber..."
        pkill -f brtn_transcriber.py
        ;;
    "run")
        echo "Starting BRTN Transcriber in background..."
        nohup ./.venv/bin/python brtn_transcriber.py > /dev/null 2>&1 &
        ;;
    *)
        echo "Usage: $0 {run|settings|stop}"
        ;;
esac
