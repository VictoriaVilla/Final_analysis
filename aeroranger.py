import subprocess
import sys
import file_analysis2
from PyQt5.QtWidgets import QApplication


def installrequirements():
    subprocess.check_call([sys.executable, "-m", "pip",
                          "install", "-r", "requirements.txt"])

app = QApplication(sys.argv)
installrequirements()
file_analysis2.run_analysis("", "terminal", app)
