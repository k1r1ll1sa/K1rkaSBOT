"""Модуль для интерфейса программы"""
import os
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import requests
import threading
import sys
import bot
import json

class Root(QMainWindow):
    def __init__(self, nickname, token):
        super().__init__()
        self.nickname = nickname
        self.token = token

        # Параметры окна
        self.setWindowTitle("K1rkasBot1k")
        self.setFixedSize(700, 420)
        self.initUi()

    def initUi(self):
        self.spacer = QWidget(self)
        self.spacer.setFixedHeight(10)
        self.spacer_0 = QWidget(self)
        self.spacer_0.setFixedHeight(5)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # Поле для ввода никнейма
        self.nickname_label = QLabel("Введите никнейм:", parent=self)
        self.nickname_label.setFont(QFont("Cascadia Code", 12, QFont.Bold))
        self.nickname_label.resize(130, 20)
        self.nickname_label.setAlignment(Qt.AlignCenter)

        self.nickname_lineedit = QLineEdit(parent=self)
        if nickname != "":
            self.nickname_lineedit.setText(nickname)
        self.nickname_lineedit.setFont(QFont("Cascadia Code", 10, QFont.Bold))
        self.nickname_lineedit.setMinimumWidth(200)
        self.nickname_lineedit.setAlignment(Qt.AlignCenter)

        # Поле для ввода токена
        self.token_label = QLabel("Access token:", parent=self)
        self.token_label.setFont(QFont("Cascadia Code", 12, QFont.Bold))
        self.token_label.setAlignment(Qt.AlignCenter)

        self.token_lineedit = QLineEdit(parent=self)
        if token != "":
            self.token_lineedit.setText(token)
        self.token_lineedit.setFont(QFont("Cascadia Code", 10, QFont.Bold))
        self.token_lineedit.setAlignment(Qt.AlignCenter)
        self.token_lineedit.setMinimumWidth(200)

        # Кнопка "Запустить"
        self.start_button = QPushButton("Запустить", parent=self)
        self.start_button.clicked.connect(self.run_button)
        self.start_button.setFont(QFont("Cascadia Code", 12, QFont.Bold))
        self.start_button.setMinimumWidth(200)
        self.start_button.setStyleSheet("background-color : #7bd17b")

        # Текст "Перейдите по ссылке:"
        self.tokengenerator_label = QLabel("Перед запуском перейдите по ссылке:", parent=self)
        self.tokengenerator_label.setFont(QFont("Cascadia Code", 12, QFont.Bold))
        self.tokengenerator_label.setAlignment(Qt.AlignCenter)

        # Ссылка на токен генератор
        self.tokengenerator_lineedit = QLineEdit("https://twitchtokengenerator.com", parent=self)
        self.tokengenerator_lineedit.setStyleSheet("font: bold italic")
        self.tokengenerator_lineedit.setFont(QFont("Times New Roman", 11))
        self.tokengenerator_lineedit.setMinimumWidth(320)
        self.tokengenerator_lineedit.setAlignment(Qt.AlignCenter)
        self.tokengenerator_lineedit.setReadOnly(True)

        # Инструкция по запуску
        self.manual_label = QLabel('Авторизуйтесь, используя <Bot chat token>.'
                                   '\n Скопируйте содержимое поля access token и вставьте в соответствующее поле в программе.',
                                   parent=self)
        self.manual_label.setFont(QFont("Cascadia Code", 12, QFont.Bold))
        self.manual_label.setAlignment(Qt.AlignCenter)
        self.manual_label.setWordWrap(True)

        # "Нажмите кнопку запустить"
        self.start_label = QLabel('Нажмите кнопку "Запустить"', parent=self)
        self.start_label.setFont(QFont("Cascadia Code", 12, QFont.Bold))
        self.start_label.setAlignment(Qt.AlignCenter)
        self.start_label.setWordWrap(True)

        # Консоль
        self.console_textedit = QTextEdit("Hello! It`s a console!", parent=self)
        self.console_textedit.setFont(QFont("Times New Roman", 11))
        self.console_textedit.setAlignment(Qt.AlignLeft)
        self.console_textedit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Поле для ввода команд
        self.console_lineedit = QLineEdit(parent=self)
        self.console_lineedit.setFont(QFont("Times New Roman", 11))
        self.console_lineedit.setAlignment(Qt.AlignLeft)

        # Расположение элементов по сетке
        # 0 столбец
        layout = QGridLayout(central_widget)
        layout.setColumnMinimumWidth(1, 250)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.addWidget(self.nickname_label, 0, 0)
        layout.addWidget(self.nickname_lineedit, 1, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.token_label, 2, 0)
        layout.addWidget(self.token_lineedit, 3, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.spacer, 4, 0)
        layout.addWidget(self.start_button, 5, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.spacer_0, 6, 0)
        layout.addWidget(self.tokengenerator_label, 7, 0)
        layout.addWidget(self.tokengenerator_lineedit, 8, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.manual_label, 9, 0)
        layout.addWidget(self.start_label, 10, 0)

        # 1 столбец
        layout.addWidget(self.console_textedit, 0, 1, 10, 1)
        layout.addWidget(self.console_lineedit, 10, 1)

        self.setLayout(layout)
        self.show()

    # гетеры
    def get_nickname(self):
        nickname = self.nickname_lineedit.text()
        return nickname

    def get_token(self):
        token = self.token_lineedit.text()
        return token

    # действие для кнопки (запуск бота)
    def run_button(self):
        nickname_text = self.get_nickname()
        token_text = self.get_token()
        if nickname_text != "" and token_text != "" and self.check_owner(nickname_text, token_text):
            try:
                bot_thread = threading.Thread(target=bot.init_bot, args=(nickname_text, self))
                bot_thread.start()
                with open("info.json", "r", encoding="utf-8") as info:
                    data = json.load(info)
                data["nickname"] = nickname_text
                data["token"] = token_text
                with open("info.json", "w", encoding="utf-8") as info:
                    json.dump(data, info, indent=4, ensure_ascii=False)
            except Exception as e:
                print(e)

    # Проверка на владельца канала
    def check_owner(self, nickname, access_token):
        client_id = 'gp762nuuoqcoxypju8c569th9wz7q5'
        url_user = 'https://api.twitch.tv/helix/users'

        headers = {'Client-ID': client_id,
                   'Authorization': f'Bearer {access_token}'}
        response_user = requests.get(url_user, headers=headers)
        user_data = response_user.json()

        if 'data' in user_data and len(user_data['data']) > 0:
            user_id = user_data['data'][0]['id']
            url_channel = f'https://api.twitch.tv/helix/users?login={nickname}'
            response_channel = requests.get(url_channel, headers=headers)
            channel_data = response_channel.json()

            if 'data' in channel_data and len(channel_data['data']) > 0:
                channel_id = channel_data['data'][0]['id']
                if user_id == channel_id:
                    return True
                else:
                    return False
            else:
                print("Error 404: channel not found.")
                return False
        else:
            print("Error: token is invalid.")
            return False

    # добавить строку в консоль
    def console_add_line(self, message):
        if message != "":
            self.console_textedit.append(message)
        else:
            self.console_textedit.append("Unknown error")

    # Закрытие программы вместе с работой бота
    def closeEvent(self, a0, QCloseEvent=None):
        os._exit(0)

if __name__ == "__main__":
    with open("info.json", "r", encoding="utf-8") as info:
        data = json.load(info)
    nickname = data["nickname"]
    token = data["token"]

    App = QApplication(sys.argv)
    root = Root(nickname, token)
    sys.exit(App.exec())
