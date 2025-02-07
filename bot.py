"""Модуль с функционалом бота"""
import datetime
import sys

from PyQt5.QtWidgets import QApplication
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
    def __init__(self, nickname, token, root):
        self.nickname = nickname
        self.nickname_ = "#" + nickname
        self.root = root
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
        self.root.console_add_line(f'{ctx.author.name} uses the command "!привет"')

    @commands.command(name='время')
    async def time(self, ctx: commands.Context):
        await ctx.send(f"{ctx.author.name} моё время: {datetime.datetime.now().strftime('%H:%M')}")
        self.root.console_add_line(f'{ctx.author.name} uses the command "!время"')
