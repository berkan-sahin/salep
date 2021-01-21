import doviz_api
import discord
from discord.ext import commands
from pymongo import MongoClient  
from typing import Union
import logging
from random import choice

API_KEY = ""

salep = commands.Bot(command_prefix="s!")

client = MongoClient()
db = client.salep

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

def extract_id(name: Union[discord.Member, str]):
    return name if type(name) == str else name.id

@salep.command()
async def add_quote(ctx, name: Union[discord.Member, str], quote: str):
    if db.people.find_one({"name": extract_id(name), "guild": ctx.guild.id}) is None:
        person = {
            "name": extract_id(name),
            "guild": ctx.guild.id,
            "quotes": [quote]
        }

        db.people.insert_one(person)
        await ctx.send("Created stack for {0} and added quote".format(name if type(name) == str else name.mention))
        return

    db.people.update_one({"name": extract_id(name), "guild": ctx.guild.id}, {"$addToSet": {"quotes": quote}})
    await ctx.send("Added quote to stack")

@salep.command()
async def quote(ctx, name: Union[discord.Member, str]):
    person = db.people.find_one({"name": extract_id(name), "guild": ctx.guild.id})
    if person is None:
        await ctx.send("This person does not exist")
        return

    await ctx.send(choice(person["quotes"]))


if __name__ == "__main__":
    logging.basicConfig(filename="salep.log", level=logging.INFO,
                        format="%(asctime)s %(levelname)-8s %(message)s",
                        datefmt="%Y-%m-%d %H:%M:%S")

    with open("TOKEN", "r") as f:
        token = f.readline().strip()
        API_KEY = f.readline().strip()


    salep.run(token)


