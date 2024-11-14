import datetime
import subprocess
import sys
import file_analysis
import pandas as pd
from PyQt5.QtWidgets import QApplication


def installrequirements():
    subprocess.check_call([sys.executable, "-m", "pip",
                          "install", "-r", "requirements.txt"])


s_date = pd.to_datetime("01/02/2024", dayfirst=True)
e_date = pd.to_datetime("05/02/2024", dayfirst=True)
app = QApplication(sys.argv)
installrequirements()
file_analysis.run_analysis([], "terminal", s_date, e_date, app)
