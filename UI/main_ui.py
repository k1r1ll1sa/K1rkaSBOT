"""Модуль для интерфейса программы"""
import os
from urllib.parse import quote
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import requests
import threading
import sys
import bot
import json
import console
from player import AudioPlayer

class CustomTitleBar(QWidget):
    def __init__(self, parent):
        super().__init__(parent)

        self.setStyleSheet("background-color: #0d1012;")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 7, 0)
        layout.setSpacing(10)

        self.spacer = QWidget(self)
        self.spacer.setFixedSize(700, 60)
        self.spacer.setStyleSheet("background-color: #0d1012")

        # Иконка
        self.icon = QLabel(parent=self.spacer)
        self.icon.setPixmap(QPixmap("icons/bot icon.png").scaled(82, 42, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.icon.setStyleSheet("background-color: #0d1012; "
                                "padding: 7px;")
        layout.addWidget(self.icon)

        # Заголовок окна
        self.title = QLabel("K1rkasBot1k", parent=self.spacer)
        self.title.setStyleSheet("background-color: #0d1012;"
            "color: qlineargradient(x1:0, y1: 0, x2: 100, y2: 0,"
            "stop: 0  rgba(173, 255, 196, 1), "
            "stop: 0.3 rgba(130, 237, 142, 1),"
            "stop: 1 rgba(52, 152, 219, 1));"
            "font: bold 20px;"
            "padding: 0px 10px;")
        layout.addWidget(self.title, alignment=Qt.AlignLeft)
        layout.addStretch()

        # Кнопка "Свернуть"
        self.minimize_button = QPushButton("–", parent=self.spacer)
        self.minimize_button.clicked.connect(parent.showMinimized)
        self.minimize_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(66, 170, 255, 1);
                color: black;
                font: bold 30px;
                border-radius: 5px;
            } QPushButton:hover {
                background-color: rgba(66, 170, 255, 0.7);
            }""")
        self.minimize_button.setFixedWidth(40)
        self.minimize_button.setFixedHeight(40)
        layout.addWidget(self.minimize_button)

        # Кнопка "Закрыть"
        self.close_button = QPushButton("✕", parent=self.spacer)
        self.close_button.clicked.connect(parent.close)
        self.close_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(238, 32, 77, 1);
                color: black;
                font: bold 30px;
                border-radius: 5px;
            } QPushButton:hover {
                background-color: rgba(238, 32, 77, 0.7);
            }""")
        self.close_button.setFixedWidth(40)
        self.close_button.setFixedHeight(40)
        layout.addWidget(self.close_button)

    # Перемещения окна
        self.dragging = False
        self.offset = QPoint()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.offset = event.globalPos() - self.parent().pos()

    def mouseMoveEvent(self, event):
        if self.dragging:
            self.parent().move(event.globalPos() - self.offset)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False


