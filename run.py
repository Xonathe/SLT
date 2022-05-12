# -*- coding: utf-8 -*-
from PySide2.QtWidgets import QApplication
from browser import Browser, write_log
import sys
import os
import subprocess
import requests

cur_ver = "1.1.0.1"


def check_ver():
    try:
        responds = requests.get("https://site.ru/slt_ver.ini")
        last_ver = responds.text
    except requests.exceptions.ConnectionError:
        return False
    v1 = cur_ver.split(".")
    v2 = last_ver.split(".")
    res = int(v2[0] + v2[1] + v2[2] + v2[3]) - int(v1[0] + v1[1] + v1[2] + v1[3])
    if res > 0:
        return True
    else:
        return False


if __name__ == "__main__":
    v = check_ver()
    if v:
        cur_dir = os.getcwd()
        subprocess.Popen([f'{cur_dir}/update/updater.exe'], cwd=f'{cur_dir}/update')
        sys.exit(0)
    else:
        pass

    print(f"Старт программы", "journal")
    app = QApplication(sys.argv)

    window = Browser()
    f = os.path.exists("slt.ini")
    if not f:
        window.setup_add_ui()
        window.show()
    else:
        window.setup_main_ui()
        window.thread_start()
        window.show()
    sys.exit(app.exec_())
