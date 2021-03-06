#!/usr/bin/env python
"""A Discord bot for managing regular announcements."""

import sys
import os
import datetime
import discord
from discord.ext import tasks, commands
import yaml
import string

__author__ = "Matthew Broadbent"
__copyright__ = "Copyright 2021, Matthew Broadbent"
__credits__ = ["Matthew Broadbent"]
__license__ = "GPL"
__version__ = "0.1.0"
__maintainer__ = "Matthew Broadbent"
__email__ = "matt@matthewbroadbent.net"
__status__ = "Development"


class Announcements(commands.Cog):

	def __init__(self, bot, config_path):
		self.bot = bot
		self.config_path = config_path
		self.config = None
		self.init = False
		self.announce.start()

	def cog_unload(self):
		self.announce.cancel()

	@tasks.loop(hours=24)
	async def announce(self):
		"""Check for upcoming announcements."""
		if self.init:
			if self.load_config():
				for announcement in self.config['announcements']:
					today = datetime.datetime.today()
					if int(announcement[0]) != -1:
						d = (today - datetime.datetime.utcfromtimestamp(0)).days
						if d % int(announcement[0]) == 0:
							await self.send(announcement[2], announcement[3], announcement[4])
					elif int(announcement[1]) != -1:
						if today.weekday() == announcement[1]:
							await self.send(announcement[2], announcement[3], announcement[4])
		else:
			self.init = True

	async def send(self, channel_name, message, link):
		"""Send contents of announcement (and link) to given channel"""
		await bot.wait_until_ready()
		channel_id = self.config['channels'].get(channel_name)
		channel = self.bot.get_channel(channel_id)
		await channel.send(message)
		try:
			await channel.send(link)
		except discord.errors.HTTPException:
			pass

	async def load_config(self):
		"""Load YAML file containing announcements and channels."""
		with open(self.config_path, "r") as ymlfile:
			self.config = yaml.safe_load(ymlfile)
			return True
		return False


class Language(commands.Cog):

	def __init__(self, bot, swears):
		self.bot = bot
		self.swears = swears

	@commands.Cog.listener()
	async def on_message(self, message):
		"""Check each message for a swear word."""
		for word in message.content.split(' '):
			word = word.lower()
			word = word.translate(str.maketrans('', '', string.punctuation))
			if word in swears:
				await message.channel.send('https://tenor.com/view/captain-america-marvel-avengers-gif-14328153')
				break


def load_swears(filename):
	"""Load text file containing swear words."""
	swears_file = open(filename, "r")
	content = swears_file.read()
	swears = content.split("\n")
	swears_file.close()
	return swears





if __name__ == '__main__':
	TOKEN = os.getenv('DISCORD_TOKEN')
	bot = commands.Bot(
		command_prefix='^',
		description='A Discord bot for managing regular announcements.',
	)
	bot.add_cog(Announcements(bot, sys.argv[1]))
	swears = load_swears(sys.argv[2])
	bot.add_cog(Language(bot, swears))
	bot.run(TOKEN)
