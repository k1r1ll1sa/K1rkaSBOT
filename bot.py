"""Модуль с функционалом бота"""
import random

import httpx
import requests
import urllib.parse
from twitchio import Message
from twitchio.ext import commands
from twitchio.models import PartialUser
from twitchio.http import TwitchHTTP
import asyncio
import datetime
import json

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

    @commands.command(name='привет')
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
    async def roulette(self, ctx: commands.Context, count=1):
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
    async def mine(self, ctx: commands.Context):
        self.root.console_add_line(f'{ctx.author.name} uses the command "!копать"')
        with open('info.json', 'r', encoding='utf-8') as f:
            info = json.load(f)
        phrase = random.choice(info['mine'])
        await ctx.send(f'{ctx.author.name} {phrase}!')

    @commands.command(name='чай')
    async def tea(self, ctx: commands.Context, user=None):
        self.root.console_add_line(f'{ctx.author.name} uses the command "!чай" with arguments {user}')\
            if user else self.root.console_add_line(f'{ctx.author.name} uses the command "!чай"')
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

    @commands.command(name='зелёный', aliases=['зеленый', 'green']) # с альтернативными враиантами
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
                await ctx.send(f'{ctx.author.name} вы отгадали все буквы! Загаданое слово: {self.correct_word}. '
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
        start_time = datetime.fromisoformat(started_at[:-1])
        duration = datetime.utcnow() - start_time
        return str(duration).split('.')[0]

    @commands.command(name='зрители')
    async def viewers_info(self, ctx: commands.Context):
        if ctx.author.is_mod:
            self.cur_viewer, stream_dur = await self.get_viewer_count()
            diff = self.cur_viewer - self.prew_viewers
            if diff == 0:
                await ctx.send(f'{self.cur_viewer} ({stream_dur})!')
            elif diff > 0:
                await ctx.send(f'{self.cur_viewer} + {diff} ({stream_dur})!')
            elif diff < 0:
                await ctx.send(f'{self.cur_viewer} - {diff} ({stream_dur})!')
            self.prew_viewers = self.cur_viewer

    async def viewer_timer(self):
        self.cur_viewer, stream_dur = await self.get_viewer_count()
        diff = self.cur_viewer - self.prew_viewers
        if diff == 0:
            await self.channel.send(f'{self.cur_viewer} ({stream_dur})!')
        elif diff > 0:
            await self.channel.send(f'{self.cur_viewer} + {diff} ({stream_dur})!')
        elif diff < 0:
            await self.channel.send(f'{self.cur_viewer} - {diff} ({stream_dur})!')
        self.prew_viewers = self.cur_viewer


    # обработчик сообщений & будущая автомодерация
    async def event_message(self, message: Message):
        if message.author is None:
            pass # Игнорирование бота и системных сообщений
        else:
            self.message_count += 1
            if self.message_count % 20 == 0:
                await self.viewer_timer()
            print(message.author.name, message.content)
            if message.author.name not in self.chatters:
                self.chatters.append(message.author.name)
            await self.handle_commands(message)