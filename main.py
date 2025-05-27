"""Точка входа"""
import json
import sys
from PyQt5.QtWidgets import QApplication
from UI.main_ui import Root

if __name__ == "__main__":
    with open("info.json", "r", encoding="utf-8") as info:
        data = json.load(info)
    nickname = data["nickname"]
    token = data["token"]
    volume = data["volume"]

    App = QApplication(sys.argv)
    root = Root(nickname, token, volume)
    sys.exit(App.exec())