class Root(QMainWindow):
    def __init__(self, nickname, token, volume):
        super().__init__()
        self.player = AudioPlayer(initial_volume=volume)
        self.console = console.Console.init_console(self)

        self.nickname = nickname
        self.token = token
        self.is_run = False
        self.bot_instance = None

        self.switch_flag = False
        self.switch_access = True
        self.switch_text = ""

        # Параметры окна
        self.setWindowTitle("K1rkasBot1k")
        self.setFixedSize(700, 490)
        self.setAutoFillBackground(False)
        self.setStyleSheet("background: #191d20")
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.title_bar = CustomTitleBar(self)
        self.setMenuWidget(self.title_bar)

        self.title_bar = CustomTitleBar(self)
        self.setMenuWidget(self.title_bar)

        self.spacer = QWidget(self)
        self.spacer.setFixedHeight(10)
        self.spacer_0 = QWidget(self)
        self.spacer_0.setFixedHeight(5)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # Поле для ввода никнейма
        self.nickname_label = QLabel("Введите никнейм:", parent=self)
        self.nickname_label.setStyleSheet("color: white")
        self.nickname_label.setFont(QFont("Cascadia Code", 12, QFont.Bold))
        self.nickname_label.resize(130, 20)
        self.nickname_label.setAlignment(Qt.AlignCenter)

        self.nickname_lineedit = QLineEdit(parent=self)
        if self.nickname != "":
            self.nickname_lineedit.setText(self.nickname)
        self.nickname_lineedit.setStyleSheet("color: #D0D0D0;"
                                             "background: #40484f;"
                                             "border-radius:10px")
        self.nickname_lineedit.setFont(QFont("Cascadia Code", 10, QFont.Bold))
        self.nickname_lineedit.setFixedSize(200, 30)
        self.nickname_lineedit.setAlignment(Qt.AlignCenter)

        # Поле для ввода токена
        self.token_label = QLabel("Access token:", parent=self)
        self.token_label.setStyleSheet("color: white")
        self.token_label.setFont(QFont("Cascadia Code", 12, QFont.Bold))
        self.token_label.setAlignment(Qt.AlignCenter)

        self.token_lineedit = QLineEdit(parent=self)
        if self.token != "":
            self.token_lineedit.setText(self.token)
        self.token_lineedit.setStyleSheet("color: #D0D0D0;"
                                          "background: #40484f;"
                                          "border-radius:10px;"
                                          "padding: 0px 25px 0px 35px")
        self.token_lineedit.setFixedHeight(30)
        self.token_lineedit.setFont(QFont("Cascadia Code", 10, QFont.Bold))
        self.token_lineedit.setAlignment(Qt.AlignLeft)
        self.token_lineedit.setFixedSize(200,30)

        self.eyes = QPushButton(parent=self.token_lineedit)
        self.eyes.setFixedSize(30,30)
        self.eyes.setIcon(QIcon("icons/openeye.png"))
        self.eyes.setIconSize(QSize(20,20))
        self.eyes.setStyleSheet("text-align: center")
        self.eyes.clicked.connect(lambda: self.switch(self.token_lineedit.text()))

        # Кнопка "Запустить"
        self.start_button = QPushButton("Запустить", parent=self)
        self.start_button.clicked.connect(self.run_button)
        self.start_button.setFont(QFont("Cascadia Code", 12, QFont.Bold))
        self.start_button.setFixedSize(200,30)
        self.start_button.setStyleSheet("""QPushButton{
                background: qlineargradient(x1:0, y1: 0.5, x2: 1, y2: 0.5,
                stop: 0  rgba(173, 255, 196, 1), stop: 0.3 rgba(130, 237, 142, 1), stop: 1 rgba(52, 152, 219, 1));
                border-radius: 10px;
            } QPushButton:hover { 
                background: qlineargradient( x1:0, y1: 0.5, x2: 1, y2: 0.5,
                stop: 0  rgba(173, 255, 196, 0.7), stop: 0.3 rgba(130, 237, 142, 0.7), stop: 1 rgba(52, 152, 219, 0.7));
            } QPushButton:pressed { 
                background: qlineargradient( x1:0, y1: 0.5, x2: 1, y2: 0.5,
                stop: 0  rgba(173, 255, 196, 0.5), stop: 0.3 rgba(130, 237, 142, 0.5), stop: 1 rgba(52, 152, 219, 0.5));
            }""")

        # Текст "Перейдите по ссылке:"
        self.tokengenerator_label = QLabel("Перед запуском перейдите по ссылке:", parent=self)
        self.tokengenerator_label.setStyleSheet("color:white;"
                                                "padding: 0px 10px")
        self.tokengenerator_label.setFont(QFont("Cascadia Code", 12, QFont.Bold))
        self.tokengenerator_label.setAlignment(Qt.AlignCenter)

        # Ссылка на токен генератор
        self.tokengenerator_lineedit = QLineEdit("https://twitchtokengenerator.com", parent=self)
        self.tokengenerator_lineedit.setStyleSheet("color: #D0D0D0;"
                                                   "background: #40484f;"
                                                   "border-radius: 10px;"
                                                   "font: bold italic;"
                                                   "padding: 0px 10px")
        self.tokengenerator_lineedit.setFixedHeight(30)
        self.tokengenerator_lineedit.setFont(QFont("Times New Roman", 11))
        self.tokengenerator_lineedit.setMinimumWidth(320)
        self.tokengenerator_lineedit.setAlignment(Qt.AlignCenter)
        self.tokengenerator_lineedit.setReadOnly(True)

        # Инструкция по запуску
        self.manual_label = QLabel('Авторизуйтесь, используя <Bot chat token>.'
                                   ' Скопируйте содержимое поля access token и вставьте в соответствующее поле в программе.',
                                   parent=self)
        self.manual_label.setStyleSheet("color:white; padding: 0px 10px")
        self.manual_label.setFont(QFont("Cascadia Code", 12, QFont.Bold))
        self.manual_label.setAlignment(Qt.AlignJustify)
        self.manual_label.setWordWrap(True)

        # "Нажмите кнопку запустить"
        self.start_label = QLabel('Нажмите кнопку "Запустить"', parent=self)
        self.start_label.setStyleSheet("color:white")
        self.start_label.setFont(QFont("Cascadia Code", 12, QFont.Bold))
        self.start_label.setAlignment(Qt.AlignCenter)
        self.start_label.setWordWrap(True)

        # Консоль
        self.console_textedit = QTextEdit("Hello! It`s a console!", parent=self)
        self.console_textedit.setStyleSheet("""
            QTextEdit {
                color: #D0D0D0;
                background: #40484f;
                border-radius: 5px;
                padding: 0px 5px 0px 5px;
            } QScrollBar:vertical {
                border: none;
                background: #40484f;
                width: 10px;
                margin: 0px 0px 0px 0px;
            } QScrollBar::handle:vertical {
                background: #60686f;
                min-height: 50px;
                border-radius: 5px;
                margin: 5px 0px 5px 0px;
            } QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
                height: 0px;
            } QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: #40484f;
            }""")
        self.console_textedit.setFont(QFont("Cascadia Code", 11))
        self.console_textedit.setAlignment(Qt.AlignLeft)
        self.console_textedit.setMinimumWidth(270)
        self.console_textedit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.console_textedit.setReadOnly(True)

        self.console_width = 75

        # Поле для ввода команд
        self.console_lineedit = QLineEdit(parent=self)
        self.console_lineedit.setPlaceholderText('вводите команды здесь!')
        self.console_lineedit.setText('')
        self.console_lineedit.setStyleSheet("color: #D0D0D0;"
                                            "background: #40484f;"
                                            "border-radius: 5px;"
                                            f"padding: 0px {self.console_width}px 0px 5px")
        self.console_lineedit.setFixedHeight(30)
        self.console_lineedit.setFont(QFont("Cascadia Code", 11))
        self.console_lineedit.setAlignment(Qt.AlignLeft)
        self.setup_enter_key_handler()

        self.enter_button = QPushButton("🠔",parent=self.console_lineedit)
        self.enter_button.clicked.connect(self._handle_command)
        self.enter_button.setStyleSheet("""QPushButton{
            background: qlineargradient(x1:0, y1: 0.5, x2: 1, y2: 0.5,
            stop: 0  rgba(173, 255, 196, 1), stop: 0.3 rgba(130, 237, 142, 1), stop: 1 rgba(52, 152, 219, 1));
            border-radius: 5px; color: black; font-size: 30px; padding: 0px 0px 0px 0px;
        } QPushButton:hover { 
            background: qlineargradient( x1:0, y1: 0.5, x2: 1, y2: 0.5,
            stop: 0  rgba(173, 255, 196, 0.7), stop: 0.3 rgba(130, 237, 142, 0.7), stop: 1 rgba(52, 152, 219, 0.7));
        } QPushButton:pressed { 
            background: qlineargradient( x1:0, y1: 0.5, x2: 1, y2: 0.5,
            stop: 0  rgba(173, 255, 196, 0.5), stop: 0.3 rgba(130, 237, 142, 0.5), stop: 1 rgba(52, 152, 219, 0.5));
        }""")
        self.enter_button.setFixedSize(75, 30)
        self.update_position()

        # Напонимание
        self.notification = QLabel("не забудьте выдать права модератора аккаунту k1rkasbot1k")
        self.notification.setStyleSheet("color: #BBBBBB;")
        self.notification.setFont(QFont("Cascadia Code", 10))
        self.notification.setAlignment(Qt.AlignCenter)

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

        # 0 + 1 столбец, 11 строка
        layout.addWidget(self.notification, 11, 0, 2, 0)
        self.setLayout(layout)
        self.show()

    def setup_enter_key_handler(self):
        self.console_lineedit.returnPressed.connect(self._handle_enter_pressed)

    def _handle_enter_pressed(self):
        self._handle_command()

    def _handle_command(self):
        msg = self.console_lineedit.text().strip()
        commands = sorted(self.console.commands, key=len, reverse=True)
        command, arg = None, ""
        for cmd in commands:
            if msg.startswith(cmd):
                command = cmd
                arg = msg[len(cmd):].strip()
                break
        if command is None:
            command = msg
            arg = ""
        self.console.handle_command(command, arg)

    def update_position(self):
        lineedit_rect = self.console_lineedit.geometry()
        button_x = 3*lineedit_rect.width() + 20 - self.enter_button.width()
        self.enter_button.move(button_x, 0)

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
            if self.is_run is False:
                if token_text == "*******************":
                    token_text = self.switch_text
                if nickname_text != "" and token_text != "" and self.check_owner(nickname_text, token_text):
                    try:
                        self.bot_thread = threading.Thread(target=bot.init_bot, args=(nickname_text, self, self.player))
                        self.bot_thread.start()
                        with open("info.json", "r", encoding="utf-8") as info:
                            data = json.load(info)
                        data["nickname"] = nickname_text
                        data["token"] = token_text
                        with open("info.json", "w", encoding="utf-8") as info:
                            json.dump(data, info, indent=4, ensure_ascii=False)
                        self.is_run = True
                        self.switch_flag = False
                        self.switch(token_text)
                        self.switch_access = False
                    except Exception as e:
                        self.console_add_line(f'Error when launching the bot: {e}.', 'error')
                elif nickname_text == "" or token_text == "":
                    self.console_add_line('Fill in the nickname and token fields.', 'error')

    # Проверка на владельца канала
    def check_owner(self, nickname, access_token):
        with open("tokens.json", "r", encoding="utf-8") as info_:
            data = json.load(info_)
            client_id = data["client_id"]
        url_user = 'https://api.twitch.tv/helix/users'

        # Избавление от спец символов (включая кириллицу)
        # для избежания краша
        encoded_token = quote(access_token.encode('utf-8'))
        headers = {'Client-ID': client_id,
                   'Authorization': f'Bearer {encoded_token}'}
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
                    self.console_add_line('Token is invalid.', 'error')
                    return False
            else:
                self.console_add_line('Channel not found.', 'error')
                return False
        else:
            self.console_add_line('unknown error when verifying the token.', 'error')
            return False


    def switch(self, text):
        if self.switch_access is True:
            if self.switch_flag is False:
                self.token_lineedit.setReadOnly(True)
                self.switch_text = text
                self.token_lineedit.setText("*******************")
                self.eyes.setIcon(QIcon("icons/closeeye.png"))
                self.switch_flag = True
            else:
                self.token_lineedit.setReadOnly(False)
                self.switch_flag = False
                self.token_lineedit.setText(self.switch_text)
                self.eyes.setIcon(QIcon("icons/openeye.png"))
        else:
            self.eyes.setIcon(QIcon("icons/closeeyered.png"))
            QTimer.singleShot(200, lambda: self.eyes.setIcon(QIcon("icons/closeeye.png")))

            # добавить строку в консоль
    def console_add_line(self, message, msg_type='user_use_bot_command'):
        if msg_type == 'user_use_bot_command':
            parts = message.split(' ', 1)
            first_word, rest = parts
            self.console_textedit.append(f'<span style="color: Azure;">{first_word}</span> {rest}')
        elif msg_type == 'bot_launch':
            self.console_textedit.append(f'<span style="color: MediumSpringGreen;">{message}</span>')
        elif msg_type == 'error':
            self.console_textedit.append(f'<span style="color: Red;"> Error: </span>{message}')
        elif msg_type == 'console_command':
            self.console_textedit.append(f'<span style="color: LightCyan;">{message}</span>')
        else:
            self.console_textedit.append("Unknown error")

    # Закрытие программы вместе с работой бота
    def closeEvent(self, a0, QCloseEvent=None):
        os._exit(0)