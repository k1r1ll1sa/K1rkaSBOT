import rating
import json
from UI.custom_commands_menu import Commands_Menu

class Console():
    def __init__(self, root):
        self.rating = rating.Rating()
        self.root = root # Основное окно
        self.bot = None
        self.commands = ['банворд добавить', 'банворд удалить', 'банворд список', 'помощь', 'ссылка список', 'ссылка добавить', 'ссылка удалить', 'реклама', 'реклама включить', 'реклама выключить', 'плохиши', 'команда']
        self.help_list = ['банворд удалить (банворд) - добавляет новое слово в список запрещённых слов. '
            'Используйте * на конце слова. Это будет означать любой символ до пробела',
            'банворд удалить (удаляемое слово) - удаляет слово из списка запрещённых слов',
            'банворд список - выводит список всех запрещённых слов',
            'плохиши - выводит топ 5 чатеров по количеству отстранений',
            'ссылка добавить (ссылка) - добавляет новую ссылку в список разрешённых ссылок',
            'ссылка удалить (ссылка) - удаляет ссылку из списка разрешённых ссылок',
            'ссылка список - выводит список всех разрешённых ссылок',
            'реклама (описание), (время повтора) - реклама описанного вами ресурса. После запятой нужно указать вермя (в минутах) повторной отправки рекламы. Автоматически включает рекламу',
            'реклама включить - включает рекламу',
            'реклама выключить - выключает рекламу',
            'команда - вызывает меню для настройки пользовательских команд',
            'плеер - инструкция по плееру для соунд реквестов',
            'помощь - выводит список всех доступных команд']
        self.player_inst = ['Плеер доступен только модераторам или вип',
            '!реквест (youtube-url) - добавить трек в очередь. Без аргумента выведет текущий играющий трек',
            '!пауза - ставит проигрыватель на паузу (для стримера)',
            '!продолжить - возобновляет проигрывание (для стримера)',
            '!скип - пропускает трек (для модераторов и вип)',
            '!громкость (число) - устанавливает громкость на (число) (для стримера)',
            'Допускаются только треки длительностью менее 5 минут и числом просмотров более 50000!',
            'Для корректной работы необходимо установить MPV проигрыватель (https://github.com/shinchiro/mpv-winbuild-cmake/releases) и добавить его в PATH.'
            'Он будет использоваться в фоне и отключаться вместе с приложением бота.',
            'ДЛЯ ИЗБЕЖАНИЯ НАКАЗАНИЙ ЗА АП ДОБАВЬТЕ ПЛЕЕР В СПЕЦИАЛЬНУЮ АУДИО-ДОРОЖКУ ДЛЯ АВТОМАТИЧЕСКОГО УДАЛЕНИЯ МУЗЫКИ С ЗАПИСИ!']
        with open('banwords.txt', "r", encoding='utf-8') as file:
            lines = file.readlines()
            self.banwords_list = lines[0].strip().split(', ')[1:]
            self.banwords_without_stars = [i.replace('*', '') for i in self.banwords_list]
            self.allow_links = lines[1].strip().split(', ')[1:]

    def set_bot(self, bot):
        self.bot = bot

    def update_banword_txt(self):
        with open('banwords.txt', 'w', encoding='utf-8') as file:
            file.write(f'список запрещённых слов:, {', '.join(self.banwords_list)}\n')
            file.write(f'список разрешённых ссылок:, {', '.join(self.allow_links)}\n')
            file.write("\nНЕ ОТКРЫВАЙТЕ И НЕ ПОКАЗЫВАЙТЕ ЭТОТ ФАЙЛ В ПРЯМОМ ЭФИРЕ\nОН МОЖЕТ СОДЕРЖАТЬ СЛОВА ЗАПРЕЩЁННЫЕ ПЛАТФОРМОЙ!\n\n\
Для добавления нового слова или ссылки добавьте его в конец соответствующей строки. В качестве разделителя используйте запятую с пробелом.\n\
При таком способе нужно будет использовать в консоле команду 'банворд обновить', чтобы бот распознал новые слова.\n\
Либо вы можете добавить слово или ссылку через консоль в приложении, использовать комманду 'банворд добавить <банворд>'.\n\
Вы можете добавить * в конец запрещённого слова, что будет означать любой символ до пробела.\n")
        self.banwords_without_stars = [i.replace('*', '') for i in self.banwords_list]

    # Обработчик команд
    def handle_command(self, command='', arg=''):
        command = command.strip().lower()
        arg = arg.strip().lower()
        if command == '':
            self.root.console_add_line('An empty input was received. Use help to help.', 'error')
        elif command == 'банворд добавить':
            if arg != '':
                if arg not in self.banwords_list:
                    self.banwords_list.append(arg)
                    self.update_banword_txt()
                    if self.bot:
                        self.bot.update_banwords()
                    self.root.console_add_line(f'Banword "{arg}" added!', 'console_command')
                else:
                    self.root.console_add_line(f'This word is already on the list of banwords!', 'console_command')
            else:
                self.root.console_add_line('Point out banword!', 'error')
        elif command == 'банворд удалить':
            if arg != '':
                if arg in self.banwords_without_stars:
                    index = self.banwords_without_stars.index(arg)
                    self.banwords_list.pop(index)
                    self.update_banword_txt()
                    if self.bot:
                        self.bot.update_banwords()
                    self.root.console_add_line(f'Banword "{arg}" deleted!', 'console_command')
                else:
                    self.root.console_add_line('This word is not on the list of banwords!', 'error')
            else:
                self.root.console_add_line('Point out banword!', 'error')
        elif command == 'банворд список':
            self.root.console_add_line(f'Banwords list: {", ".join(self.banwords_list)}', 'console_command')
        elif command == 'помощь':
            self.root.console_add_line('All available commands:', 'console_command')
            for i in self.help_list:
                self.root.console_add_line(f'* {i}', 'console_command')
            self.root.console_add_line(' ')
        elif command == 'плохиши':
            self.root.console_add_line('The most frequent violators:', 'console_command')
            top = self.rating.get_top_users_timeouts()
            for nickname, timeouts in top:
                self.root.console_add_line(f'{nickname} - {timeouts["timeout_count"]} timeouts', 'console_command')
        elif command == 'ссылка добавить':
            if arg:
                if arg not in self.allow_links:
                    self.allow_links.append(arg)
                    self.update_banword_txt()
                    self.root.console_add_line(f'Link "{arg}" added to allowed list!', 'console_command')
                    if self.bot:
                        self.bot.update_banwords()
                else:
                    self.root.console_add_line('This link is already in the allowed list!', 'error')
            else:
                self.root.console_add_line('Specify the link!', 'error')
        elif command == 'ссылка удалить':
            if arg:
                if arg in self.allow_links:
                    self.allow_links.remove(arg)
                    self.update_banword_txt()
                    self.root.console_add_line(f'Link "{arg}" removed from allowed list!', 'console_command')
                    if self.bot:
                        self.bot.update_banwords()
                else:
                    self.root.console_add_line('This link is not in the allowed list!', 'error')
            else:
                self.root.console_add_line('Specify the link!', 'error')
        elif command == 'ссылка список':
            self.root.console_add_line(f'Allowed links list: {", ".join(self.allow_links)}', 'console_command')
        elif command == 'реклама':
            if arg:
                try:
                    if not ',' in arg:
                        self.root.console_add_line(f'use a comma as a separator!','error')
                    else:
                        arg = arg.split(', ', 1)
                        desc, time = arg[0], arg[1]
                        self.root.console_add_line(f'The ad has been created: {desc}. Repeat time:{time}.', 'console_command')
                        with open('info.json', 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        data['adv'] = {'desc': desc, 'time': time}
                        with open('info.json', 'w', encoding='utf-8') as f:
                            json.dump(data, f , ensure_ascii=False, indent=4)
                        if self.bot:
                            self.bot.is_adv = True
                except Exception as e:
                    print(e)
            else:
                self.root.console_add_line(f'No description or time was received.', 'error')
        elif command == 'реклама включить':
            if self.bot:
                self.root.console_add_line('Ads are enabled!', 'console_command')
                self.bot.is_adv = True
            else:
                self.root.console_add_line('Turn on the bot first!', 'error')
        elif command == 'реклама выключить':
            if self.bot:
                self.root.console_add_line('Ads are disabled!', 'console_command')
                self.bot.is_adv = False
            else:
                self.root.console_add_line('Turn on the bot first!', 'error')
        elif command == 'команда':
            try:
                self.commands_window = Commands_Menu()
                self.commands_window.init_bot(self.bot)
                self.commands_window.show()
            except Exception as e:
                print(e)
        elif command == 'плеер':
            self.root.console_add_line('Инструкция по плееру:', 'console_command')
            for i in self.player_inst:
                self.root.console_add_line(f'* {i}', 'console_command')
            self.root.console_add_line(' ')
        self.root.console_lineedit.setText('')

    def init_console(root):
        return Console(root)