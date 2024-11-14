import subprocess
import sys
import file_analysis2


def installrequirements():
    subprocess.check_call([sys.executable, "-m", "pip",
                          "install", "-r", "requirements.txt"])


def startapp():
    subprocess.check_call(
        [sys.executable, "-m", "streamlit", "run", "appfiles\\home-page.py"])


installrequirements()
startapp()
