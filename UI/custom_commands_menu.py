"""Модуль с окном для натсройки кастомных команд"""
import json

from PyQt5 import Qt
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

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


class Commands_Menu(QMainWindow):
    def __init__(self):
        super().__init__()
        self.bot = None
        self.setWindowTitle("K1rkasBot1k - Настройки команд")
        self.setFixedSize(700, 490)
        self.setAutoFillBackground(False)
        self.setStyleSheet("background: #191d20")
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.title_bar = CustomTitleBar(self)
        self.setMenuWidget(self.title_bar)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Список команд
        commands_panel = QWidget()
        commands_layout = QVBoxLayout(commands_panel)
        commands_layout.setContentsMargins(0, 0, 0, 0)
        commands_layout.setSpacing(5)

        self.commands_list = QListWidget()
        self.commands_list.setFocusPolicy(Qt.NoFocus)
        self.commands_list.setStyleSheet("""
            QListWidget {
                background: #40484f;
                color: #D0D0D0;
                border-radius: 5px;
            } 
            QListWidget::item {
                padding: 8px;
                border-radius: 5px;
            } 
            QListWidget:QAbstractItemView {
                outline: 0px;
            }
            QListWidget::item:selected {
                background: #2a82da; 
                color: white;
            }
            QListWidget::item:selected:first {
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }
            QListWidget::item:selected:last {
                border-bottom-left-radius: 5px;
                border-bottom-right-radius: 5px;
            }
            QScrollBar:vertical {
                border: none;
                background: #40484f;
                width: 10px;
                margin: 0px 0px 0px 0px;
            } 
            QScrollBar::handle:vertical {
                background: #60686f;
                min-height: 50px;
                border-radius: 5px;
                margin: 5px 0px 5px 0px;
            } 
            QScrollBar::add-page:vertical, 
            QScrollBar::sub-page:vertical {
                background: #40484f;
            } 
            QScrollBar::add-line:vertical, 
            QScrollBar::sub-line:vertical {
                border: none;
                background: none;
                height: 0px;
            }
        """)
        self.commands_list.setFont(QFont('Cascadia Code', 10, QFont.Bold))
        self.commands_list.setFixedWidth(250)
        commands_layout.addWidget(self.commands_list)

        buttons_container = QWidget()
        buttons_container.setFixedWidth(250)
        buttons_layout = QHBoxLayout(buttons_container)
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_layout.setSpacing(5)

        self.add_button = QPushButton("Добавить")
        self.delete_button = QPushButton("Удалить")

        for button in [self.add_button, self.delete_button]:
            button.setStyleSheet("""
                QPushButton {
                    background: #40484f;
                    color: white;
                    border-radius: 5px;
                    padding: 5px;
                    min-width: 70px;
                }
                QPushButton:hover {
                    background: #505860;
                }
            """)
            button.setFont(QFont('Cascadia Code', 10, QFont.Bold))
            button.setFixedHeight(40)
            buttons_layout.addWidget(button)

        commands_layout.addWidget(buttons_container)
        main_layout.addWidget(commands_panel)

        # Правая панель с настройками команды
        settings_panel = QWidget()
        settings_layout = QVBoxLayout(settings_panel)
        settings_layout.setContentsMargins(0, 0, 0, 0)
        settings_layout.setSpacing(5)

        # Контейнер для полей названия и кулдауна
        top_row = QWidget()
        top_layout = QHBoxLayout(top_row)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(20)

        # Группа для названия команды
        name_group = QWidget()
        name_layout = QVBoxLayout(name_group)
        name_layout.setContentsMargins(0, 0, 0, 0)
        name_layout.setSpacing(5)

        self.name_label = QLabel("Название команды:")
        self.name_label.setFont(QFont('Cascadia Code', 12, QFont.Bold))
        self.name_label.setStyleSheet("color: white; padding-left: 5px;")

        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText('Придумайте название')
        self.name_edit.setFont(QFont('Cascadia Code', 10, QFont.Bold))
        self.name_edit.setStyleSheet("""
            QLineEdit {
                background: #40484f;
                color: #D0D0D0;
                border-radius: 5px;
                padding: 8px;
            }
        """)

        name_layout.addWidget(self.name_label)
        name_layout.addWidget(self.name_edit)
        top_layout.addWidget(name_group)

        # Группа для кулдауна
        cooldown_group = QWidget()
        cooldown_layout = QVBoxLayout(cooldown_group)
        cooldown_layout.setContentsMargins(0, 0, 0, 0)
        cooldown_layout.setSpacing(5)

        self.cooldown_label = QLabel("Кулдаун:")
        self.cooldown_label.setFont(QFont('Cascadia Code', 12, QFont.Bold))
        self.cooldown_label.setStyleSheet("color: white; padding-left: 5px;")

        self.cooldown_edit = QLineEdit()
        self.cooldown_edit.setPlaceholderText('Кулдаун в секундах')
        self.cooldown_edit.setFont(QFont('Cascadia Code', 10, QFont.Bold))
        self.cooldown_edit.setStyleSheet("""
            QLineEdit {
                background: #40484f;
                color: #D0D0D0;
                border-radius: 5px;
                padding: 8px;
            }
        """)
        self.cooldown_edit.setValidator(QIntValidator(0, 3600))

        cooldown_layout.addWidget(self.cooldown_label)
        cooldown_layout.addWidget(self.cooldown_edit)
        top_layout.addWidget(cooldown_group)

        settings_layout.addWidget(top_row)

        # Поле для текста команды
        self.text_label = QLabel("Текст ответа:")
        self.text_label.setFont(QFont('Cascadia Code', 12, QFont.Bold))
        self.text_label.setStyleSheet("color: white; padding-left: 5px;")
        self.text_label.setFixedWidth(400)
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText('Что должен ответить бот? Придумайте что-то оригинальное!')
        self.text_edit.setFont(QFont('Cascadia Code', 10, QFont.Bold))
        self.text_edit.setStyleSheet("""
            QTextEdit {
                background: #40484f;
                color: #D0D0D0;
                border-radius: 5px;
                margin-bottom: 5px;
                padding-left: 8px;
                padding-top: 5px;
                padding-bottom: 5px;
                padding-right: 8px;
            }
        """)
        self.text_edit.setFixedHeight(70)
        settings_layout.addWidget(self.text_label)
        settings_layout.addWidget(self.text_edit)

        # Инструкция
        self.instructions = QTextEdit()
        self.instructions.setFont(QFont('Cascadia Code', 10, QFont.Bold))
        self.instructions.setPlainText(
            "Специальные обозначения:\n"
            "{name} - никнейм человека, который использовал команду\n"
            "{random(min, max)} - случайное число от min до max\n"
            "{msg} - сообщение после команды (!привет к̲т̲о̲-̲т̲о̲)\n\n"
            "> Название команды может содержать только одно слово\n"
            "> Оставьте чекбоксы пустыми, если команда доступна для всех\n"
            "> Кулдаун по умолчанию - 1 минута, а максимально допустимый - 1 час\n"
            "> Нажмите 'сохранить' когда закончите с настройкой команды\n"
        )
        self.instructions.setStyleSheet("""
            QTextEdit {
                background: #40484f;
                color: #D0D0D0;
                border-radius: 5px;
                padding-left: 8px;
                padding-top: 5px;
                padding-bottom: 5px;
                padding-right: 8px;
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
            } QScrollBar::add-page:vertical, 
                QScrollBar::sub-page:vertical {
                background: #40484f;
            } QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
                height: 0px;
            } QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: #40484f;
            """)

        self.instructions.setReadOnly(True)
        self.instructions.setFixedHeight(100)
        settings_layout.addWidget(self.instructions)

        # Чекбоксы для прав доступа
        self.access_group = QGroupBox("Кто может использовать:")
        self.access_group.setFont(QFont('Cascadia Code', 12, QFont.Bold))
        self.access_group.setStyleSheet("""
            QGroupBox {
                color: white;
                border: 1px solid #40484f;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 22px;
            }
        """)

        access_layout = QHBoxLayout()
        access_layout.setContentsMargins(10, 5, 10, 10)
        access_layout.setSpacing(20)

        self.moderator_check = QCheckBox("Модераторы")
        self.moderator_check.setFont(QFont('Cascadia Code', 10, QFont.Bold))
        self.moderator_check.setStyleSheet("color: white;")
        self.vip_check = QCheckBox("VIP")
        self.vip_check.setFont(QFont('Cascadia Code', 10, QFont.Bold))
        self.vip_check.setStyleSheet("color: white;")

        access_layout.addWidget(self.moderator_check)
        access_layout.addWidget(self.vip_check)
        access_layout.addStretch()

        self.access_group.setLayout(access_layout)
        settings_layout.addWidget(self.access_group)

        # Кнопка сохранения
        self.save_button = QPushButton("Сохранить")
        self.save_button.setStyleSheet("""
            QPushButton {
                background: #2a82da;
                color: white;
                border-radius: 5px;
                padding: 8px;
                font: bold 12px;
            }
            QPushButton:hover {
                background: #1a6fc9;
            }
        """)
        self.save_button.setFixedHeight(40)
        settings_layout.addWidget(self.save_button)

        main_layout.addWidget(settings_panel)

        # Подклчение кнопок
        self.add_button.clicked.connect(self.add_command)
        self.save_button.clicked.connect(self.save_command)
        self.delete_button.clicked.connect(self.delete_command)

        self.moderator_check.stateChanged.connect(self.update_checkboxes)
        self.vip_check.stateChanged.connect(self.update_checkboxes)

        self.load_commands()
        self.commands_list.itemClicked.connect(self.load_selected_command)

    # Обновление чекбоксов
    def update_checkboxes(self, state):
        sender = self.sender()
        if sender == self.moderator_check and state == Qt.Checked:
            self.vip_check.setChecked(False)
        elif sender == self.vip_check and state == Qt.Checked:
            self.moderator_check.setChecked(False)

    # Определение доступа по чекбоксам
    def get_access_level(self):
        if self.moderator_check.isChecked():
            return "mod"
        elif self.vip_check.isChecked():
            return "vip"
        else:
            return "all"

    # Добавление команды
    def add_command(self):
        self.name_edit.clear()
        self.text_edit.clear()
        self.moderator_check.setChecked(False)
        self.vip_check.setChecked(False)
        self.commands_list.setCurrentItem(None)

    # Загрузка данных из выбранного элемента в списке
    def load_selected_command(self):
        current_item = self.commands_list.currentItem()
        if current_item:
            cmd_data = current_item.data(Qt.UserRole)
            self.name_edit.setText(current_item.text())
            self.text_edit.setPlainText(cmd_data["text"])
            self.cooldown_edit.setText(str(cmd_data.get("cooldown", 60)))
            access = cmd_data["access"]
            self.moderator_check.setChecked(access == "mod")
            self.vip_check.setChecked(access == "vip")

    # Сохранение команды в json
    def save_command(self):
        name = self.name_edit.text().strip()
        if not name.startswith("!"):
            name = "!" + name
        text = self.text_edit.toPlainText().strip()
        cooldown = int(self.cooldown_edit.text()) if self.cooldown_edit.text() else 60
        access = self.get_access_level()
        error = False
        if not name or ' ' in name:
            self.highlight_label(self.name_label)
            error = True
        if not text:
            self.highlight_label(self.text_label)
            error = True
        if error:
            return
        try:
            with open('custom_commands.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
        except:
            data = {"custom_commands": {}}

        current_item = self.commands_list.currentItem()
        if current_item is not None:
            if name in data["custom_commands"] and name != current_item.text():
                self.highlight_label(self.name_label)
                return
            previous_name = current_item.text()
            del data["custom_commands"][previous_name]

        if name in data["custom_commands"]:
            self.highlight_label(self.name_label)
            return
        data["custom_commands"][name] = {
            "text": text,
            "access": access,
            "cooldown": cooldown
        }
        with open('custom_commands.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        self.load_commands()

    # Удаление команд
    def delete_command(self):
        current_item = self.commands_list.currentItem()
        if not current_item:
            return
        name = current_item.text()
        with open('custom_commands.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        if name in data["custom_commands"]:
            del data["custom_commands"][name]
            with open('custom_commands.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            self.load_commands()

    # Загрузка команд в спсиок
    def load_commands(self):
        self.commands_list.clear()
        with open('custom_commands.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        for name, cmd_data in data.get("custom_commands", {}).items():
            item = QListWidgetItem(name)
            item.setData(Qt.UserRole, cmd_data)
            self.commands_list.addItem(item)
        if self.bot:
            self.bot.update_custom_commands()

    # Подсвечивание лейблов для ошибок
    def highlight_label(self, label):
        original_style = label.styleSheet()
        label.setStyleSheet("color: red; padding-left: 5px;")
        QTimer.singleShot(500, lambda: label.setStyleSheet(original_style))

    def init_bot(self, bot):
        self.bot = bot
