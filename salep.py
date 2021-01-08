import doviz_api
import discord
from discord.ext import commands
import logging
import re

API_KEY = ""

salep = commands.Bot(command_prefix="s!")


@salep.event
async def on_ready():
    logging.info('Logged in as')
    logging.info(salep.user.name)
    logging.info(salep.user.id)
    logging.info('------')

@salep.command()
async def döviz(ctx, currency: str):

    try:
        exchange_rate, currency_abbr = doviz_api.get_exchange_rate(currency, API_KEY)
    except doviz_api.InvalidCurrencyError:
        await ctx.send(f"{currency} diye bir kur yok!")
        return
    
    await ctx.send(f"1 {currency_abbr} = {exchange_rate} {doviz_api.base_currency}")

@salep.listen("on_message")
async def schtupid(message):
    if message.author.id == salep.user.id:
        return

    if re.search("(z|Z)oom", message.clean_content):
        await message.channel.send("Zoom is schtupid!!!1")

if __name__ == "__main__":
    token_file = open("TOKEN", "r")

    logging.basicConfig(filename="salep.log", level=logging.INFO,
                        format="%(asctime)s %(levelname)-8s %(message)s",
                        datefmt="%Y-%m-%d %H:%M:%S")

    token = token_file.readline().strip()
    API_KEY = token_file.readline().strip()
    token_file.close()

    salep.run(token)


