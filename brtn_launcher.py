import sys
import subprocess
import os

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--settings":
        subprocess.Popen([sys.executable, "brtn_settings_ui.py"])
    else:
        # Start the transcriber
        # In a real app we might want to start it in a detached way
        subprocess.Popen([sys.executable, "brtn_transcriber.py"])

if __name__ == "__main__":
    main()
