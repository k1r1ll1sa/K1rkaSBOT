"""Модуль с функционалом бота"""
import random
from asyncio import timeout

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
        loop.run_until_complete(bot.run())
    except Exception as e:
        print(e)


class Bot(commands.Bot):
    def __init__(self, nickname, token, client_secret, client_id, root):
        self.nickname = nickname
        self.nickname_ = "#" + nickname
        self.token = token
        self.client_secret = client_secret
        self.client_id = client_id
        self.root = root

        self.http = TwitchHTTP(client_id=self.client_id, client=self, client_secret=self.client_secret)
        self.user = None # PartialUser
        self.bot_id = None

        # Рулетка
        self.lose_count = 6
        self.random_count = None
        self.roulette_is_run = False

        super().__init__(
            prefix='!',
            token=self.token,
            client_secret=self.client_secret,
            client_id=client_id,
            initial_channels=[self.nickname_])

    async def event_ready(self):
        channel = self.get_channel(self.nickname)
        owner = await self.fetch_users(names=[self.nickname])
        owner_id = owner[0].id # для инициализации self.user, далее не нужен
        bot = await self.fetch_users(names=['k1rkasbot1k'])
        self.bot_id = bot[0].id
        self.user = PartialUser(self.http, owner_id, self.nickname)
        print(self.bot_id)
        await channel.send(f'{self.nick} запущен!')
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
        self.root.console_add_line(f'{ctx.author.name} uses the command "!рулетка"')
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
        self.root.console_add_line(f'{ctx.author.name} uses the command "!кубик"')
        random_cube = random.randint(1, number)
        if random_cube == number:
            await ctx.send(f'{ctx.author.name} критический успех! {number} 🎲')
        elif random_cube == 1:
            await ctx.send(f'{ctx.author.name} критический провал! 1 🎲')
        else:
            await ctx.send(f'{ctx.author.name} выпало число {random_cube} 🎲')

    @commands.command(name='копать')
    async def mine(self, ctx: commands.Context):
        with open('info.json', 'r', encoding='utf-8') as f:
            info = json.load(f)
        phrase = random.choice(info['mine'])
        await ctx.send(f'{ctx.author.name} {phrase}!')