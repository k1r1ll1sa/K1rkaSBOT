"""Модуль с функционалом бота"""
import random

from twitchio.ext import commands
from twitchio.models import PartialUser
from twitchio.http import TwitchHTTP
import asyncio
import datetime


def init_bot(nickname, token, root):
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        bot = Bot(nickname, token, root)
        loop.run_until_complete(bot.run())
    except Exception as e:
        print(e)


class Bot(commands.Bot):
    def __init__(self, nickname, access_token, root):
        self.nickname = nickname
        self.nickname_ = "#" + nickname
        self.root = root

        # рулетка
        self.is_run = False
        self.lose_count = 1
        self.patron_count = 1

        super().__init__(
            prefix='!',
            token='oauth:vs83g4g488bynbav14ut4trjbka22c',
            client_secret='ec0r4iibqershw03cgo35iginpq6q9',
            initial_channels=[self.nickname_])

    async def event_ready(self):
        channel = self.get_channel(self.nickname)
        await channel.send(f'{self.nick} запущен!')
        self.root.console_add_line(f'{self.nick} is launched on the channel {self.nickname}')

    @commands.command(name='привет')
    async def hello_command(self, ctx: commands.Context):
        await ctx.send(f'Привет, {ctx.author.name}! 👋')
        self.root.console_add_line(f'{ctx.author.name} used the command "!привет"')

    @commands.command(name='время')
    async def time(self, ctx: commands.Context):
        await ctx.send(f"{ctx.author.name} моё время: {datetime.datetime.now().strftime('%H:%M')} 🕑")
        self.root.console_add_line(f'{ctx.author.name} used the command "!время"')

    @commands.command(name='копать')
    async def mine(self, ctx: commands.Context):
        with open("mine.txt", "r", encoding='utf-8') as file:
            phrase = file.readlines()
            random_phrase = phrase[random.randint(0, len(phrase) - 1)]
        await ctx.send(f"{ctx.author.name} {random_phrase}")
        self.root.console_add_line(f'{ctx.author.name} used the command "!копать"')

    @commands.command(name='кубик')
    async def cube(self, ctx: commands.Context, limit=100):
        limit = int(limit)
        number = random.randint(1, int(limit))
        if number == limit:
            await ctx.send(f"{ctx.author.name} критический успех! {limit} 🎲")
        elif number == 1:
            await ctx.send(f'{ctx.author.name} критический промах! 1 🎲')
        else:
            await ctx.send(f'{ctx.author.name} выпало число {number} 🎲!')

    @commands.command(name='рулетка')
    async def roullete(self, ctx: commands.Context, count=1):
        self.root.console_add_line(f'{ctx.author.name} used the command "!рулетка"')
        if not self.is_run:
            self.is_run = True
            await ctx.send(f'{ctx.author.name} перезаряжает револьвер...')
            self.patron_count = random.randint(1, 6)
            self.lose_count = int(count)
        if self.lose_count <= self.patron_count:
            self.lose_count += 1
            await ctx.send(f'{ctx.author.name} выживает!')
        else:
            await ctx.send(f'{ctx.author.name} проиграл в рулетку! 💀')
            # реализовать замут
            self.lose_count = 1
            self.is_run = False
