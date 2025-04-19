"""Модуль с функционалом бота"""
import random
from operator import index

import httpx
import urllib.parse
import requests
import twitchio.errors
from certifi.core import exit_cacert_ctx
from twitchio import Message
from twitchio.ext import commands
from twitchio.ext.commands import CommandOnCooldown, Cooldown, Bucket
from twitchio.models import PartialUser
from twitchio.http import TwitchHTTP
from twitchio.errors import HTTPException
import asyncio
from datetime import datetime, timezone
from dateutil.parser import parse
from googletrans import Translator
import json
import itertools
import re
import rating

rating = rating.Rating()

def init_bot(nickname, root):
    try:
        with open("tokens.json", "r", encoding="utf-8") as tokens:
            config = json.load(tokens)
        token = config["token"]
        client_secret = config["client_secret"]
        client_id = config["client_id"]

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        bot = Bot(nickname, token, client_secret, client_id, root)
        root.bot_instance = bot
        loop.run_until_complete(bot.run())
    except Exception as e:
        print(e)

class Bot(commands.Bot):
    def __init__(self, nickname, token, client_secret, client_id, root):
        self.nickname = nickname
        self.channel = None
        self.nickname_ = "#" + nickname
        self.token = token
        self.client_secret = client_secret
        self.client_id = client_id
        self.root = root
        self.chatters = []
        self.message_count = 1
        self.http = TwitchHTTP(client_id=self.client_id, client=self, client_secret=self.client_secret)
        self.user = None # PartialUser
        self.bot_id = None

        # Рулетка
        self.lose_count = 6
        self.random_count = None
        self.roulette_is_run = False

        # Бомба
        self.colors = ['зеленый', 'красный', 'синий']
        self.correct_color = None

        # Wodly
        self.correct_word = None
        self.hidden_word = ''
        with open('russian_nouns.txt', 'r', encoding='utf-8') as file:
            self.words = [line.strip() for line in file]

        # Отслеживание зрителей
        self.prew_viewers = 0
        self.cur_viewers = 0

        # Розыгрыш
        self.raffle_key_word = '+'
        self.raffle_player_list = []
        self.raffle_flag = False
        self.raffle_black_list = []

        # Задача
        self.answer = 0
        self.task_flag = False

        # Словарь для автомодерации RU & ENG
        self.lit_dict = {"0": ["o", "о"],"1": ["i", "l", "!"],"2": ["z"],"3": ["e", "з", "е"],"4": ["ч", "h"],
                         "5": ["s"],"6": ["b", "б"],"7": ["t"],"9": ["g"],"@": ["a", "а"],"#": ["h", "н"],"$": ["s"],
                         "%": ["x"],"?": ["p"],"!": ["i"],"|": ["i", "l"], "a": ["а"],"b": ["в", "б", "ь", "ъ"],
                         "c": ["с", "c"],"e": ["е", "ё"],"f": ["ф"],"g": ["д", "g"],"h": ["н"],"i": ["и"],"j": ["у"],
                         "k": ["к"],"l": ["л"],"m": ["м"],"n": ["и", "п", "й"],"o": ["о"],"p": ["р", "п"],
                         "r": ["г", "я"],"s": ["с", "з"],"t": ["т"],"u": ["у", "ц"],"v": ["u", "v"],"w": ["ш", "щ", "в"],
                         "x": ["х"],"y": ["у", "й"], "(": ["с", "c"],")": ["j"],"<": ["k"],"+": ["х", "т"],
                         "]": ["j"],"=": ["ж"],"^": ["л"],"}": ["д"],"Λ": ["л"]}
        with open('banwords.txt', "r", encoding='utf-8') as file:
            lines = file.readlines()
            self.nword_list = lines[0].strip().split(', ')[1:]
            self.allow_links = lines[1].strip().split(', ')[1:]

        # Отслеживание фолловеров
        self.last_followers = []

        super().__init__(
            prefix='!',
            token=self.token,
            client_secret=self.client_secret,
            client_id=client_id,
            initial_channels=[self.nickname_])

    async def event_ready(self):
        self.channel = self.get_channel(self.nickname)
        owner = await self.fetch_users(names=[self.nickname])
        owner_id = owner[0].id # для инициализации self.user, далее не нужен
        bot = await self.fetch_users(names=['k1rkasbot1k'])
        self.bot_id = bot[0].id
        self.user = PartialUser(self.http, owner_id, self.nickname)
        await self.channel.send(f'{self.nick} запущен!')
        self.root.console_add_line(f'{self.nick} is launched on the channel {self.nickname}')

    async def event_follow(self, follower):
        with open('info.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
        if follower.name not in data['last_followers']:
            await self.channel.send(f'{follower} спасибо за фолоу! Добро пожаловать на канал!')
            data['last_followers'].append(follower.name)
            with open('info.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)

    @commands.command(name='привет')
    @commands.cooldown(rate=1, per=5, bucket=commands.Bucket.channel)
    async def hello_command(self, ctx: commands.Context):
        await ctx.send(f'Привет, {ctx.author.name}! 👋')
        self.root.console_add_line(f'{ctx.author.name} uses the command "!привет"')
    
    @commands.command(name='время')
    async def time(self, ctx: commands.Context):
        await ctx.send(f'{ctx.author.name} моё время: {datetime.datetime.now().strftime('%H:%M')}')
        self.root.console_add_line(f'{ctx.author.name} uses the command "!время"')

    @commands.command(name='вуз')
    async def university(self, ctx: commands.Context):
        await ctx.send(f'{ctx.author.name} бот написан в лучшем вузе на свете -> https://ikit.sfu-kras.ru')
        self.root.console_add_line(f'{ctx.author.name} uses the command "!вуз"')

    @commands.command(name='рулетка')
    async def roulette(self, ctx: commands.Context, count='1'):
        if '\U000e0000' in count:
            count = 1
        try:
            count = int(count)
        except ValueError:
            count = 1
        self.root.console_add_line(f'{ctx.author.name} uses the command "!рулетка"') if count == 1 else (
            self.root.console_add_line(f'{ctx.author.name} uses the command "!рулетка" with arguments {count}'))
        if count > 1:
            self.roulette_is_run = False
        if self.roulette_is_run is False:
            if 6 >= count > 0:
                self.roulette_is_run = True
                self.random_count = random.randint(count, 6)
                if self.roul_game():
                    await ctx.send(f'{ctx.author.name} выживает!')
                else:
                    try:
                        await self.user.timeout_user(token=self.token[6:], moderator_id=self.bot_id, user_id=ctx.author.id, duration=60, reason='проиграл в рулетку...')
                        await ctx.send(f'{ctx.author.name} проиграл в рулетку...')
                    except Exception:
                        await ctx.send(f'{ctx.author.name} чудом выживает')
            else:
                await ctx.send(f'{ctx.author.name} столько патронов не влезет...')
        elif self.roulette_is_run is True:
            if self.roul_game():
                await ctx.send(f'{ctx.author.name} выживает!')
            else:
                try:
                    await self.user.timeout_user(token=self.token[6:], moderator_id=self.bot_id, user_id=ctx.author.id, duration=60, reason='проиграл в рулетку...')
                    await ctx.send(f'{ctx.author.name} проиграл в рулетку...')
                except Exception:
                    await ctx.send(f'{ctx.author.name} чудом выживает')

    def roul_game(self):
        if self.random_count < self.lose_count:
            self.random_count += 1
            return True
        elif self.random_count >= self.lose_count:
            self.roulette_is_run = False
            return False
        else:
            return True

    @commands.command(name='кубик')
    async def roll(self, ctx: commands.Context, number=100):
        message = f'{ctx.author.name} uses the command "!кубик"' if number==100 \
            else f'{ctx.author.name} uses the command "!кубик" with arguments "{number}"'
        self.root.console_add_line(message)
        random_cube = random.randint(1, number)
        if random_cube == number:
            await ctx.send(f'{ctx.author.name} критический успех! {number} 🎲')
        elif random_cube == 1:
            await ctx.send(f'{ctx.author.name} критический провал! 1 🎲')
        else:
            await ctx.send(f'{ctx.author.name} выпало число {random_cube} 🎲')

    @commands.command(name='копать')
    async def mine(self, ctx: commands.Context, command: str = '', *, phrase: str = ''):
        self.root.console_add_line(f'{ctx.author.name} uses the command "!копать"')
        if '\U000e0000' in phrase:
            phrase = phrase.replace('\U000e0000', '')
            phrase = phrase.strip()

        with open('info.json', 'r', encoding='utf-8') as f:
            info = json.load(f)
        if ctx.author.is_mod and command == 'добавить' and phrase != '':
            if phrase not in list(info['mine'].values()):
                max_key = max(int(k) for k in info['mine'].keys()) if info['mine'] else 0
                next_key = str(max_key + 1)
                info['mine'][next_key] = phrase
                with open('info.json', 'w', encoding='utf-8') as f:
                    json.dump(info, f, ensure_ascii=False, indent=4)
                await ctx.send(f'Фраза "{phrase}" добавлена в список!')
            else:
                await ctx.send(f'Фраза "{phrase}" уже есть в списке!')
            return

        if ctx.author.is_mod and command.lower() == 'список':
            if not info['mine']:
                await ctx.send("Список фраз пуст!")
                return
            try:
                page = int(phrase) if phrase else 1
            except ValueError:
                page = 1

            sorted_phrases = sorted(info['mine'].items(), key=lambda x: int(x[0]))
            total_phrases = len(sorted_phrases)
            phrases_per_page = 5

            # Уменьшение контента, если он не помещается на 1 страницу (450 символов)
            while True:
                test_message = "Список фраз (страница 1/1): " + "".join(f"{num} - {text}, " for num, text in sorted_phrases[:phrases_per_page])
                if len(test_message) <= 450 or phrases_per_page <= 1:
                    break
                phrases_per_page -= 1
            total_pages = (total_phrases + phrases_per_page - 1) // phrases_per_page
            page = max(1, min(page, total_pages))
            start_idx = (page - 1) * phrases_per_page
            end_idx = min(start_idx + phrases_per_page, total_phrases)
            phrases_list = "".join(f"{num} - {text}, " for num, text in sorted_phrases[start_idx:end_idx])

            if phrases_list.endswith(', '):
                phrases_list = phrases_list[:-2] + '...'
            message = (f"Список фраз (страница {page}/{total_pages}): {phrases_list}")
            if len(message) > 450:
                message = message[:447] + "..."
            await ctx.send(message)
            return

        if ctx.author.is_mod and command.lower() == 'удалить':
            if not phrase:
                await ctx.send("Укажите номер фразы для удаления!")
                return
            try:
                del_key = phrase
                if del_key not in info['mine']:
                    await ctx.send(f"Фраза с номером {del_key} не найдена!")
                    return

                deleted_phrase = info['mine'].pop(del_key)
                new_mine = {}
                current_num = 1

                # Сдвиг ключей
                for old_num in sorted(info['mine'].keys(), key=int):
                    new_mine[str(current_num)] = info['mine'][old_num]
                    current_num += 1

                info['mine'] = new_mine
                with open('info.json', 'w', encoding='utf-8') as f:
                    json.dump(info, f, ensure_ascii=False, indent=4)
                await ctx.send(f'Фраза "{deleted_phrase}" (№{del_key}) удалена!')
            except ValueError:
                await ctx.send("Номер фразы должен быть числом!")
            return

        # если отправитель не модератор или не использует под-команды выше
        phrase = random.choice(list(info['mine'].values()))
        await ctx.send(f'{ctx.author.name} {phrase}!')

    @commands.command(name='чай')
    async def tea(self, ctx: commands.Context, user=None):
        self.root.console_add_line(f'{ctx.author.name} uses the command "!чай" with arguments {user}')\
            if user else self.root.console_add_line(f'{ctx.author.name} uses the command "!чай"')
        if user is not None:
            user = user.lower()
            if '@' in user:
                user = user.replace('@', '')
                print(user)
        print(self.chatters)
        if user and user in self.chatters:
            await ctx.send(f'{ctx.author.name} угостил чаем {user}')
        else:
            await ctx.send(f'{ctx.author.name} угостил чаем {random.choice(self.chatters)}')

    @commands.command(name='бомба')
    async def bomb(self, ctx: commands.Context):
        self.root.console_add_line(f'{ctx.author.name} uses the command "!бомба"')
        if self.correct_color is None:
            await ctx.send('Угадай цвет, чтобы разминировать бомбу! (!зелёный, !красный, !синий)')
            self.correct_color = random.choice(self.colors)

    @commands.command(name='зелёный', aliases=['зеленый', 'green']) # с альтернативными вариантами
    async def bomb_green(self, ctx: commands.Context):
        self.root.console_add_line(f'{ctx.author.name} uses the command "!зелёный"')
        if self.correct_color is not None:
            if self.correct_color in ['зелёный', 'зеленый']:
                await ctx.send(f'{ctx.author.name} разминировал бомбу!')
            else:
                try:
                    await self.user.timeout_user(token=self.token[6:], moderator_id=self.bot_id, user_id=ctx.author.id,
                                                 duration=60, reason='такой себе сапёр...')
                    await ctx.send(f'{ctx.author.name} оказался такой себе сапёр...')
                except Exception:
                    await ctx.send(f'{ctx.author.name} увернулся от взрыва!')
            self.correct_color = None
        else:
            await ctx.send(f'{ctx.author.name} игра ещё не началась! пиши "!бомба"')

    @commands.command(name='красный')
    async def bomb_red(self, ctx: commands.Context):
        self.root.console_add_line(f'{ctx.author.name} uses the command "!красный"')
        if self.correct_color is not None:
            if self.correct_color == 'красный':
                await ctx.send(f'{ctx.author.name} разминировал бомбу!')
            else:
                try:
                    await self.user.timeout_user(token=self.token[6:], moderator_id=self.bot_id, user_id=ctx.author.id,
                                                 duration=60, reason='такой себе сапёр...')
                    await ctx.send(f'{ctx.author.name} оказался такой себе сапёр...')
                except Exception:
                    await ctx.send(f'{ctx.author.name} увернулся от взрыва!')
            self.correct_color = None
        else:
            await ctx.send(f'{ctx.author.name} игра ещё не началась! пиши "!бомба"')

    @commands.command(name='синий')
    async def bomb_blue(self, ctx: commands.Context):
        self.root.console_add_line(f'{ctx.author.name} uses the command "!синий"')
        if self.correct_color is not None:
            if self.correct_color == 'синий':
                await ctx.send(f'{ctx.author.name} разминировал бомбу!')
            else:
                try:
                    await self.user.timeout_user(token=self.token[6:], moderator_id=self.bot_id, user_id=ctx.author.id,
                                                 duration=60, reason='такой себе сапёр...')
                    await ctx.send(f'{ctx.author.name} оказался такой себе сапёр...')
                except Exception:
                    await ctx.send(f'{ctx.author.name} увернулся от взрыва!')
            self.correct_color = None
        else:
            await ctx.send(f'{ctx.author.name} игра ещё не началась! пиши "!бомба"')

    @commands.command(name='слово')
    async def word(self, ctx: commands.Context, word=None):
        self.root.console_add_line(f'{ctx.author.name} uses the command "слово" with arguments {word}') if word \
            else self.root.console_add_line(f'{ctx.author.name} uses the command "слово"')
        if self.correct_word is None:
            self.correct_word = random.choice(self.words).strip()
            self.hidden_word = '▯' * len(self.correct_word)
            print(self.correct_word)
            await ctx.send(f'{ctx.author.name} попробуй угадать слово! Оно содержит {len(self.correct_word)} букв!')
        elif self.correct_word is not None and word in self.words:
            hidden_word_list = list(self.hidden_word)
            for i, let in enumerate(self.correct_word):
                if let in word:
                    hidden_word_list[i] = let
            self.hidden_word = ''.join(hidden_word_list)
            if '▯' in self.hidden_word:
                await ctx.send(f'{ctx.author.name} текущий прогресс: {self.hidden_word}')
            else:
                encoded_word = urllib.parse.quote(self.correct_word.lower())
                wiki_url = f"https://ru.wikipedia.org/w/index.php?search={encoded_word}"
                await ctx.send(f'{ctx.author.name} вы отгадали все буквы! Загаданное слово: {self.correct_word}. '
                               f'Почитать здесь -> {wiki_url}')
                self.correct_word = None
        elif word not in self.words:
            await ctx.send(f'{ctx.author.name} такого слова нет в моём словаре!')


    # Получить data (кол-во зрителей и время трансляции)
    async def get_viewer_count(self):
        nickname_ = "https://api.twitch.tv/helix/streams?user_login=" + self.nickname
        async with httpx.AsyncClient() as client:
            response = await client.get(nickname_, headers={
                'Client-ID': f'{self.client_id}',
                'Authorization': f'Bearer {self.token[6:]}'
            })
            data = response.json()
            if data['data']:
                viewer_count = data['data'][0]['viewer_count']
                started_at = data['data'][0]['started_at']
                stream_duration = self.calculate_stream_duration(started_at)
                return viewer_count, stream_duration
            return 0, 'Трансляция не ведется'

    def calculate_stream_duration(self, started_at):
        start_time = parse(started_at[:-1] if started_at.endswith('Z') else started_at)
        duration = datetime.utcnow() - start_time
        hours, remainder = divmod(duration.total_seconds(), 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"

    @commands.command(name='зрители')
    async def viewers_info(self, ctx: commands.Context):
        if ctx.author.is_mod:
            self.cur_viewer, stream_dur = await self.get_viewer_count()
            diff = self.cur_viewer - self.prew_viewers
            if diff == 0:
                await ctx.send(f'{self.cur_viewer} ({stream_dur} 🕝)!')
            elif diff > 0:
                await ctx.send(f'{self.cur_viewer} (+{diff}👤) ({stream_dur} 🕝)!')
            elif diff < 0:
                await ctx.send(f'{self.cur_viewer} ({diff}👤) ({stream_dur} 🕝)!')
            self.prew_viewers = self.cur_viewer

    async def viewer_timer(self):
        self.cur_viewer, stream_dur = await self.get_viewer_count()
        diff = self.cur_viewer - self.prew_viewers
        if diff == 0:
            await self.channel.send(f'{self.cur_viewer} ({stream_dur} 🕝)!')
        elif diff > 0:
            await self.channel.send(f'{self.cur_viewer} (+{diff}👤) ({stream_dur} 🕝)!')
        elif diff < 0:
            await self.channel.send(f'{self.cur_viewer} ({diff}👤) ({stream_dur} 🕝)!')
        self.prew_viewers = self.cur_viewer

    @commands.command(name='розыгрыш')
    async def raffle(self, ctx: commands.Context, command: str = 'начать', atr: str = '+'):
        if ctx.author.is_mod:
            if command == 'начать':
                self.raffle_key_word = '+'
                self.raffle_player_list = []
                self.raffle_key_word = atr if atr !='+' else '+'
                self.raffle_flag = True
                await ctx.send(f'Розыгрыш начался! Пиши {self.raffle_key_word}, чтобы участвовать!')
            elif command == 'отстранить' and self.raffle_flag:
                atr = atr.lower()
                if '@' in atr:
                    atr = atr.replace('@', '')
                if atr in self.raffle_player_list:
                    self.raffle_black_list.append(atr)
                    self.raffle_player_list = [player for player in self.raffle_player_list if player != atr]
                    await ctx.send(f'{atr} отстранён от розыгрыша!')
            elif command == 'добавить' and self.raffle_flag:
                atr = atr.lower()
                if '@' in atr:
                    atr = atr.replace('@', '')
                if atr in self.raffle_black_list:
                    self.raffle_black_list.remove(atr)
                if atr not in self.raffle_player_list:
                    self.raffle_player_list.append(atr)
                    await ctx.send(f'{atr} записан на розыгрыш!')
            elif command == 'очистить' and self.raffle_flag:
                if atr == '+':
                    self.raffle_player_list = []
                    await ctx.send('Список участников очищен!')
                elif atr == '-':
                    self.raffle_black_list = []
                    await ctx.send('Список отстранённый очищен!')
                else:
                    self.raffle_player_list = []
                    await ctx.send('Список участников очищен!')
            elif command == 'закончить' and self.raffle_flag:
                if len(self.raffle_player_list) == 0:
                    await ctx.send('В списке нет участников.')
                    if atr == '-':
                        await ctx.send('Розыгрыш завершён без определения победителя.')
                        self.raffle_flag = False
                        self.raffle_black_list = []
                if len(self.raffle_player_list) != 0:
                    self.raffle_flag = False
                    self.raffle_key_word = '+'
                    await ctx.send(f'{random.choice(self.raffle_player_list)} победил в розыгрыше!')
                if atr == 'очистить':
                    await ctx.send('Список участников очищен.')
                    self.raffle_player_list = []
                    self.raffle_black_list = []
            elif command == 'список' and self.raffle_flag:
                if atr == '+':
                    uniq_player_list = set(self.raffle_player_list)
                    await ctx.send(f'Список участников розыгрыша: {", ".join(uniq_player_list)}')
                elif atr == '-':
                    uniq_black_list = set(self.raffle_black_list)
                    await ctx.send(f'Список отстранённых от розыгрыша: {", ".join(uniq_black_list)}')
            elif not self.raffle_flag:
                await ctx.send('Розыгрыш не был начат.')

    @commands.command(name='фолоу', aliases=['фоллоу', 'followage'])
    async def followage(self, ctx: commands.Context):
        broadcaster = await self.fetch_users(names=[self.nickname])
        broadcaster_id = broadcaster[0].id
        follow_data = await self.http.get_channel_followers(broadcaster_id=broadcaster_id, user_id=ctx.author.id, token=self.token[6:])
        if not follow_data:
            await ctx.send(f'@{ctx.author.name} не подписан на канал.')
            return
        followed_at = follow_data[0]['followed_at']
        if isinstance(followed_at, str):
            followed_at = datetime.fromisoformat(followed_at.replace('Z', '+00:00'))
        now = datetime.now(timezone.utc)
        delta = now - followed_at
        years = delta.days // 365
        months = (delta.days % 365) // 30
        days = (delta.days % 365) % 30
        time_parts = [] # дата: год/месяц/день
        if years: time_parts.append(f"{years} {'год' if years == 1 else 'года' if 2 <= years <= 4 else 'лет'}")
        if months: time_parts.append(f"{months} {'месяцев' if months >= 5 or months == 0 else 'месяц' if months == 1 else 'месяца'}")
        if days: time_parts.append(f"{days} {'дней' if days >= 5 or days == 0 else 'день' if days == 1 else 'дня'}")
        if not time_parts:
            await ctx.send(f'@{ctx.author.name} подписан на канал менее дня!')
        else:
            await ctx.send(f'@{ctx.author.name} подписан на канал уже {" ".join(time_parts)}!')

    @commands.command(name='задача')
    async def task(self, ctx: commands.Context):
        x = random.randint(1, 100)
        y = random.randint(1, 100)
        arithmetic = {'+': lambda: x + y,
                      '-': lambda: x - y,
                      '*': lambda: x * y,
                      '/': lambda: round(x / y, 2)}
        operation = random.choice(list(arithmetic.keys()))
        self.answer = arithmetic[operation]()
        await ctx.send(f'Решите пример: {x} {operation} {y}')
        self.task_flag = True

    @commands.command(name='шутка')
    async def joke(self, ctx: commands.Context):
        joke = requests.get('https://official-joke-api.appspot.com/random_joke').json()
        setup = joke['setup']
        punchline = joke['punchline']
        final_joke = (f'{setup} {punchline}')

        translator = Translator()
        trans_final_joke = await translator.translate(final_joke, dest='ru')
        trans_text_joke = trans_final_joke.text
        await ctx.send(f"ВНИМАНИЕ! Анекдот: {trans_text_joke}")

    # Топ-5 чатеров по количеству сообщений
    @commands.command(name='рейтинг')
    async def rating(self, ctx: commands.Context):
        top = rating.get_top_users()
        await ctx.send(f'Топ чатеров по количеству сообщенйи: {", ".join([f"{1 + top.index(nick)}. {nick[0]}: "
                       f"{nick[1]['message_count']} ✉️" for nick in top])}.'
                       f' Ваше количество сообщений: {rating.get_msg(ctx.author.name)} 📫')

    # Функция для автомодерации
    def bunword_check(self, message):
        def normalize_repeats(word):
            if len(word) < 2:
                return word
            normalized = []
            prev_char = word[0]
            normalized.append(prev_char)
            for char in word[1:]:
                if char != prev_char:
                    normalized.append(char)
                    prev_char = char
            return ''.join(normalized)
        words = message.lower().split()

        for word in words:
            if len(word) > 20 or len(word) < 3:
                continue
            variants = []
            word = normalize_repeats(word)
            for char in word:
                if char in self.lit_dict:
                    variants.append([char] + self.lit_dict[char])
                else:
                    variants.append([char])
            all_combinations = {''.join(combination) for combination in itertools.product(*variants)}
            for ban_word in self.nword_list:
                if ban_word.endswith('*'):
                    base_word = ban_word[:-1]
                    if any(comb.startswith(base_word) for comb in all_combinations):
                        print("2")
                        return True
                else:
                    if ban_word in all_combinations:
                        print("2")
                        return True
        return False

    # Определения наличия ссылок в сообщении
    def links_check(self, message):
        url_pattern = r'''(?:https?://|ftp://)(?:[a-z0-9-]+\.)+[a-z]{2,4}(?:[/?#][^\s]*)?|
        \bwww\.(?:[a-z0-9-]+\.)+[a-z]{2,4}(?:[/?#][^\s]*)?|\b(?:[a-z0-9-]+\.){1,2}[a-z]{2,4}\b'''
        urls = re.findall(url_pattern, message, re.VERBOSE | re.IGNORECASE)

        for url in urls:
            lower_url = url.lower()
            if not any(allowed.lower() in lower_url for allowed in self.allow_links):
                return True
        return False

        # обработчик сообщений
    async def event_message(self, message: Message):
        if message.author is None:
            pass # Игнорирование бота и системных сообщений
        else:
            # Автомод
            print(message.content)
            rating.add_msg(message.author.name)
            try:
                if self.links_check(message.content):
                    if rating.get_timeout(message.author.name) >= 5:
                        await self.user.timeout_user(token=self.token[6:], moderator_id=self.bot_id, user_id=message.author.id,
                                                    duration=3600, reason='не используйте запрещённые ссылки')
                    else:
                        await self.user.timeout_user(token=self.token[6:], moderator_id=self.bot_id, user_id=message.author.id,
                                                     duration=5, reason='не используйте запрещённые ссылки')
                    rating.add_timeout(message.author.name)
                elif self.bunword_check(message.content):
                    if rating.get_timeout(message.author.name) >= 5:
                         await self.user.timeout_user(token=self.token[6:], moderator_id=self.bot_id, user_id=message.author.id,
                                                    duration=3600, reason='не используйте плохие слова в чате')
                    else:
                        await self.user.timeout_user(token=self.token[6:], moderator_id=self.bot_id, user_id=message.author.id,
                                                     duration=5, reason='не используйте плохие слова в чате')
                    rating.add_timeout(message.author.name)
                else:
                    pass
            except Exception as e:
                print(e)
            # Розыгрыши
            if (self.raffle_flag and message.author.name not in self.raffle_player_list
                    and message.content == self.raffle_key_word and message.author.name not in self.raffle_black_list):
                self.raffle_player_list.append(message.author.name)
                if message.author.is_subscriber:
                    self.raffle_player_list.append(message.author.name)
                await self.channel.send(f'{message.author.name} записан на розыгрыш!')
            # Задача
            if self.task_flag:
                msg = str(message.content)
                msg = msg.replace(',', '.')
                if msg == str(self.answer):
                    await self.channel.send(f'{message.author.name} дал правильный ответ: {msg}!')
                    self.task_flag = False
            # Зрители
            self.message_count += 1
            if self.message_count % 50 == 0:
                await self.viewer_timer()
            if message.author.name not in self.chatters:
                self.chatters.append(message.author.name)
            await self.handle_commands(message)

    async def event_command_error(self, error: Exception, data: str = None):
        if isinstance(error, CommandOnCooldown):
            pass
